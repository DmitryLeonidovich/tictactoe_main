import random
import sys
from typing import List

Done = True
warzone_field = [           # игровое поле
                [0, 0, 0],  # 00 01 02
                [0, 0, 0],  # 10 11 12
                [0, 0, 0]   # 20 21 22
                ]

legal_coord: List[int] = [0, 1, 2, 10, 11, 12, 20, 21, 22]  # список легальных координат

#                                 создание таблицы векторов с координатами
vector_coord = [[0, 1, 2],        # 0 [00, 01, 02]    S=01    C=00
                [10, 11, 12],     # 1 [10, 11, 12]    S=10
                [22, 21, 20],     # 2 [22, 21, 20]    S=21    C=22
                [20, 10, 00],     # 3 [20, 10, 00]            C=20
                [1, 11, 21],      # 4 [01, 11, 21]
                [2, 12, 22],      # 5 [02, 12, 22]    S=12    C=02
                [2, 11, 20],      # 6 [02, 11, 20]
                [0, 11, 22],      # 7 [00, 11, 22]
                [11]              # 8 [11] центровой, никчемный вектор
                ]

vector_corner: List[int] = [0, 2, 20, 22]  # вектор с координатами углов

vector_side: List[int] = [1, 10, 12, 21]  # вектор с координатами середин сторон

#                                   словарь угловых векторов
cell_cor_dic = {0: tuple([0]),      # 00: (0)
                2: tuple([3]),      # 02: (5)
                20: tuple([5]),     # 20: (3)
                22: tuple([2])      # 22: (2)
                }
#                                   словарь боковых векторов
cell_sid_dic = {1: tuple([0]),      # 00: (0)
                10: tuple([3]),     # 10: (3)
                12: tuple([5]),     # 12: (5)
                21: tuple([2])      # 22: (2)
                }
#                                   словарь отстоящих от клетки векторов
cell_dis_dic = {0: tuple([2, 5]),   # 00: (2, 5)
                1: tuple([2, 2]),   # 01: (2, 2)
                2: tuple([2, 3]),   # 02: (2, 3)
                10: tuple([5, 5]),  # 10: (5, 5)
                11: tuple([8, 8]),  # 11: (8, 8)
                12: tuple([3, 3]),  # 12: (3, 3)
                20: tuple([0, 5]),  # 20: (0, 5)
                21: tuple([0, 0]),  # 21: (0, 0)
                22: tuple([0, 3])   # 22: (0, 3)
                }
vector_guru_cnt: List[int] = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # число занятых компьютером клеток по векторно
vector_user_cnt: List[int] = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # число занятых игроком клеток по векторно
play_guru_log = []  # лог ходов компьютера
play_user_log = []  # лог ходов игрока

# по умолчанию пользователь ходит крестиками
user_sign = 2
user_sign_str = 'X'
guru_sign = 1
guru_sign_str = '0'

# крестики ходят первыми
current_step = 1
key_code = 24
poke_cnt = 0

cl: List[str] = ['', '', '', '']  # список подсветки вывода (не для Windows)


def color_mode(mode=True):
    global cl
    if not mode:
        cl = ['', '', '', '']
    else:  # -0-red-------1-grn-------2-yel-------3-clr
        cl = ['\033[31m', '\033[32m', '\033[33m', '\033[0m']
    return


def display_warzone():  # обновление экрана
    s = cl[1] + chr(0x22f1) + ' 0 1 2\n' + cl[3]
    for i in range(0, 3):
        s = s + cl[1] + str(i) + ' ' + cl[3]
        for j in range(0, 3):
            if warzone_field[i][j] == 1:
                ss = '0'
            elif warzone_field[i][j] == 2:
                ss = 'X'
            elif warzone_field[i][j] == 3:
                ss = '*'
            else:
                ss = chr(0x25e6)
            ss += ' '
            s += ss
        s += '\n'
    print(s)
    return


def wrong_coordinates(es):
    print('Error, ' + es + ', repeat please.', end=' ')
    return 24


