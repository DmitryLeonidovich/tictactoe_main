Done = True
warzone_field = [ # игровое поле
                 [0, 0, 0],
                 [0, 0, 0],
                 [0, 0, 0]
                 ]
legal_coord = [0,1,2,10,11,12,20,21,22] # список легальных координат
vector_coord = [legal_coord[0:3:1],
                legal_coord[3:6:1],
                legal_coord[6:9:1],
                legal_coord[0:9:3],
                legal_coord[1:9:3],
                legal_coord[2:9:3],
                legal_coord[2:8:2],
                legal_coord[0:9:4]
                ]

cell_dis_dic = { 0: tuple([2, 5]),  # словарь отстоящих векторов
                 1: tuple([2, 9]),
                 2: tuple([2, 3]),
                10: tuple([5, 9]),
                11: tuple([9, 9]),
                12: tuple([3, 9]),
                20: tuple([0, 5]),
                21: tuple([0, 9]),
                22: tuple([0, 3])
                }
vector_guru_cnt = [0,0,0,0,0,0,0,0] # число чпокнутых компьютером клеток повекторно
vector_user_cnt = [0,0,0,0,0,0,0,0] # число чпокнутых игроком клеток повекторно
play_guru_log = []                  # лог ходов компьютера
play_user_log = []                  # лог ходов игрока

# по умолчанию пользователь ходит крестиками
user_sign = 2
user_sign_str = 'X'
guru_sign = 1
# крестики ходят первыми
current_step = 1
keycode = 24
poke_cnt = 0

''' обновление экрана '''
def display_warzone():
    s = chr(0x22f1) + ' 0 1 2\n'
    for i in range(0, 3):
        s = s + str(i) + ' '
        for j in range(0, 3):
            if warzone_field[i][j] == 1:
                ss = '0'
            elif warzone_field[i][j] == 2:
                ss = 'X'
            else:
                ss = chr(0x25e6)
            ss += ' '
            s += ss
        s +='\n'
    print(s)
    return

def wrong_coordinates(es):
    print('Error, ' + es +', repeat please.', end=' ')
    return 24

''' анализ команд пользователя'''
def user_choice():
    attempt_cnt = 0
    keydata = 24
    while keydata > 23:
        keystr = input('Input "Q" for exit or coordinates row+column for [' + user_sign_str + '] sign\n(RC - 00 - 22):')
        attempt_cnt +=1
        if attempt_cnt > 2:
            attempt_cnt = 0
            print('\nYou play [' + user_sign_str + '] sign.\n')
            display_warzone()
        if len(keystr) > 0:
            if str.isnumeric(keystr):
                keydata = int(keystr)
                if legal_coord.count(keydata):
                    if warzone_field_free(keydata):
                        warzone_field_poke(keydata, user_sign)
                    else:
                        keydata = wrong_coordinates('cell already in use')
                else:
                    keydata = wrong_coordinates('wrong coordinates')
            elif str.lower(keystr) == "q":
                keydata = 23
            else: print('Error, invalid symbol, repeat please.', end=' ')
    return keydata

# декодер координат клетки
def warzone_field_rc(rc):
    if rc <10:
        c = rc
        r = 0
    else:
        c = rc % 10
        r = rc // 10
    #print('Декодер координат', rc, r, c)
    return [r,c]
# декодер координат проверка клетки на занятость
def warzone_field_free(target):
    rc = warzone_field_rc(target)
    #print('координаты точки перед проверкой', rc)
    #print('Состояние точки', warzone_field[rc[0]][rc[1]])
    return warzone_field[rc[0]][rc[1]] == 0
# выборка содержимого клетки по координатам
def warzone_field_data(target):
    rc = warzone_field_rc(target)
    #print('координаты точки перед проверкой', rc)
    #print('Состояние точки', warzone_field[rc[0]][rc[1]])
    return warzone_field[rc[0]][rc[1]]


# занесение в клетку по координатам значения (сокращенно "чпок")
def warzone_field_poke(target, data):
    global poke_cnt
    rc = warzone_field_rc(target)
    warzone_field[rc[0]][rc[1]] = data
    if data == user_sign:
        play_user_log.append(target)
    else:
        play_guru_log.append(target)
        print('Computer poke [' + chr(guru_sign) + '] to cell ', target)
    poke_cnt +=1
    return
# проверка диспозиции и выставление флагов окончания (для упрощения - каждый раз с "0")
def vectors_update():
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
        vec_nom +=1

    #print('GURU=', vector_guru_cnt, 'LOG=', play_guru_log)
    #print('USER=', vector_user_cnt, 'LOG=', play_user_log)
    res = [vector_guru_cnt.count(3) > 0,
           vector_user_cnt.count(3) > 0,
           ((vector_guru_cnt.count(0) + vector_user_cnt.count(0)) == 0 or (poke_cnt >= 9))]
    #print('Флаги=', res, vector_guru_cnt.count(0), vector_user_cnt.count(0))
    return res
