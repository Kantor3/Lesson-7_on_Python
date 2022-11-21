"""
Модуль обеспечения работы с базой данных "Телефонный справочник".
База данных организована в виде списка записей контактов.
Каждая запись представляет собой именованную запись в формате словаря
"""
import random
import math
import td_view as vw

# Начальные значения глобальных переменных до их инициализации
contacts, structure, id_name, id_type = [{}], (), '', None
export_file, formats_file = '', ''
cnt_default = 10                        # число строк (по умолчанию)
all_db = '*'                           # Признак отбора - его отсутствие (вся база данных)


# коллекция данных для случайного заполнения базы данных
def rand_collections(count, fio=True, phone=True):
    fio_s = ('Макар Терентьев',
             'Марк Михайлов',
             'Роберт Коршунов',
             'Александр Козлов',
             'Даниил Большаков',
             'Марк Овсянников',
             'Алиса Ефремова',
             'Дмитрий Моисеев',
             'Ангелина Григорьева',
             'Амина Овсянникова',
             'Артемий Моисеев',
             'Дмитрий Харитонов') if fio else None
    phones = ('7 (524) 194-18-00',
              '7 (708) 686-29-34',
              '7 (202) 116-97-64',
              '7 (714) 131-15-82',
              '7 (657) 105-13-15',
              '7 (020) 869-15-42',
              '7 (020) 812-17-82',
              '7 (284) 274-50-78',
              '7 (292) 533-95-29',
              '7 (967) 175-80-06',
              '7 (314) 199-44-63',
              '7 (162) 328-49-64') if phone else None
    count = cnt_default if isinstance(count, bool) else count
    collections = set()
    len_source = len(fio_s)
    while len(collections) != count:
        number = random.randint(0, len_source-1)
        collections.add((fio_s[number], phones[number]))

    return collections


# Получить текущий размер справочника
def get_size():
    return len(contacts)


# Получить глобальные данные модели
def get_params_model():
    params = (structure, id_name, id_type, contacts, all_db, export_file, formats_file)
    return params


# Получение среза справочника
def get_slice(db, rang):
    frm, to = (rang + (None,))[:2] if rang else (all_db, None)
    if frm == all_db: return db
    frm = 0 if frm is None else frm
    to = len(db) if to is None else to
    return db[frm: to]


# Наложение фильтра по полям базы данных
# реализован самый простой вариант - все полученные данные по полям соединяются логикой "И":
# Вариант-1 Фильтр => кортеж значений всех полей, последовательность - строгая.
#                     Не учитываемые поля, значения которых в кортеже == None.
# Вариант-2 Фильтр => в виде запроса, представляющего словарь с полями, по которым требуется выполнить (поиск/отбор)
# Если это поиск соответствия для переданной записи - то возврат True/False, иначе индекс найденной записи из БД или 0
# request - что ищем (запрос, фильтр), варианты см. выше
# records - гдк ищем (если не указано, то по всему телефонному справочнику)
def where(request, records=None):

    def isin_records(recs, rqst):
        if isinstance(rqst, dict):
            res = math.prod([str(v) in str(recs[k]) for k, v in tuple(rqst.items())])
        else:
            res = math.prod([f is None or str(f) in str(v) for v, f in zip(tuple(recs.values()), rqst)])
        return res

    request = {id_name: request} if isinstance(request, int) else request   # поддержка варианта поиска по id
    records = contacts if records is None else records

    if isinstance(records, dict):                       # если проверяем в одной (переданной) записи
        return isin_records(records, request)
    else:                                               # если это список записей, возвращаем номер найденной записи
        for ind, rec in enumerate(records):
            if isin_records(rec, request):
                return ind + 1
        else:
            return 0


# Формирование и передача уникального ключа.
# Для упрощения: 1) ключ. id - числовой; 2) новый ключ назначается как следующий от максимального имеющегося в БД
def get_uniqid():
    id_new = max(map(lambda rec: rec[id_name], contacts)) + 1
    return id_new