def user_choice():  # анализ команд пользователя
    attempt_cnt = 0
    key_data = 24
    while key_data > 23:
        key_str = input(cl[2] + 'Input "Q" for exit or coordinates'
                                ' row+column for [' + cl[3] + user_sign_str + cl[2] +
                                '] sign\n(RC = 00, 12, 22):')
        attempt_cnt += 1
        if attempt_cnt > 2:
            attempt_cnt = 0
            print('\nYou play [' + cl[3] + user_sign_str + cl[2] + '] sign.\n')
            display_warzone()
        if len(key_str) > 0:
            print(cl[0])
            if str.isnumeric(key_str):
                key_data = int(key_str)
                if legal_coord.count(key_data):
                    if warzone_field_free(key_data):
                        warzone_field_poke(key_data, user_sign)
                    else:
                        key_data = wrong_coordinates('cell already in use')
                else:
                    key_data = wrong_coordinates('wrong coordinates')
            elif str.lower(key_str) == "q":
                key_data = 23
            else:
                print('Error, invalid symbol, repeat please.', end=' ')
    return key_data


def warzone_field_rc(rc):  # декодер координат клетки из формата [01] в формат [0][1]
    if rc < 10:
        c = rc
        r = 0
    else:
        c = rc % 10
        r = rc // 10
    return [r, c]


def warzone_field_nn(r, c):  # декодер координат клетки из формата [0][1] в формат [01]
    return r * 10 + c


def warzone_field_free(target):  # проверка клетки на незанятость по адресу в формате [01]
    rc = warzone_field_rc(target)
    return warzone_field[rc[0]][rc[1]] == 0


def warzone_field_data(target):  # выборка содержимого клетки по координатам
    rc = warzone_field_rc(target)
    return warzone_field[rc[0]][rc[1]]


def warzone_field_poke(target, data, info=True):  # занесение в клетку по координатам значения (ход)
    global poke_cnt                               # БЕЗ ПРОВЕРКИ НА ЗАНЯТОСТЬ !!!
    rc = warzone_field_rc(target)
    warzone_field[rc[0]][rc[1]] = data
    if data == user_sign:
        play_user_log.append(target)
    else:
        play_guru_log.append(target)
        if info:
            print('Computer poke [' + guru_sign_str + '] to cell', "{:02d}".format(target))
    poke_cnt += 1
    return


def fill_winner_sign(vec):
    for i in vector_coord[vec]:
        warzone_field_poke(i, 3, False)
    return


def vectors_update():  # проверка диспозиции и выставление флагов окончания (для упрощения - каждый раз с "0")
    vec_nom = 0
    for i in vector_coord:
        vector_guru_cnt[vec_nom] = 0
        vector_user_cnt[vec_nom] = 0
        for j in i:
            xo = warzone_field_data(j)
            if xo == guru_sign:
                vector_guru_cnt[vec_nom] += 1
            elif xo == user_sign:
                vector_user_cnt[vec_nom] += 1
        vec_nom += 1
    result = [vector_guru_cnt.count(3) > 0, vector_user_cnt.count(3) > 0,
              ((vector_guru_cnt.count(0) + vector_user_cnt.count(0)) == 0 or (poke_cnt >= 9))]
             
    if result[0]:
        fill_winner_sign(vector_guru_cnt.index(3))
    elif result[1]:
        fill_winner_sign(vector_user_cnt.index(3))
    return result


def guru_choice():  # выбор хода компьютером
    global poke_cnt
    vectors_update()
    vc_zero_pos = None
    for i in range(0, 8):  # просмотр векторов, готовых к закрытию линии компьютером
        if vector_user_cnt[i] == 0 and vector_guru_cnt[i] == 2:
            for vc_zero_pos in vector_coord[i]:
                if warzone_field_data(vc_zero_pos) == 0:
                    break
            warzone_field_poke(vc_zero_pos, guru_sign)
            return  # компьютер завершил линию и выходит из игры
    for i in range(0, 8):  # просмотр векторов, готовых к закрытию линии игроком
        if vector_user_cnt[i] == 2 and vector_guru_cnt[i] == 0:
            for vc_zero_pos in vector_coord[i]:
                if warzone_field_data(vc_zero_pos) == 0:
                    break
            print("Computer cancel completing the line by player.", end=' ')
            warzone_field_poke(vc_zero_pos, guru_sign)
            return  # если такие нашлись - обломать пользователю закрытие линии своим ходом
    if poke_cnt == 0:  # проверка на первый ход
        print('Computer makes the first poke.', end=' ')
        warzone_field_poke(11, guru_sign)
        return  # компьютер сделал первый ход
    if len(play_user_log) > 0:  # ответ на ход игрока
        print('Computer responds to the player''s poke.', end=' ')
        if guru_sign == 2:  # Компьютер играет крестиками - стратегия на победу или ничью
            # поиск наиболее удаленной группы клеток от последнего хода игрока
            vec_list = list(cell_dis_dic.get(play_user_log[len(play_user_log) - 1]))
            # формирование списка клеток
            vc = sorted(list((set(vector_coord[vec_list[0]]) ^ set(vector_coord[vec_list[1]])) |  # не повторяющиеся
                             (set(vector_coord[vec_list[0]]) & set(vector_coord[vec_list[1]]))))  # + повторяющиеся
            random_poke(vc)  # выберем случайным образом из полученного списка клеток одну и сходим в нее
        else:  # Компьютер играет ноликами - стратегия делится на три варианта
            if play_user_log[0] == 11:
                center_blow()  # реакция на первый ход пользователя в центр
            elif play_user_log[0] in vector_corner:
                corner_blow()  # реакция на первый ход пользователя в угол
            elif play_user_log[0] in vector_side:
                side_blow()  # реакция на первый ход пользователя на сторону
            else:  # Что-то пошло не так! Сюда попасть не должно!
                print("Что-то пошло не так!")
                raise OverflowError  # поднимаем ошибку переполнения разума
    return  # нормальный возврат


