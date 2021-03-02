
import numpy as np
import copy
import utils
import itertools

ids = ['342457421', '931177406']

""" Tab change for letter to int 
             unpopulated  U = 1
             immune       I = 8

             healthy      H = 2

             sick         S = 33 - 3 days left 
                            = 32 - 2 days left
                            = 31 -  Last day 
                            = 30 go to healthy --> 2



             quarantined  Q = 52 - 2 days left
                            = 51 -  Last day 
                            = 50 go to healthy --> 2

            ? :  0  1  2  3  4  5  6  7  
                 U  H S1 S2 S3  I Q1 Q2
                 2 si vrai 1 si faux
               """


def solve_problem(input):
    maps = input['observations']
    queries = input['queries']
    police = input['police']
    medics = input['medics']

    all_the_maps = fulling_my_maps(maps, police)

    all_the_actions = {}
    for time in range(len(maps)):
        if time == len(maps) - 1:
            break

        all_the_actions[time] = actions(all_the_maps[time], police, medics)

    all_the_maps = prepare_the_maps(all_the_maps, all_the_actions)

    dict_result = {}

    for i in range(len(queries)):
        coor = queries[i][0]
        time = queries[i][1]
        val = queries[i][2]
        tr_val = trad_val(val)
        if all_the_maps[time][coor[0]][coor[1]] > 1111:
            dict_result[queries[i]] = '?'
        elif dizaine_number(all_the_maps[time][coor[0]][coor[1]])[0] == tr_val:
            dict_result[queries[i]] = 'T'
        elif dizaine_number(all_the_maps[time][coor[0]][coor[1]])[0] != tr_val:
            dict_result[queries[i]] = 'F'

    return dict_result
    # put your solution here, remember the format needed


def fulling_my_maps(maps, police):
    """ fulling the all_maps with the helps of maps
    with the code of ex1
    if the case is ? fulling with the previous information
    if their are not previous information (time = 0 ) fulling with all the possible information frone the start"""
    list_of_maps = []
    shape = [len(maps[0]), len(maps[0][0])]
    for t in range(len(maps)):
        actual_map = np.zeros(shape, int)
        if t == 0:
            for i in range(shape[0]):
                for j in range(shape[1]):
                    letter = maps[t][i][j]
                    if letter == 'U':
                        actual_map[i][j] = 1
                    elif letter == 'H':
                        actual_map[i][j] = 2
                    elif letter == 'S':
                        actual_map[i][j] = 33
                    elif letter == 'I':
                        actual_map[i][j] = 8
                    elif letter == 'Q':
                        actual_map[i][j] = 52
                    elif letter == '?':
                        actual_map[i][j] = 22211111
        else:
            for i in range(shape[0]):
                for j in range(shape[1]):
                    letter = maps[t][i][j]
                    previous_num = list_of_maps[t - 1][i][j]
                    if letter == 'U':
                        actual_map[i][j] = 1
                    elif letter == 'H':
                        actual_map[i][j] = 2
                    elif letter == 'S':
                        if dizaine_number(previous_num)[0] == 3:
                            if previous_num == 33:
                                actual_map[i][j] = 32
                            if previous_num == 32:
                                actual_map[i][j] = 31

                        else:
                            actual_map[i][j] = 33
                        # the previous num is not sure
                        if previous_num > 11111:
                            conter = []
                            if dizaine_number(previous_num)[2] == 2:
                                conter.append(2)
                            if dizaine_number(previous_num)[3] == 2:
                                conter.append(1)
                            if dizaine_number(previous_num)[4] == 2:
                                conter.append(3)

                            if len(conter) == 1:
                                actual_map[i][j] = 30 + conter[0]
                            if len(conter) == 0:
                                actual_map[i][j] = 33
                            elif len(conter) > 1:
                                tmp = [1, 1, 1, 1, 1, 1, 1, 1]
                                for ct in range(len(conter)):
                                    if conter[ct] == 2:
                                        tmp[3] = 2
                                    if conter[ct] == 1:
                                        tmp[4] = 2
                                    if conter[ct] == 3:
                                        tmp[2] = 2
                                actual_map[i][j] = tab_to_number(tmp)
                    elif letter == 'I':
                        actual_map[i][j] = 8
                    elif letter == 'Q':
                        if dizaine_number(previous_num)[0] == 5:
                            if previous_num == 52:
                                actual_map[i][j] = 51
                        if dizaine_number(previous_num)[0] == 3:
                            actual_map[i][j] = 52
                        if previous_num > 1111:
                            if check_chiffre(previous_num, 2, 6):
                                actual_map[i][j] = 11111122

                    elif letter == '?':
                        tab_previous = dizaine_number(previous_num)
                        tab_result = copy.deepcopy(tab_previous)
                        if previous_num > 1111:
                            if tab_previous[2] == 2:
                                tab_result[2] = 1
                                tab_result[3] = 2
                                tab_result[6] = 2
                            if tab_previous[3] == 2:
                                tab_result[3] = 1
                                tab_result[4] = 2
                                tab_result[6] = 2
                            if tab_previous[4] == 2:
                                tab_result[4] = 1
                                tab_result[1] = 2
                            if tab_previous[6] == 2:
                                tab_result[6] = 1
                                tab_result[7] = 2
                            if tab_previous[7] == 2:
                                tab_result[7] = 1
                                tab_result[1] = 2
                            actual_map[i][j] = tab_to_number(tab_result)
                        else:
                            tmp_tab = [1, 1, 1, 1, 1, 1, 1, 1]

                            if previous_num == 2:
                                tmp_tab[1] = 2
                            if previous_num == 33:
                                tmp_tab[3] = 2
                                if police > 0:
                                    tmp_tab[6] = 2
                            if previous_num == 32:
                                tmp_tab[4] = 2
                                if police > 0:
                                    tmp_tab[6] = 2
                            if previous_num == 31:
                                tmp_tab[1] = 2
                            if previous_num == 52:
                                tmp_tab[7] = 2
                            if previous_num == 51:
                                tmp_tab[1] = 2

                            actual_map[i][j] = tab_to_number(tmp_tab)
                            if previous_num == 1:
                                actual_map[i][j] = 1

        list_of_maps.append(actual_map)

    return list_of_maps


