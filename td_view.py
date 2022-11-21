"""
3. td_view:
=============
View - Передача-получение данных в файл, с выводом на консоль (интерфейс)

Методы:
--------------
operation_menu  - общее меню операция ('-F', '-E', '-R', '-H', '-Q')
                  (Файл: export, import; Редактирование: добавление, удаление, изменение; Отчет; Помощь; Выход)
menu_editing    - подменю выбора операций редактирования
menu_file       - подменю выбора операций файлового обмена (загрузка / выгрузка справочника)
menu_view       - подменю выбора операций вывода данных контактов из справочника
output_instr    - вывод инструкции
output_contacts - вывод данных о контактах
input_request   - запрос данных о контакте (запрос по ID, по ФИО, Имени, по интервалу от ... до) для целей:
                    - вывода данных о найденных контактах (по поисковому запросу или отбору)
                    - установки фокуса (установка текущего контакта) с последующим удалением или редактированием
input_contacts  - ввод данных контакта -ов ('Добавление новых контактов:')
editing_contact - редактирование выбранного контакта
select_format   - выбор формата файла для экспорта (CSV, txt или JSON)
import_method   - выбор способа импорта (загрузки) данных в справочник (только измененные, добавление только новых)
output_message  - вывод сообщений о результатах выполнения операций, в т.ч. инструкций, подсказок и пр.
"""
import os.path as osp
import types
import td_directory as dr
import my_lib as myl

purpose = dict([('-a', 'добавления'),
                ('-e', 'редактирования'),
                ('-d', 'удаления'),
                ('-r', 'отбора или поиска'),
                ('-s', 'выгрузки'),
                ('-l', 'загрузки'),
                ('-h', 'получения подсказки'),
                ('-q', 'выхода')
                ])


# Вывод меню
def output_menu():
    print()
    print('Меню:---------------------------------------------------------------------------')
    print('Файл           | Редактирование    | Отчет ("-r") | Помощь ("-h") | Выход ("-q")')
    print('export ("-s")  | новый ("-a")      |')
    print('import ("-l")  | изменение ("-e")  |')
    print('               | удаление ("-d")   |')


# Печать титула при выводе записей базы данных на консоль
def output_title(db, txt='База данных'):
    if not db:
        structure_db = dr.get_params_model()[0]
        db = [ dict([(k, None) for k in structure_db]) ]
    l_keys = tuple(db[0].keys())
    l_max_val = myl.get_maxlen_fields(db)
    outline = '-' * (sum(l_max_val) + 2)
    print('\n', txt)
    print(outline)
    print(*[e.ljust(l) for e, l in zip(l_keys, l_max_val)])
    print(outline)
    return l_max_val


# Главное меню
#  общее меню операция ('-F', '-E', '-R', '-H', '-Q'):
#  Файл: export, import; Редактирование: новый, удаление, изменение; Отчет; Помощь; Выход
def operation_menu(start_process=None):
    if start_process: output_menu()
    menu = myl.sep_option('aderslhq')
    print()
    operation = myl.get_input(menu, type_input=tuple, txt='Выберите операцию.', end='-q')
    return operation


# Запрос данных о контакте (запрос по ID, по ФИО, Имени, по интервалу от ... до) для целей:
#   - вывода данных о найденных контактах (по поисковому запросу или отбору)
#   - установки фокуса (установка текущего контакта) с последующим удалением или редактированием
def input_request(operation, structure_db, all_db=None):
    txt_for = purpose[operation]
    if operation in ('-r', '-l'):            # запрос данных для отбора (поиска) данных справочника
        print()
        print(f'Для {txt_for} последовательно определите границы (номера записи [от] и [до]),\n'
              f'а также значения полей справочника {structure_db}. Для пропуска определений нажимайте [Enter]:')
        td_size = dr.get_size()
        frm = myl.get_input(1, td_size, default=1, txt='[от]:', not_mess=True)
        default = frm if frm-1 else td_size
        to = myl.get_input(frm, td_size, default=default, txt='[до]:', not_mess=True)

        req_struct = tuple([(None, None, f'Укажите значение "{el}" для поиска или отбора') for el in structure_db])
        flt = myl.get_inputs(*req_struct, type_input=str, not_mess=True, all_input=True)

        print(f'\nСформирован запрос. Границы (от...до) = {(frm, to)}; Фильтр: {structure_db} -> {flt}')

        frm -= 1
        req = (frm, to, *flt)
        if myl.empty_coll(flt) and frm == 0 and to == td_size:
            request = all_db                                        # вся база данных
        else:
            request = req[:2] + (dict(filter(lambda el: not el[1] is None,
                                             map(lambda kv: kv, zip(structure_db, req[2:])))),)
        return request

    if operation in ('-e', '-d'):                   # Выбор контакта по id для редактирования или удаления
        req = myl.get_input(txt=f'Введите {structure_db} контакта для {txt_for}', not_mess=True)
        return req