def center_blow():  # реакция на первый ход пользователя в центр
    # ищем место для удара в угол
    if guru_poke(vector_corner):
        return  # в клетку сходили, сваливаем
    # Ищем место для удара по сторонам, т.к. другого варианта нет
    if guru_poke(vector_side):
        return  # в клетку сходили, сваливаем
    print('Сбой при выборе стратегии ответа на ход игрока в центр.\nСходить не удалось. :-(')
    raise OverflowError  # поднимаем ошибку переполнения разума


def corner_blow():  # реакция на первый ход пользователя в угол
    if poke_cnt == 1:
        warzone_field_poke(11, guru_sign)  # ходим центр, он по определению свободен
        return
    elif poke_cnt == 3:  # ходим в противоположный угол от первого хода пользователя
        vc = [opposite_corner(play_user_log[0])]
        if guru_poke(vc):
            return  # в клетку сходили, сваливаем
        else:  # Ищем место для удара по сторонам, т.к. другого варианта нет
            if guru_poke(vector_side):
                return  # в клетку сходили, сваливаем
        print('Сбой при выборе стратегии ответа на первый ход игрока в противоположный угол.\nСходить не удалось. :-(')
        raise OverflowError  # поднимаем ошибку переполнения разума
    # до конца игры ходим в случайное место (при наличии).
    if random_poke():
        return  # в клетку сходили, сваливаем
    # сюда попадают от безысходности
    print('Сбой при выборе стратегии ответа на первый ход игрока в противоположный угол.')
    print('Не удалось найти любую свободную клетку.\nСходить не удалось. :-(')
    raise OverflowError  # поднимаем ошибку переполнения разума


def side_blow():  # реакция на первый ход пользователя на сторону
    if poke_cnt == 1:
        warzone_field_poke(11, guru_sign)  # ходим центр, он по определению свободен
        return
    if poke_cnt >= 3:
        if play_user_log[0] in vector_corner:
            vc = [opposite_corner(play_user_log[0])]
            if guru_poke(vc):  # ходим в противоположный угол, он по определению свободен
                return
            else:
                plugging_the_hole('БОКОВОЙ: 2-й ход врага в УГОЛ, а свободного противоположного угла НЕТ!')
        elif play_user_log[0] == opposite_side(play_user_log[0]):  #
            if random_poke(vector_corner):
                return
            else:
                plugging_the_hole('БОКОВОЙ: 2-й ход врага на противоположную сторону, а свободных углов НЕТ!')
        elif play_user_log[0] in vector_side:  # первый ход врага (U) на сторону
            vc = play_user_log[len(play_user_log) - 1:len(play_user_log)]  # в vc[0] адрес клетки 2 хода U в формате NN
            if (vc[0] in vector_side) and \
               (vc[0] != opposite_side(play_user_log[0])):  # 2-й ход U на сторону и смежный с 1-м ходом U
                vec_list: List[int] = \
                    [list(cell_sid_dic.get(play_user_log[len(play_user_log) - 1]))[0],
                     list(cell_sid_dic.get(play_user_log[0]))[0]]
                # формирование списка из одной точки, которая общая для смежных сторон
                vc = list(set(vector_coord[vec_list[0]]) & set(vector_coord[vec_list[1]]))
                if guru_poke(vc):
                    return
            else:
                plugging_the_hole('БОКОВОЙ: 2-й ход врага на ближнюю сторону, а общий угол занят!')
        else:
            plugging_the_hole('БОКОВОЙ: 2-й ход врага вообще не понятен!')
    return