def trad_val(x):
    if x == 'H':
        return 2
    if x == 'U':
        return 1
    if x == 'S':
        return 3
    if x == 'I':
        return 8
    if x == 'Q':
        return 5


def actions(map_np, police, medics):
    vaccinate_list = []
    quarantine_list = []
    shape = [len(map_np), len(map_np[0])]

    # fulling vaccinate list
    for i in range(shape[0]):
        for j in range(shape[1]):
            number = map_np[i][j]
            if number == 2:
                vaccinate_list.append(('vaccinate', (i, j)))
            if number > 111:
                if dizaine_number(number)[1] == 2:
                    vaccinate_list.append(('vaccinate', (i, j)))

    # fulling quarantine list
    for i in range(shape[0]):
        for j in range(shape[1]):
            number_arr = dizaine_number(map_np[i][j])
            if number_arr[0] == 3:
                quarantine_list.append(('quarantine', (i, j)))
            if len(number_arr) > 2:
                if number_arr[2] == 2 or number_arr[3] == 2 or number_arr[4] == 2:
                    quarantine_list.append(('quarantine', (i, j)))

    all_action = []

    mixed_quarantine_list = special_power_set(quarantine_list, min(police, len(quarantine_list)))
    mixed_vaccinate_list = special_power_set(vaccinate_list, min(medics, len(vaccinate_list)))

    mixed_vaccinate_list = list(mixed_vaccinate_list)
    mixed_quarantine_list = list(mixed_quarantine_list)

    for i in range(len(mixed_quarantine_list)):
        for j in range(len(mixed_vaccinate_list)):
            tpi = mixed_quarantine_list[i]
            tpj = mixed_vaccinate_list[j]
            temp = tpj + tpi
            all_action.append(temp)
    all_action_tuple = tuple(all_action)
    if medics == 0 and police != 0:
        return mixed_quarantine_list
    if medics != 0 and police == 0:
        return tuple(mixed_vaccinate_list)
    if medics == 0 and police == 0:
        return all_action

    return all_action_tuple


