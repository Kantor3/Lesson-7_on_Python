"""
Отдельные полезные функции, составляющие мою библиотеку
"""


# Организация выхода:
# Варианты:
# 1. sign = None
# 2. sign = True
# 1. sign = '[symbol_EXIT]' - передан символ для запроса выхода, например, "Y"
# или строка символов, каждый из которых ведет к "Выходу"
def check_exit(sign='YyНн', special=None, txt_req='Продолжить? ("Y" - ДА) -> ', not_mess=None):
    # print(f'sign, special, txt_req -> {(sign, special, txt_req )}')

    add = special if not (special is None) else False
    if isinstance(sign, str):
        inp = input(txt_req)
        out = not (f'-{inp}' in map(lambda el: f'-{el}', f'{sign}{add if add else ""}'))

        print(f'out = {out}')

    else:
        inp = None
        out = sign is None or isinstance(sign, bool) and sign

    if out:
        if not not_mess: print("\nРабота с программой завершена, До встречи!")
        return True

    return False if special is None else inp


# Организация ввода и возврат целого, вещественного числа (в т.ч. отрицательное) или строки
# в заданном диапазоне или выход. С полным контролем корректности
def get_input(*rang, default=None, txt='Введите число', type_input=int, end=None, not_mess=None):
    borders = '' if len(rang) == 0 or rang[0] is None and rang[-1] is None else \
        f'{rang[0]}' if type_input == tuple else \
            f'({rang[0]} ... )' if len(rang) == 1 else \
                f'({rang[0]} ... {rang[1]})'

    txt_input = f'{txt} {f"Возможные значения => {borders}" if borders else ""}'
    frm, to = (rang + (None, None))[:2]

    while True:
        txt_or = '' if end is None or default else ' или '
        key_for_cancel = f'введите "{end}"' if not (end is None) else (f'{txt_or}[Enter]' if default is None else '')
        mess_cancel = '' if not_mess else f'Для отказа {key_for_cancel}'
        entered = input(f'{txt_input} {mess_cancel} -> ')
        entered = None if not (end is None) and entered == end else \
            (None if default is None else default) if len(entered) == 0 else entered
        if entered is None:
            break

        if type_input == tuple:
            if not (entered in rang[0]):
                print(f'Введено "{entered}" допустимые значения {rang[0]}. ', end='')
                txt_input = 'Повторите ввод...'
                continue

        if type_input != int:
            break

        try:
            entered = int(entered)
        except ValueError:
            try:
                entered = float(entered)
            except ValueError:
                print(f'Введенная строка "{entered}" не является числом. ', end='')
                txt_input = 'Повторите ввод.'
                continue

        if not (frm is None) and entered < frm or not (to is None) and entered > to:
            print(f'Введенное число {entered} должно быть в диапазоне ({rang[0]} ... {rang[1]}) -> ', end='')
            txt_input = 'Повторите ввод.'
            continue

        break

    return entered


# Ввод нескольких элементов данных (целых чисел, строк и пр.) - Возврат введенных данных в виде кортежа
def get_inputs(*input_params, type_input=int, end=None, not_mess=None, all_input=None):
    tup_i_par = tuple()
    cnt_params = len(input_params)

    for param in input_params:
        if type_input == tuple:
            if isinstance(param[0], tuple):
                ranges = (param[0], None, param[1] if len(param) == 3 else None)
            else:
                ranges = (param[:-1] + (None, None))[:3]
            default = ranges[2]
            input_param = get_input(ranges[0], ranges[1], default=default,  # = last_input =
                                    txt=param[-1], type_input=type_input, end=end, not_mess=not_mess)
        else:
            input_param = get_input(txt=param, type_input=type_input, end=end, not_mess=not_mess)
        if all_input is None and input_param is None:
            break

        tup_i_par += (input_param,)

    return (tup_i_par + (None,) * cnt_params)[:cnt_params]


# Считывание и возврат данных из файла по заданному пути
def get_data_file(name_file, err_txt='\n'):
    try:
        with open(name_file, 'r', encoding='utf8') as f:
            str_read = f.read()
        return str_read
    except FileNotFoundError:
        print(f'{err_txt}The requested file {name_file} was not found')
        return None


# Запись данных в файл
def wr_data_file(name_file, txt, message=None):
    try:
        f = open(name_file, 'w')
        f.close()
        with open(name_file, 'a', encoding='utf8') as f:
            f.writelines(txt)
        if not (message is None):
            print(f'{message} -> {name_file}')
        return True
    except FileNotFoundError:
        print(f'The requested file {name_file} was not found')
        return None


# транспонирование вложенного списка
# size_ll = len(stt)
# stt_flat = [ell for i in range(size_ll) for el in stt for ell in [el[i]]]            # этот вариант тоже рабочий
# ret = [reduce(lambda ell, el: ell + [el], stt_flat[i * size_ll:][:size_ll], []) for i in range(size_ll)]
def trans_ll(lst_lst):
    return [list(el) for el in zip(*lst_lst)]


# Проверка коллекции на пустые значения {0, None, False, '', [], ()}
def empty_coll(coll):
    return not list(filter(lambda el: el, coll))


# Разделитель строки на кортеж опций
def sep_option(line_option):
    return tuple(f"-{',-'.join(line_option)}".split(','))


# Получение кортежа максимальной длины значения полей БД, записанной в форме списка записей. Каждая запись - словарь.
def get_maxlen_fields(db):
    len_fields = [map(len, map(str, el.values())) for el in db] + [tuple(map(len, db[0]))]
    tlen_fields = [el for el in zip(*len_fields)]
    return list(map(max, tlen_fields))