def plugging_the_hole(s):
    if random_poke():
        return
    print(s)
    raise OverflowError  # поднимаем ошибку переполнения разума


def opposite_corner(cc):  # вычисление координат противоположного угла
    dc = cc
    if cc in vector_corner:
        if cc == 00:
            dc = 22
        elif cc == 22:
            dc = 0
        elif cc == 20:
            dc = 2
        else:
            dc = 20
    return dc


def opposite_side(cc):  # вычисление координат противоположной стороны
    dc = cc
    if cc in vector_side:
        if cc == 1:
            dc = 21
        elif cc == 21:
            dc = 1
        elif cc == 10:
            dc = 12
        else:
            dc = 10
    return dc


def free_cells(fc_vec_comp=None):  # список пустых клеток по всему полю или по переданному вектору
    dfc_f = []
    dfc_v = []
    with_compare = fc_vec_comp is not None  # признак наличия вектора для поиска
    for i in range(9):
        f = (i // 3) * 10 + (i % 3)
        if warzone_field[i // 3][i % 3] == 0:  # если текущая клетка пуста
            if with_compare:
                for j in fc_vec_comp:
                    if j == f:
                        dfc_v.append(f)  # занесен в выборку по вектору
                        break
            # занесен в выборку по всему полю
            dfc_f.append(f)
    if with_compare and len(dfc_v) != 0:
        return dfc_v  # возврат выборки по вектору при ее наполненности
    if len(dfc_f) == 0:  # сюда попадают от безысходности
        print('Смотрели по всему полю битвы.')
        print('Не удалось найти ни одной свободной клетки.\nСходить не удалось. :-(')
        raise OverflowError  # поднимаем ошибку переполнения разума
    return dfc_f  # Возврат выборки по всему полю 'по любому'. Если пустая, то поднять ошибку после возврата


def random_poke(rp_vec_comp=None):  # случайный ход по всему полю или по линии переданного вектора
    if rp_vec_comp is None:
        free_cells_lst = free_cells()  # создание списка свободных клеток по всему полю
    else:
        free_cells_lst = free_cells(rp_vec_comp)  # создание списка свободных клеток из вектора
    free_cells_cnt = len(free_cells_lst)  # определяем количество свободных клеток
    vc = free_cells_lst[random.randint(0, free_cells_cnt - 1)]
    warzone_field_poke(vc, guru_sign)
    return True  # в клетку ходим и сваливаем с возвратом успешного результата


def guru_poke(vector):  # отработка списка клеток для возможного удара с проверкой на свободность
    poke_cnt_before = poke_cnt  # сохраним число внесенных ходов на поле боя до поиска места для нового
    for i in vector:  # ищем первое встреченное свободное место для удара
        if warzone_field_free(i):
            warzone_field_poke(i, guru_sign)
            return poke_cnt_before < poke_cnt  # в клетку сходили, сваливаем с признаком успеха
    return False  # сделать ход не удалось сваливаем понуро


"""
# main block ======================================================
"""


if sys.platform == 'win32':
    color_mode(False)
# color_mode(True) # для PyCharm можно разбанить
print('\nHello guys! This is Tic-tac-toe.')
if len(input('Simply press Enter if you choose [X] sign, any other key - [0] sign:')) != 0:
    user_sign = 1
    guru_sign = 2
    user_sign_str = '0'
    guru_sign_str = 'X'
    current_step = 0  # крестики ходят первыми, а это GURU
else:
    display_warzone()

while Done:
    if current_step:
        key_code = user_choice()
        g_res = vectors_update()
    else:
        guru_choice()
        g_res = vectors_update()
        display_warzone()
    current_step = (current_step + 1) & 1
    if g_res[0] or g_res[1] or g_res[2]:
        key_code = 23
        if g_res[0]:
            print('The computer won!!!')
        elif g_res[1]:
            display_warzone()
            print('The user won!!!')
        elif g_res[2]:
            display_warzone()
            print('The game ended in a draw!!!')
    Done = not key_code == 23
print('Game over. Thankyou and bye.')