# выбор хода компьютером
def guru_choice():
    global poke_cnt
    #print(legal_coord)
    #print(vector_coord)
    vectors_update()
    #print(vc)
    vc = []
    for i in range(0, 8):
        if vector_user_cnt[i] == 2 and vector_guru_cnt[i] == 0:
            vc.append(i)
    #print('VC=', vc)
    #print('VC lenght=', len(vc))
    # проверка на угрозу заполнения линии
    if len(vc) > 0:
        vec_nom = vc[0]
        print("Computer cancel completing the line by player.", end=' ')
        #print('Warning=', vec_nom)
        #print('Vector=', vector_coord[vec_nom])
        vc = vector_coord[vec_nom]
        for i in vc:
            if warzone_field_data(i) == 0:
                warzone_field_poke(i, guru_sign)
    # проверка на первый ход
    elif poke_cnt == 0:
        print('Computer makes the first poke.', end=' ')
        warzone_field_poke(11, guru_sign)
    # ответ на ход игрока
    elif len(play_user_log) > 0:
        print('Computer responds to the player''s poke.', end=' ')
        if guru_sign == 2: # Компьютер играет крестиками - стратегия на победу или ничью
            #print('Last User choice =', play_user_log)
            #print('Last User choice =', play_user_log[len(play_user_log) - 1:len(play_user_log)])
            #print("I'll try to decide what to do!!!")
            # получим список координат чпоков врага и выберем последний
            vec_dis_dic_key = play_user_log[len(play_user_log) - 1:len(play_user_log)]
            # заберем из полученного списка последнее значение (список состоит всегда из одного, последнего значения)
            vec_list = cell_dis_dic.get(vec_dis_dic_key[0])
            #print('Vectors to check =', vec_list)
            poke_cnt_before = poke_cnt  # сохраним число внесенных чпоков на поле боя до поиска места для нового
            for i in vec_list:
                if (i != 9) and (poke_cnt_before == poke_cnt):  # если вектор существует и еще не чпокнули в поле
                    vec_cell_poke(i)
            #print('poke_cnt_before=', poke_cnt_before, 'poke_cnt=', poke_cnt)
            if poke_cnt_before < poke_cnt: return # в клетку чпокнули, сваливаем
            # вектора забиты, нужно искать свободную клетку в ближнем окружении последнего вражьего чпока
            #print('GURU=', vector_guru_cnt)
            #print('USER=', vector_user_cnt)
            if 0 <= vector_guru_cnt.count(0) < 8:
                # выбираем клетку из векторов компьютера
                #print('vector_guru_cnt.count(0)', vector_guru_cnt.count(0))
                vec_cell_poke(vector_guru_cnt.count(0))
            else:
                # если первый ход компьютера после игрока то ищем по векторам игрока
                #print('vector_user_cnt.count(0)', vector_user_cnt.count(0))
                vec_cell_poke(vector_user_cnt.count(0))
        else: # Компьютер играет ноликами - стратегия делится на три варианта
            pass
    return

# выполнение хода компьютером в свободную клетку по вектру принадлежности
# без привязки к последнему ходу игрока
def vec_cell_poke(vector_nom):
    vec_cell = vector_coord[vector_nom]
    #print('Вектор с координатами =', vec_cell)
    # проверим вектор на свободные места и засадим в первое встреченное
    # с одного края
    if warzone_field_free(vec_cell[0]): warzone_field_poke(vec_cell[0], guru_sign)
    # с другого края
    elif warzone_field_free(vec_cell[2]): warzone_field_poke(vec_cell[2], guru_sign)
    # в середине
    elif warzone_field_free(vec_cell[1]): warzone_field_poke(vec_cell[1], guru_sign)
    return

'''
main block ======================================================
'''
#print(vector_coord)
#print(cell_dis_dic)
print('\nHello guys! This is Tic-tac-toe.')

if len(input('Simply press Enter if you choose [X] sign, any other key - [0] sign:')) != 0:
    user_sign = 1
    guru_sign = 2
    user_sign_str = '0'
    current_step = 0  # крестики ходят первыми, а это GURU

while Done:
    display_warzone()
    if current_step:
        keycode = user_choice()
    else:
        guru_choice()
    current_step = (current_step + 1) & 1
    res = vectors_update()
    if res[0] or res[1] or res[2]:
        keycode = 23
        display_warzone()
        if res[0]:
            print('The computer won!!!')
        elif res[1]:
            print('The user won!!!')
        elif res[2]:
            print('The game ended in a draw!!!')
    Done = not keycode == 23

print('Game over. Thankyou and by.')