# Инициализация базы данных "Контакты" (телефонный справочник)
def init(default=None):
    global structure
    global id_name
    global id_type
    global contacts
    global export_file
    global formats_file

    structure = ('id', 'fio', 'phone')                    # по умолчанию 1-й элемент - внутренний ключ (id)
    id_name = structure[0]
    id_type = int                                         # преобразование к типу: result = [*map(id_type, [id_])][0]
    export_file = 'ex_contacts'
    formats_file = ('csv', 'json', 'txt')

    if not (default is None):
        collections = rand_collections(default)
        records = tuple([(i+1,) + el for i, el in enumerate(collections)])
        contacts = [dict([(structure[i], ell) for i, ell in enumerate(el) ]) for el in records]
        # print('База инициирована начальными данными:')
        vw.output_contacts(contacts)    # покажем начальное состояние базы (первые несколько строк), если она не пустая


# Получение данных о контактах в соответствии с полученным отбором
#  (открытие канала для последовательного получения данных о контактах) - get_contacts (chn_contacts)
def get_contacts(*rang, d_filter=None, one=None):
    contacts_slice = get_slice(contacts, rang)
    sql_list = contacts_slice if d_filter is None else \
               list(filter(lambda rec: where(d_filter, records=rec), contacts_slice))
    result = sql_list[0] if one and sql_list else sql_list
    return result


# Добавление в базу новых записей.
# с автоматическим присвоением уникального id
# и, если задано, с проверкой на уникальность записи по всем полям
# Записи передаются в формате списка. Каждая запись - словарь со значениями полей
# Переданные для добавления записи могут иметь произвольный набор полей, кроме ID
def adding_contacts(contacts_add, uniq=True):

    if not contacts_add: return None
    global contacts
    add_records = []

    if not isinstance(contacts_add[0], dict):
        contacts_add = [dict([(k, v) for k, v in zip(structure[1:], contact)]) for contact in contacts_add]

    for record in contacts_add:                                     # для каждой записи переданного пакета
        # если запись уже с id - "отрезаем" ее
        record_short = record if len(record) < len(structure) else dict([el for el in tuple(record.items())[1:]])

        if uniq and where(record_short): continue                  # добавляемая запись не может совпадать с к-л в БД

        key_record = record.keys()
        record_new = {id_name: get_uniqid()}                        # первое поле - ключ записи (id)
        add_records.append(record_new)
        for k in structure[1:]:
            record_new[k] = record[k] if k in key_record else None  # Присваиваем None при отсутствии нужного поля
        contacts.append(record_new)

    return add_records


# Запись модифицированных данных полученной записи контакта
# Модифицированные данные (values_ch) передаются в виде кортежей
# значений в строгом порядке следования полей в базе данных.
# Направление доработки: Для загружаемых данных формата csv и json
# добавить возможность обновления данных по наименованию полей
def update_contact(contact, values_ch):
    values_ch = tuple(values_ch.values()) if isinstance(values_ch, dict) else values_ch
    id_val = contact[id_name]
    request_id = {id_name: id_val}
    ind_contact = where(request_id)
    if ind_contact:
        vals_ch_plus = (id_val, *values_ch)
        contact_ch = dict([(k, v) for k, v in zip(structure, vals_ch_plus)])
        contacts[ind_contact - 1] = contact_ch
        return contact_ch
    return None


# Удаление контакта
def del_contact(contacts_del):
    l_deleted = []
    for contact in contacts_del:
        ind_contact = where(contact)
        if ind_contact:
            contacts.pop(ind_contact - 1)
            l_deleted.append(contact[id_name])
    return l_deleted


# запись загруженных данных в базу в режиме (замещения c одинаковым id и/или добавление новых)
# method - метод загрузки:
#          "-n" - только новые контакты
#          "-u" - только обновление изменений, имеющихся в базе, контактов
#          "-f" - как можно полное обновление
def upload_contacts(contacts_upload, method=None):

    method = "-f" if method is None else method
    contacts_add, contacts_upd, added, updated = [], [], [], []
    for el in contacts_upload:
        if where(el[id_name]):
            contacts_upd.append(el)
        else:
            contacts_add.append(el)

    print(f'contacts_upd = {contacts_upd}')

    if method in ('-n', '-f'):  added = adding_contacts(contacts_add)
    if method in ('-u', '-f'):  updated = [update_contact(rec, dict(tuple(rec.items())[1:])) for rec in contacts_upd]

    return added, updated
