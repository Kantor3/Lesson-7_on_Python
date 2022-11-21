"""
4. td_controller:
==================
Controller - обмен данными между Model и View, а также их (данных) пред- или пост- обработка

Методы:
---------------
manager         - Основное тело (локальный main)
export_contacts - экспорта полученных данных (запись в файл, указанного формата)
import_contacts - импорт данных (загрузка данных из файла указанного формата)
"""
import csv
import json
import td_directory as dr
import td_view as vw
import my_lib as myl

dr.init()                                                       # инициализация модели данных
structure_db, id_name, id_type, _, all_db, \
              export_file, formats_file = dr.get_params_model()  # получить параметры модели


# Выгрузка данных из справочника (запись в файл, указанного формата)
def export_contacts(contacts_gen, format_file, file_name=None):
    frm_csv, frm_json, frm_txt = formats_file
    file_name = export_file if file_name is None else file_name
    full_name = f'{file_name}.{format_file}' if format_file not in file_name else file_name
    contacts = [contact for contact in contacts_gen]

    with open(full_name, mode="w", encoding='cp1251') as ex_file:  # encoding='utf-8'

        if format_file == frm_csv:
            names = list(structure_db)
            file_wr = csv.DictWriter(ex_file, delimiter=",", lineterminator="\r", fieldnames=names)
            file_wr.writeheader()
            file_wr.writerows(contacts)

        if format_file == frm_json:
            json.dump(contacts, ex_file)

        if format_file == frm_txt:
            print(*contacts, file=ex_file, sep='\n')

        return full_name


# Загрузка данных в справочник из файла указанного формата
def import_contacts(file_name):
    frm_csv, frm_json, frm_txt = formats_file
    format_file = file_name.split('.')[-1]
    contacts_im = []

    with open(file_name, mode="r", encoding='cp1251') as im_file:  # encoding='utf-8'

        if format_file == frm_csv:
            file_rd = csv.DictReader(im_file, delimiter=",")
            for row in file_rd:
                id_str = row[id_name]
                row[id_name] = [*map(id_type, [id_str])][0]
                contacts_im.append(row)

        if format_file == frm_json:
            contacts_im = json.load(im_file)

        if format_file == frm_txt:
            lines = im_file.readlines()
            for line in lines:
                contact = eval(line[:-1])
                contacts_im.append(contact)

        return contacts_im


"""
Управляющие процедуры отработки операций с базой данных (телефонный справочник)
Возможный рефакторинг - вынесение их тоже в отдельный модуль. 
"""


# 1. Вывод данных о контакте в виде отчета, в т.ч. поиск/отбор по имени и по другим полям
def db_report(operation):
    request = vw.input_request(operation, structure_db, all_db=all_db)
    if isinstance(request, tuple):
        frm, to, flt = request
    else:
        frm, to, flt = request, None, None
    contacts_gen = dr.get_contacts(frm, to, d_filter=flt)
    vw.output_contacts(contacts_gen)


# 2. Добавление контакта
def db_added(operation):
    contacts_add = vw.input_contacts(operation, structure_db)
    if contacts_add:
        l_added = dr.adding_contacts(contacts_add)
        vw.output_not(f'В телефонный справочник добавлены {len(l_added)} записей',
                      content_not=contacts_add)
    else:
        vw.output_not(f'Введенные данные пустые ({contacts_add}). Выберите нужную операцию')


# 3. Редактирование данных контакта
def db_editing(operation):
    select = vw.input_request(operation, id_name)
    if not select:
        vw.output_not(f'Операция по редактированию контакта отменена')
        return None

    contact_edit = dr.get_contacts(d_filter={id_name: select}, one=True)
    contact_ch = None
    if contact_edit:
        values_change = vw.editing_contact(contact_edit, structure_db)  # запись контакта вместе с ключом
        if not values_change:
            vw.output_not(f'Редактирование контакта ({id_name} = {select}) отменено')
            return None
        contact_ch = dr.update_contact(contact_edit, values_change)

    if contact_ch is None:
        vw.output_not(f'Контакт с таким ({id_name} = {select}) в телефонном справочнике не найден')
    else:
        vw.output_not(f'Данные контакта ({id_name} = {select}) изменены.',
                      content_not=(f'Новые данные: {contact_ch}',))
    return None


# 4. Удаление контакта
def db_deleted(operation):
    select = vw.input_request(operation, id_name)
    if not select:
        vw.output_not(f'Операция по удалению контакта отменена')
        return None

    contact_del = dr.get_contacts(d_filter={id_name: select})  # только id контакта
    if contact_del:
        deleted = dr.del_contact(contact_del)
        vw.output_not(f'Из справочника удален контакт c {id_name} = {deleted}')
    else:
        vw.output_not(f'Контакт с {id_name} = {select} в телефонном справочнике не найден')
    return None


# 5. Экспорт справочника (выгрузка)
def db_export(operation):
    request = vw.input_request(operation, structure_db, all_db=all_db)
    if isinstance(request, tuple):
        frm, to, flt = request
    else:
        frm, to, flt = request, None, None
    contacts_gen = dr.get_contacts(frm, to, d_filter=flt)
    format_file = vw.select_format(formats_file)
    if not (format_file is None):
        res = export_contacts(contacts_gen, format_file)
        vw.output_not(f'Выгрузка в файл "{res}" выполнена успешно')


# 6. Импорт справочника (загрузка)
def db_import():
    file_name, method = vw.set_load_param()
    if not (file_name is None) and not (method is None):
        contacts_upload = import_contacts(file_name)
        added, updated = dr.upload_contacts(contacts_upload, method=method)
        content_not = (('Добавлено записей:', *added) if added else ()) + \
                      (('Обновлено записей:', *updated) if updated else ()) + \
                      (('Новых данных для загрузки из указанного файла НЕТ!',)
                       if not (added or updated) else ())
        vw.output_not(f'Загрузка из файла "{file_name}" выполнена успешно', content_not=content_not)


# Главная процедура
# -------------------------------------------------------------------------------
def manager(non_zero=None):
    if non_zero: dr.init(default=non_zero)
    vw.output_menu()  # Вывод меню

    while True:
        operation = vw.operation_menu()  # Запрос операции над телефонным справочником

        if operation is None and myl.check_exit(operation):  # Выход
            break

        elif operation == '-h':  # Вывод меню на экран
            vw.output_menu()

        elif operation == '-r':  # Вывод данных о контакте, в т.ч. поиск по имени
            db_report(operation)

        elif operation == '-a':  # Добавление контакта
            db_added(operation)

        elif operation == '-e':  # Редактирование данных контакта
            db_editing(operation)

        elif operation == '-d':  # Удаление контакта
            db_deleted(operation)

        elif operation == '-s':  # Экспорт справочника (выгрузка)
            db_export(operation)

        elif operation == '-l':  # Импорт справочника (загрузка)
            db_import()