def prepare_the_maps(all_map, all_the_actions):
    list_of_unknown = {}
    dict_map_possib = {}

    shape = [len(all_map[0]), len(all_map[0][0])]

    for time in range(len(all_map)):
        coor_list = []
        if time == len(all_map) - 1:
            break
        for i in range(shape[0]):
            for j in range(shape[1]):
                poss_list = []
                if all_map[time][i][j] > 111:
                    arr_value = dizaine_number(all_map[time][i][j])
                    if arr_value[0] == 2:
                        poss_list.append(1)
                    if arr_value[1] == 2:
                        poss_list.append(2)
                    if arr_value[2] == 2:
                        poss_list.append(33)
                    if arr_value[3] == 2:
                        poss_list.append(32)
                    if arr_value[4] == 2:
                        poss_list.append(31)
                    if arr_value[5] == 2:
                        poss_list.append(1)
                    if arr_value[6] == 2:
                        poss_list.append(52)
                    if arr_value[7] == 2:
                        poss_list.append(51)
                    coor_list.append(poss_list)
        list_of_unknown[time] = coor_list

    for time in range(len(list_of_unknown)):
        if len(list_of_unknown[time]) == 0:
            continue
        for unk in range(len(list_of_unknown[time])):
            for pos in range(len(list_of_unknown[time][unk])):
                val = list_of_unknown[time][unk][pos]
                list_of_unknown[time][unk][pos] = put_number_in_zero(val, unk + 1)

    for time in range(len(list_of_unknown)):
        list_tmp_map = []
        coor_of_unknown = where(all_map[time], 1111, 'sup')
        tmp_list = []
        if len(list_of_unknown[time]) == 0:
            tmp = []
            tmp.append(all_map[time])
            dict_map_possib[time] = tmp
            continue
        for unk in range(len(list_of_unknown[time])):
            tmp_list += list_of_unknown[time][unk]
        number_unk = len(list_of_unknown[time])
        sub = spcial_subsets(tmp_list, number_unk)

        for s in range(len(sub)):
            for unk in range(number_unk):
                sub[s][unk] = remove_number_in_zero(sub[s][unk])

        for s in range(len(sub)):
            tmp_map = copy.deepcopy(all_map[time])
            for unk in range(number_unk):
                coord = coor_of_unknown[unk]
                tmp_map[coord[0]][coord[1]] = sub[s][unk]
            list_tmp_map.append(tmp_map)
        dict_map_possib[time] = list_tmp_map

    for time in range(len(dict_map_possib)):
        list_equal = []
        act_equal = []
        actual_map_eq = []
        coor_of_unknown = where(all_map[time], 1111, 'sup')

        for im in range(len(dict_map_possib[time])):
            for act in range(len(all_the_actions)):

                test_map = dict_map_possib[time][im]
                if len(all_the_actions[time]) == 0:
                    test_action = []
                else:
                    test_action = all_the_actions[time][act]

                map_res = result(test_map, test_action, shape)

                true_future_map = all_map[time + 1]

                if check_tow_map_equal(map_res, true_future_map):
                    if len(list_equal) == 0:
                        list_equal.append(map_res)
                        actual_map_eq.append(dict_map_possib[time][im])
                        act_equal.append(all_the_actions[act])
                    elif not check_tow_map_equal(list_equal[0], map_res):
                        list_equal.append(map_res)
                        actual_map_eq.append(dict_map_possib[time][im])
                        act_equal.append(all_the_actions[act])

        # list_equal = distinct(list_equal)
        if len(list_equal) == 1:
            map_choice = actual_map_eq[0]
            all_map[time] = map_choice
            map_res = list_equal[0]
            all_map[time + 1] = map_res

        if len(list_equal) > 1:
            for unk in range(len(coor_of_unknown)):
                crd = coor_of_unknown[unk]
                tmp_val = [1, 1, 1, 1, 1, 1, 1, 1]
                for eq in range(len(list_equal)):
                    map_res = list_equal[eq]
                    val_res = map_res[crd[0]][crd[1]]
                    if val_res == 1:
                        tmp_val[0] = 2
                    if val_res == 2:
                        tmp_val[1] = 2
                    if val_res == 33:
                        tmp_val[2] = 2
                    if val_res == 32:
                        tmp_val[3] = 2
                    if val_res == 31:
                        tmp_val[4] = 2
                    if val_res == 8:
                        tmp_val[5] = 2
                    if val_res == 52:
                        tmp_val[6] = 2
                    if val_res == 51:
                        tmp_val[7] = 2
                all_map[time][crd[0]][crd[1]] = tab_to_number(tmp_val)

    for time in range(len(all_map)):
        for i in range(shape[0]):
            for j in range(shape[1]):
                val = all_map[time][i][j]
                if val > 1111:
                    if check_safe_case(val):
                        all_map[time][i][j] = check_safe_case(val)
    vac_list = []
    unpop_list = []
    for time in range(len(all_map)):
        for i in range(shape[0]):
            for j in range(shape[1]):
                val = all_map[time][i][j]
                if val == 8:
                    vac_list.append((i, j, time))
                if (i, j) in unpop_list:
                    continue
                if val == 1:
                    unpop_list.append((i, j))
    for vac in vac_list:
        x = vac[0]
        y = vac[1]
        time = vac[2]
        for t2 in range(len(all_map)):
            if t2 > time:
                all_map[t2][x][y] = 8

    for un in unpop_list:
        x = un[0]
        y = un[1]
        for t2 in range(len(all_map)):
            all_map[t2][x][y] = 1

    return all_map