# Ввод данных контакта для добавления в справочник
def input_contacts(operation, structure_db):
    txt_for = purpose[operation]
    contacts_add = []
    print()
    while True:
        print(f'Для {txt_for} контакта заполните значения полей {structure_db}:')
        for_input = tuple([el for el in structure_db[1:]])
        contact = myl.get_inputs(*for_input, type_input=str, not_mess=True, all_input=True)

        if myl.empty_coll(contact):
            print('Введена пустая запись')
        else:
            contacts_add.append(contact)
        if myl.check_exit(sign='+', txt_req='"+" - добавить еще контакт, любая другая клавиша - завершить ввод -> ',  not_mess=True):
            break

    return contacts_add


# Редактирование выбранного контакта
def editing_contact(contact, structure_db):
    print()
    print(f'Редактирование данных контакта: {contact}')
    while True:
        for_input = tuple([el for el in structure_db[1:]])
        contact = myl.get_inputs(*for_input, type_input=str, not_mess=True, all_input=True)
        if myl.empty_coll(contact):
            print('Введена пустая запись')
            if myl.check_exit(txt_req='Повторить редактирование? ("Y" - ДА) -> ', not_mess=True):
                contact = None
                break
        else:
            break
    return contact


# Выбор формата файла для экспорта (CSV, txt или JSON)
def select_format(formats):
    print()
    format_sel = myl.get_input(formats, type_input=tuple, txt='Введите формат выгрузки данных', end='-q')
    return format_sel


# Задание параметров загрузки (импорта)
# Задание имени файла загрузки
# Выбор способа импорта (загрузки) данных в справочник (только измененные, добавление только новых, все)
# method - метод загрузки:
#          "-n" - только новые контакты
#          "-u" - только обновление изменений, имеющихся в базе, контактов
#          "-f" - как можно полное обновление
def set_load_param():
    print()
    while True:
        filename = myl.get_input(type_input=str, txt='Введите имя файла загрузки (вместе с расширением)')
        if filename is None: return None, None
        if not osp.isfile(filename):
            print(f'Указанный файл {filename} не найден. Уточните имя.')
            continue
        break

    print('Поддерживаются сл. методы загрузки:\n'
          '     "-n" - только новые контакты\n'
          '     "-u" - только обновление изменений, имеющихся в базе, контактов\n'
          '     "-f" - обновить, что можно, по максимуму')
    methods = myl.sep_option('nuf')
    method = myl.get_input(methods, default='u', type_input=tuple, txt='Введите способ загрузки данных', end='-')

    return filename, method


# Вывод данных о контактах
def output_contacts(contacts_gen):
    contacts_h = [el for el in contacts_gen] if isinstance(contacts_gen, types.GeneratorType) else contacts_gen
    l_max_val = output_title(contacts_h)
    contacts_prn = [tuple([str(e).ljust(l) for e, l in zip(tuple(rec.values()), l_max_val)]) for rec in contacts_h]
    for contact in contacts_prn:
        print(*contact)                 # Печать содержимого записи (контакта)


# Вывод сообщений (уведомлений) о результатах выполнения операций, в т.ч. инструкций, подсказок и пр.
def output_not(title_not, content_not=None):
    pointer = '---->'
    print()
    print(f'{pointer} {title_not}!')
    if content_not:
        for line in content_not:
            print(f'{" "*len(pointer)}{line}')