def result(map_base, action, shape):
    map_np = copy.deepcopy(map_base)

    # 1 do all the action
    for i in range(len(action)):
        if len(action) == 0:
            break
        type_action = action[i][0]

        coor_action = action[i][1]

        if type_action == 'vaccinate' or type_action == 'v':
            map_np[coor_action[0]][coor_action[1]] = 8
        if type_action == 'quarantine' or type_action == 'q':
            map_np[coor_action[0]][coor_action[1]] = 53

        # 2 contamination
    list_contamination = []
    for i in range(shape[0]):
        for j in range(shape[1]):

            if dizaine_number(map_np[i][j])[0] == 3:
                if check_in_map(i - 1, j, shape):
                    if map_np[i - 1][j] == 2:
                        tmp = [i - 1, j]
                        list_contamination.append(tmp)

                if check_in_map(i + 1, j, shape):
                    if map_np[i + 1][j] == 2:
                        tmp = [i + 1, j]
                        list_contamination.append(tmp)

                if check_in_map(i, j - 1, shape):
                    if map_np[i][j - 1] == 2:
                        tmp = [i, j - 1]
                        list_contamination.append(tmp)

                if check_in_map(i, j + 1, shape):
                    if map_np[i][j + 1] == 2:
                        tmp = [i, j + 1]
                        list_contamination.append(tmp)

    for i in range(len(list_contamination)):
        map_np[list_contamination[i][0]][list_contamination[i][1]] = 34

    # 3 reduce the quarantine and sicks
    for i in range(shape[0]):
        for j in range(shape[1]):
            number = dizaine_number(map_np[i][j])
            if number[0] == 3 or number[0] == 5:
                if number[1] == 1:
                    map_np[i][j] = 2
                else:
                    map_np[i][j] -= 1

    return map_np


def where(arr, value, st):
    list_res = []

    if len(np.shape(arr)) == 1:
        for i in range(len(arr)):
            if arr[i] == value and st == 'eq':
                list_res.append(i)
            elif arr[i] > value and st == 'sup':
                list_res.append(i)
        return list_res

    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if arr[i][j] == value and st == 'eq':
                list_res.append((i, j))
            elif arr[i][j] > value and st == 'sup':
                list_res.append((i, j))
    return list_res


def check_safe_case(x):
    """check if one unknow case have just one possibility
    input : x  int of 8 chiffres
    output :if yes return the true value
            else return fals"""

    tab_x = dizaine_number(x)
    tab_x = np.asanyarray(tab_x)

    indx_tow = where(tab_x, 2, 'eq')

    if len(indx_tow) > 1:
        return False

    if indx_tow[0] == 0:
        return 1
    if indx_tow[0] == 1:
        return 2
    if indx_tow[0] == 2:
        return 33
    if indx_tow[0] == 3:
        return 32
    if indx_tow[0] == 4:
        return 31
    if indx_tow[0] == 5:
        return 1
    if indx_tow[0] == 6:
        return 52
    if indx_tow[0] == 7:
        return 51


def check_tow_map_equal(resmap, truemap):
    shape = np.shape(resmap)
    for i in range(shape[0]):
        for j in range(shape[1]):
            if truemap[i][j] > 1111:
                continue
            if truemap[i][j] != resmap[i][j]:
                return False
    return True


def tab_to_number(x):
    """arr of 8  with len(arr) == 8  to a int
    intput : [1, 2, 3, 4, 5, 6, 7, 8] ---> 12345678"""

    res = 0
    po = 7
    for i in range(8):
        res += x[i] * pow(10, po)
        po -= 1
    return res


def check_maybe_sick(x):
    """check if the case is maybe an sick 33 or 32"""
    if check_chiffre(x, 2, 2):
        return True
    if check_chiffre(x, 2, 3):
        return True
    return False


def check_chiffre(x, value, place):
    """check if in the number the value is in the place
    x:1234, value: 3, place:2 ----> true  """
    arr_x = dizaine_number(x)

    if arr_x[place] == value:
        return True
    return False


def check_in_map(x, y, shape):
    if shape[0] > x >= 0 and shape[1] > y >= 0:
        return True
    return False


def dizaine_number(x):
    """transphorm a int number to a revers arr
    1234 ---> [1, 2, 3, 4]"""
    chiffres = []
    while x > 0:
        chiffres.append(x % 10)
        x = x // 10
    chiffres.reverse()
    return chiffres


def findsubsets(s, n):
    if len(s) >= n:
        return [list(i) for i in itertools.combinations(s, n)]
    else:
        return [s]


def put_number_in_zero(x, val):
    x += val * 10 ** len(dizaine_number(x))
    return x


def remove_number_in_zero(x):
    val = dizaine_number(x)[0]
    x -= val * 10 ** (len(dizaine_number(x)) - 1)
    return x


def spcial_subsets(list, k):
    res = findsubsets(list, k)

    final_res = []
    for i in range(len(res)):
        flag = 0
        for tr in range(k):
            if dizaine_number(res[i][tr])[0] != tr + 1:
                flag = 1
        if flag == 0:
            final_res.append(res[i])
    return final_res


def special_power_set(list, k):
    temp = utils.powerset(list)
    final = []
    for i in range(len(temp)):
        if len(temp[i]) == k:
            final.append(temp[i])
    return final
