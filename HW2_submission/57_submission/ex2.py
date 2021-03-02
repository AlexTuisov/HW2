import utils
import sympy

ids = ['316365410', '312234784']


def query_if_h(pol_team, med_team, observ, turn_num, index):
    bool_check = '?'

    for turn in observ:
        if turn[index[0]][index[1]] == "U":
            bool_check = 'F'
            return bool_check
    if (turn_num + 1) != len(observ):
        if observ[turn_num + 1][index[0]][index[1]] == "Q":
            bool_check = 'F'
            return bool_check
        elif observ[turn_num + 1][index[0]][index[1]] == "H":
            if turn_num < 2:
                bool_check = 'T'
                return bool_check
            elif observ[turn_num - 1][index[0]][index[1]] == "H":
                bool_check = 'T'
                return bool_check
        elif observ[turn_num + 1][index[0]][index[1]] == "I":
            if turn_num == 0:
                bool_check = 'T'
                return bool_check
            elif observ[turn_num - 1][index[0]][index[1]] == "I":
                bool_check = 'F'
                return bool_check
            elif observ[turn_num - 1][index[0]][index[1]] == "H":
                count_question = count_question_mark_in_turn(observ, turn_num - 1)
                count_h = count_h_in_turn(observ, turn_num - 1)
                if med_team >= (count_h + count_question):
                    bool_check = 'F'
                    return bool_check
                elif med_team == (count_h_turned_into_i(observ, turn_num - 1)):
                    bool_check = 'T'
                    return bool_check
        elif observ[turn_num + 1][index[0]][index[1]] == "S":
            if not check_S_neihbours(observ, turn_num, index):
                bool_check = 'F'
            elif check_S_neihbours(observ, turn_num, index):
                if check_H_neihbours(observ, turn_num, index) != 0:
                    h_neighbours = check_H_neihbours(observ, turn_num, index)
                    for neighbour in h_neighbours:
                        if observ[turn_num + 1][neighbour[0]][neighbour[1]] == "S":
                            bool_check = 'F'
                            return bool_check
                        if observ[turn_num + 1][neighbour[0]][neighbour[1]] == "H":
                            bool_check = 'T'
                            return bool_check
        elif observ[turn_num + 1][index[0]][index[1]] == "?":
            if (turn_num + 2) != len(observ):
                if observ[turn_num + 2][index[0]][index[1]] == "S":
                    if not check_S_neihbours(observ, turn_num, index):
                        bool_check = 'F'
                    elif check_S_neihbours(observ, turn_num, index):
                        if check_H_neihbours(observ, turn_num, index) != 0:
                            h_neighbours = check_H_neihbours(observ, turn_num, index)
                            for neighbour in h_neighbours:
                                if observ[turn_num + 1][neighbour[0]][neighbour[1]] == "S":
                                    bool_check = 'F'
                                    return bool_check
                                if observ[turn_num + 1][neighbour[0]][neighbour[1]] == "H":
                                    bool_check = 'T'
                                    return bool_check
            else:
                if check_H_neihbours(observ, turn_num, index) != 0:
                    h_neighbours = check_H_neihbours(observ, turn_num, index)
                    for neighbour in h_neighbours:
                        if observ[turn_num + 1][neighbour[0]][neighbour[1]] == "S":
                            bool_check = 'F'
                            return bool_check

    if turn_num != 0:
        if (observ[turn_num - 1][index[0]][index[1]] == "U") or (observ[turn_num - 1][index[0]][index[1]] == "I"):
            bool_check = 'F'
            return bool_check
        elif observ[turn_num - 1][index[0]][index[1]] == "H":
            if med_team == 0:
                if (not check_S_neihbours(observ, turn_num - 1, index)) or (
                        check_S_neihbours(observ, turn_num - 1, index) and not check_S_neihbours(observ, turn_num,
                                                                                                 index)):
                    bool_check = 'T'
                    return bool_check
                else:
                    bool_check = 'F'
                    return bool_check
            count_question = count_question_mark_in_turn(observ, turn_num - 1)
            count_h = count_h_in_turn(observ, turn_num - 1)
            if med_team >= (count_h + count_question):
                bool_check = 'F'
                return bool_check
            elif med_team == (count_h_turned_into_i(observ, turn_num - 1)):
                if not check_S_neihbours(observ, turn_num, index):
                    bool_check = 'T'
                else:
                    if turn_num != (len(observ) - 1):
                        if check_S_neihbours(observ, turn_num + 1, index):
                            bool_check = 'F'
                            return bool_check

        elif observ[turn_num - 1][index[0]][index[1]] == "Q":
            if turn_num > 2:
                if observ[turn_num - 2][index[0]][index[1]] == "Q":
                    bool_check = 'T'
                    return bool_check
                else:
                    bool_check = 'F'
                    return bool_check
            else:
                bool_check = 'F'
                return bool_check

            # check the option that we had question mark in the middle

        elif observ[turn_num - 1][index[0]][index[1]] == "S":
            if turn_num > 3:
                if observ[turn_num - 2][index[0]][index[1]] == "S":
                    if observ[turn_num - 3][index[0]][index[1]] == "S":
                        bool_check = 'T'
                        return bool_check
                    else:
                        bool_check = 'F'
                        return bool_check
                else:
                    bool_check = 'F'
                    return bool_check
            else:
                bool_check = 'F'
                return bool_check
        elif observ[turn_num - 1][index[0]][index[1]] == "?":
            if check_S_neihbours(observ, turn_num - 1, index):
                if check_S_neihbours(observ, turn_num, index):
                    bool_check = 'F'
                    return bool_check
    if turn_num != (len(observ) - 1):
        if check_S_neihbours(observ, turn_num, index) and check_S_neihbours(observ, turn_num + 1, index):
            if query_if_s(pol_team, med_team, observ, turn_num + 1, index) == 'F':
                bool_check = 'F'
                return bool_check

    return bool_check


def query_if_q(pol_team, med_team, observ, turn_num, index):
    bool_check = '?'
    if turn_num == 0:
        bool_check = 'F'
        return bool_check

    if pol_team == 0:
        bool_check = 'F'
        return bool_check

    for turn in observ:
        if turn[index[0]][index[1]] == "U":
            bool_check = 'F'
            return bool_check
        elif (turn[index[0]][index[1]] == "I") and (turn < turn_num):
            bool_check = 'F'
            return bool_check
    if observ[turn_num - 1][index[0]][index[1]] == "H":
        bool_check = 'F'
        return bool_check

    if observ[turn_num - 1][index[0]][index[1]] == "S":
        count_question = count_question_mark_in_turn(observ, turn_num - 1)
        count_q = count_q_in_turn(observ, turn_num - 1)
        if pol_team >= (count_q + count_question):
            bool_check = 'T'
            return bool_check
        elif count_s_turned_into_q(observ, turn_num) == pol_team:
            bool_check = 'F'
            return bool_check

    if observ[turn_num - 1][index[0]][index[1]] == "Q":
        if observ[turn_num - 2][index[0]][index[1]] == "Q":
            bool_check = 'F'
            return bool_check
        elif observ[turn_num - 2][index[0]][index[1]] == "S":
            bool_check = 'T'
            return bool_check

    if observ[turn_num - 1][index[0]][index[1]] == "?":
        # if find_h_neihgbours(observ, turn_num, index):
        #     neighbours = find_h_neihgbours(observ, turn_num, index)
        #     for nei in neighbours:
        #         if observ[turn_num][nei[0]][nei[1]] == "H":
        #             if turn_num - 1 == 0:
        #                 bool_check = 'F'
        #                 return bool_check
        #             elif (count_q_in_turn(observ, turn_num - 1) + pol_team) == count_q_in_turn(observ, turn_num):
        #                 bool_check = 'F'
        #                 return bool_check

        if check_H_neihbours(observ, turn_num - 1, index) != 0:
            h_neighbours = check_H_neihbours(observ, turn_num - 1, index)
            for neighbour in h_neighbours:
                if observ[turn_num][neighbour[0]][neighbour[1]] != "S":
                    if turn_num - 1 == 0:
                        bool_check = 'F'
                        return bool_check
                    elif (count_q_in_turn(observ, turn_num - 1) + pol_team) == count_q_in_turn(observ, turn_num):
                        bool_check = 'F'
                        return bool_check
                elif observ[turn_num][neighbour[0]][neighbour[1]] == "S":
                    if (count_q_in_turn(observ, turn_num - 1) + pol_team) == count_q_in_turn(observ, turn_num):
                        bool_check = 'F'
                        return bool_check

    return bool_check


def query_if_i(pol_team, med_team, observ, turn_num, index):
    bool_check = '?'

    if turn_num == 0:
        bool_check = 'F'
        return bool_check

    if med_team == 0:
        bool_check = 'F'
        return bool_check

    for turn in observ:
        if turn[index[0]][index[1]] == "U":
            bool_check = 'F'
            return bool_check
    cur_turn = 0
    for turn in observ:
        if (turn[index[0]][index[1]] == "I") and (cur_turn < turn_num):
            bool_check = 'T'
            return bool_check
        elif (turn[index[0]][index[1]] != "?") and (turn[index[0]][index[1]] != "I") and (cur_turn > turn_num):
            bool_check = 'F'
            return bool_check
        if observ[turn_num - 1][index[0]][index[1]] == "H":
            count_question = count_question_mark_in_turn(observ, turn_num - 1)
            count_h = count_h_in_turn(observ, turn_num - 1)
            if med_team >= (count_h + count_question):
                bool_check = 'T'
                return bool_check
            elif med_team == (count_h_turned_into_i(observ, turn_num - 1)):
                bool_check = 'F'
                return bool_check
        cur_turn += 1

    if observ[turn_num - 1][index[0]][index[1]] == "?":
        if check_S_neihbours(observ, turn_num - 1, index) and check_S_neihbours(observ, turn_num, index):
            bool_check = 'F'
            return bool_check
        elif count_i_in_turn(observ, turn_num - 1) + med_team == count_i_in_turn(observ, turn_num):
            bool_check = 'F'
            return bool_check

    if observ[turn_num - 1][index[0]][index[1]] == "Q":
        bool_check = 'F'
        return bool_check

    return bool_check


def query_if_u(pol_team, med_team, observ, turn_num, index):
    bool_check = '?'
    for turn in observ:
        if turn[index[0]][index[1]] == "U":
            bool_check = 'T'
            return bool_check
        elif (turn[index[0]][index[1]] != "U") and (turn[index[0]][index[1]] != "?"):
            bool_check = 'F'
            return bool_check

    if (query_if_s(pol_team, med_team, observ, turn_num, index) == 'F') and (
            query_if_i(pol_team, med_team, observ, turn_num, index) == 'F') and (
            query_if_q(pol_team, med_team, observ, turn_num, index) == 'F') and (
            query_if_h(pol_team, med_team, observ, turn_num, index) == 'F'):
        bool_check = 'T'
        return bool_check

    elif (query_if_s(pol_team, med_team, observ, turn_num, index) == 'T') or (
            query_if_i(pol_team, med_team, observ, turn_num, index) == 'T') or (
            query_if_q(pol_team, med_team, observ, turn_num, index) == 'T') or (
            query_if_h(pol_team, med_team, observ, turn_num, index) == 'T'):
        bool_check = 'F'
        return bool_check

    return bool_check


def query_if_s(pol_team, med_team, observ, turn_num, index):
    bool_check = '?'
    for turn in observ:
        if turn[index[0]][index[1]] == "U":
            bool_check = 'F'
            return bool_check
        elif (turn[index[0]][index[1]] == "I") and (turn < turn_num):
            bool_check = 'F'
            return bool_check

    if pol_team == 0:
        if (turn_num <= 2) and (turn_num != 0):
            if observ[turn_num - 1][index[0]][index[1]] == "S":
                bool_check = 'T'
                return bool_check
            elif (observ[turn_num - 1][index[0]][index[1]] == "?") and (turn_num > 1):
                if observ[turn_num - 2][index[0]][index[1]] == "S":
                    bool_check = 'T'
                    return bool_check
                elif observ[turn_num - 2][index[0]][index[1]] == "?":
                    if check_H_neihbours(observ, turn_num - 2, index) != 0:
                        h_neighbours = check_H_neihbours(observ, turn_num - 2, index)
                        for neighbour in h_neighbours:
                            if observ[turn_num - 1][neighbour[0]][neighbour[1]] == "S":
                                bool_check = 'T'
                                return bool_check
                            if observ[turn_num - 1][neighbour[0]][neighbour[1]] == "H":
                                bool_check = 'F'
                                return bool_check

        if turn_num != 0:
            if observ[turn_num - 1][index[0]][index[1]] == "S":
                if observ[turn_num - 2][index[0]][index[1]] == "S":
                    if observ[turn_num - 3][index[0]][index[1]] == "S":
                        bool_check = 'F'
                        return bool_check
                    elif observ[turn_num - 3][index[0]][index[1]] == "?":
                      # if find_h_neihgbours(observ, turn_num-3, index):
                      #     neighbours = find_h_neihgbours(observ, turn_num-3, index)
                      #     for nei in neighbours:
                      #         if observ[turn_num-2][nei[0]][nei[1]] == "H":
                      #             bool_check = 'T' #because on the turn_num-3 he wasn't S so now he is
                      #             return bool_check
                      if check_H_neihbours(observ, turn_num - 3, index) != 0:
                        h_neighbours = check_H_neihbours(observ, turn_num - 3, index)
                        for neighbour in h_neighbours:
                            if observ[turn_num-2][neighbour[0]][neighbour[1]] == "S":
                                bool_check = 'F'  #because the quetion mark three turns ago was S, so now i'm H
                                return bool_check
                            elif observ[turn_num-2][neighbour[0]][neighbour[1]] == "H":
                                bool_check = 'T'
                                return bool_check
                    elif observ[turn_num - 3][index[0]][index[1]] == "H":
                        bool_check = 'T'
                        return bool_check
                elif observ[turn_num - 2][index[0]][index[1]] == "?":
                    if turn_num-3 == 0:
                        if observ[turn_num - 3][index[0]][index[1]] == "S":
                            bool_check = 'F'
                            return bool_check
                        elif observ[turn_num - 3][index[0]][index[1]] != "S" and observ[turn_num - 3][index[0]][index[1]] != "?" :
                            bool_check = 'T'
                            return bool_check
                        elif observ[turn_num - 4][index[0]][index[1]] == "S":
                            bool_check = 'T'
                            return bool_check
                        elif observ[turn_num - 3][index[0]][index[1]] == "?":
                            if observ[turn_num - 4][index[0]][index[1]] == "H":
                                bool_check = 'F'
                                return bool_check
            elif observ[turn_num - 1][index[0]][index[1]] != "S" and observ[turn_num - 1][index[0]][index[1]] != "H":
                if observ[turn_num - 1][index[0]][index[1]] == "?":
                    if observ[turn_num - 2][index[0]][index[1]] == "?":
                        # if find_h_neihgbours(observ, turn_num, index):
                        #     neighbours = find_h_neihgbours(observ, turn_num, index)
                        #     for nei in neighbours:
                        #         if observ[turn_num][nei[0]][nei[1]] == "H":
                        #             bool_check = 'F'
                        #             return bool_check
                        if check_H_neihbours(observ, turn_num - 1, index) != 0:
                            h_neighbours = check_H_neihbours(observ, turn_num - 1, index)
                            for neighbour in h_neighbours:
                                if observ[turn_num][neighbour[0]][neighbour[1]] == "S":
                                    bool_check = 'T'
                                    return bool_check
                                if observ[turn_num][neighbour[0]][neighbour[1]] == "H":
                                    bool_check = 'F'
                                    return bool_check
                    elif observ[turn_num - 2][index[0]][index[1]] == "S":
                        if observ[turn_num - 3][index[0]][index[1]] == "S":
                            if observ[turn_num - 4][index[0]][index[1]] == "S":
                                if check_S_neihbours(observ, turn_num - 1, index) and check_S_neihbours(observ,
                                                                                                        turn_num,
                                                                                                        index):
                                    bool_check = 'T'
                                    return bool_check
                                else:
                                    bool_check = 'F'
                                    return bool_check
                    elif observ[turn_num - 2][index[0]][index[1]] == "H":
                        if observ[turn_num - 3][index[0]][index[1]] == "?":
                            if check_S_neihbours(observ, turn_num-2, index) and check_S_neihbours(observ, turn_num-1, index):
                                bool_check = 'T'
                                return bool_check
                        elif observ[turn_num - 3][index[0]][index[1]] == "S":
                            bool_check = 'T'
                            return bool_check
                        elif observ[turn_num - 3][index[0]][index[1]] == "H":
                            if check_S_neihbours(observ, turn_num-3, index) and check_S_neihbours(observ, turn_num-2, index):
                                bool_check = 'T'
                                return bool_check
                            if check_S_neihbours(observ, turn_num-2, index) and check_S_neihbours(observ, turn_num-1, index):
                                bool_check = 'T'
                                return bool_check
                            else:
                                bool_check = 'F'
                                return bool_check
                        else:
                            bool_check = 'F'
                            return bool_check
                    else:
                        bool_check = 'F'
                        return bool_check
                else:
                    bool_check = 'F'
                    return bool_check

    if observ[turn_num - 1][index[0]][index[1]] == "H":
        if check_S_neihbours(observ, turn_num - 1, index):
            if check_S_neihbours(observ, turn_num, index):
                bool_check = 'T'
                return bool_check
        else:
            bool_check = 'F'
            return bool_check

    # # if find_h_neihgbours(observ, turn_num, index):
    # #     neighbours = find_h_neihgbours(observ, turn_num, index)
    # #     for nei in neighbours:
    # #         if observ[turn_num+1][nei[0]][nei[1]] == "H":
    # #             bool_check = 'F'
    # #             return bool_check

    if check_H_neihbours(observ, turn_num - 1, index) != 0:
        h_neighbours = check_H_neihbours(observ, turn_num - 1, index)
        for neighbour in h_neighbours:
            if observ[turn_num][neighbour[0]][neighbour[1]] == "S":
                bool_check = 'T'
                return bool_check
            if observ[turn_num][neighbour[0]][neighbour[1]] == "H":
                if not check_S_neihbours(observ, turn_num-1, index):
                    bool_check = 'F'
                    return bool_check

    elif pol_team != 0:
        if observ[turn_num - 1][index[0]][index[1]] == "S":
            if pol_team >= (count_s_in_turn(observ,turn_num-1) + count_question_mark_in_turn(observ, turn_num-1)):
                bool_check = 'F'
                return bool_check
            elif pol_team == count_s_turned_into_q(observ, turn_num-1):
                if turn_num >=2 :
                    bool_check = 'T'
                    return bool_check
        elif observ[turn_num - 1][index[0]][index[1]] == "H":
            if check_S_neihbours(observ, turn_num - 1, index) and check_S_neihbours(observ, turn_num, index):
                bool_check = 'T'
                return bool_check
            else:
                bool_check = 'F'
                return bool_check
        elif observ[turn_num - 1][index[0]][index[1]] == "?":
            # if find_h_neihgbours(observ, turn_num-1, index):
            #     neighbours = find_h_neihgbours(observ, turn_num-1, index)
            #     for nei in neighbours:
            #         if observ[turn_num][nei[0]][nei[1]] == "H":
            #             bool_check = 'F'
            #             return bool_check
            if check_H_neihbours(observ, turn_num - 1, index) != 0:
                h_neighbours = check_H_neihbours(observ, turn_num - 1, index)
                for neighbour in h_neighbours:
                    if observ[turn_num][neighbour[0]][neighbour[1]] == "S":
                        bool_check = 'T'
                        return bool_check
                    if observ[turn_num][neighbour[0]][neighbour[1]] == "H":
                        if not check_S_neihbours(observ, turn_num - 1, index):
                            bool_check = 'F'
                            return bool_check
            if observ[turn_num - 2][index[0]][index[1]] == "S":
                if pol_team >= (
                        count_s_in_turn(observ, turn_num - 1) + count_question_mark_in_turn(observ, turn_num - 1)):
                    bool_check = 'F'
                    return bool_check
                elif pol_team == count_s_turned_into_q(observ, turn_num - 1):
                    if turn_num >= 2:
                        bool_check = 'T'
                        return bool_check
            elif observ[turn_num - 2][index[0]][index[1]] == "H":
                if check_S_neihbours(observ, turn_num - 2, index) and check_S_neihbours(observ, turn_num-1, index):
                    #here we know that in turn = turn_num-1 we have S
                    if pol_team >= (
                            count_s_in_turn(observ, turn_num - 1) + count_question_mark_in_turn(observ, turn_num - 1)):
                        bool_check = 'F'
                        return bool_check
                    elif pol_team == count_s_turned_into_q(observ, turn_num - 1):
                        if turn_num >= 2:
                            bool_check = 'T'
                            return bool_check
                else:
                    bool_check = 'F'
                    return bool_check
            elif observ[turn_num - 2][index[0]][index[1]] == "?":
                # if find_h_neihgbours(observ, turn_num - 2, index):
                #     neighbours = find_h_neihgbours(observ, turn_num - 2, index)
                #     for nei in neighbours:
                #         if observ[turn_num-1][nei[0]][nei[1]] == "H":
                #             bool_check = 'F'
                #             return bool_check
                if check_H_neihbours(observ, turn_num - 2, index) != 0:
                    h_neighbours = check_H_neihbours(observ, turn_num - 2, index)
                    for neighbour in h_neighbours:
                        if observ[turn_num-1][neighbour[0]][neighbour[1]] == "S":
                            bool_check = 'T'
                            return bool_check
                        if observ[turn_num-1][neighbour[0]][neighbour[1]] == "H":
                            if not check_S_neihbours(observ, turn_num - 1, index):
                                bool_check = 'F'
                                return bool_check
            else:
                bool_check = 'F'
                return bool_check
        else:
            bool_check = 'F'
            return bool_check

    return bool_check


def check_S_neihbours(observ, turn_num, index):
    min_raw = 0
    min_col = 0
    max_raw = (len(observ[0]) - 1)
    max_col = (len(observ[0][0]) - 1)

    if index[0] != min_raw:
        if observ[turn_num][index[0] - 1][index[1]] == 'S':
            return True
    if index[1] != min_col:
        if observ[turn_num][index[0]][index[1] - 1] == 'S':
            return True
    if index[0] != max_raw:
        if observ[turn_num][index[0] + 1][index[1]] == 'S':
            return True
    if index[1] != max_col:
        if observ[turn_num][index[0]][index[1] + 1] == 'S':
            return True
    else:
        return False


def check_if_s_is_q(observ, turn_num, index):
    for turn in observ:
        if turn[index[0]][index[1]] == "Q":
            return True
    return False


def check_H_neihbours(observ, turn_num, index):
    min_raw = 0
    min_col = 0
    max_raw = (len(observ[0]) - 1)
    max_col = (len(observ[0][0]) - 1)
    neighbours_H = []

    if index[0] != min_raw:
        if observ[turn_num][index[0] - 1][index[1]] == 'H':
            if (not check_S_neihbours(observ, turn_num, (index[0] - 1, index[1])) or (
                    check_S_neihbours(observ, turn_num, (index[0] - 1, index[1])) and check_if_s_is_q(observ, turn_num,
                                                                                   (index[0] - 1, index[1])))):
                neighbours_H.append((index[0] - 1, index[1]))
    if index[1] != min_col:
        if observ[turn_num][index[0]][index[1] - 1] == 'H':
            if (not check_S_neihbours(observ, turn_num, (index[0], index[1] - 1)) or (
                    check_S_neihbours(observ, turn_num,
                                      (index[0], index[1] - 1)) and check_if_s_is_q(observ, turn_num,
                                                                                   (index[0], index[1] - 1)))):
                neighbours_H.append((index[0], index[1] - 1))
    if index[0] != max_raw:
        if observ[turn_num][index[0] + 1][index[1]] == 'H':
            if (not check_S_neihbours(observ, turn_num, (index[0] + 1, index[1])) or (
                    check_S_neihbours(observ, turn_num,
                                      (index[0] + 1, index[1])) and check_if_s_is_q(observ, turn_num,
                                                                                   (index[0] + 1, index[1])))):
                neighbours_H.append((index[0] + 1, index[1]))
    if index[1] != max_col:
        if observ[turn_num][index[0]][index[1] + 1] == 'H':
            if (not check_S_neihbours(observ, turn_num, (index[0], index[1] + 1)) or (
                    check_S_neihbours(observ, turn_num,
                                      (index[0], index[1] + 1)) and check_if_s_is_q(observ, turn_num,
                                                                                   (index[0], index[1] + 1)))):
                neighbours_H.append((index[0], index[1] + 1))
    if len(neighbours_H) != 0:
        return neighbours_H
    else:
        return 0

def find_h_neihgbours(observ, turn_num, index):
    min_raw = 0
    min_col = 0
    max_raw = (len(observ[0]) - 1)
    max_col = (len(observ[0][0]) - 1)
    neighbours_H = []

    if index[0] != min_raw:
        if observ[turn_num][index[0] - 1][index[1]] == 'H':
            neighbours_H.append((index[0] - 1, index[1]))
    if index[1] != min_col:
        if observ[turn_num][index[0]][index[1] - 1] == 'H':
            neighbours_H.append((index[0], index[1] - 1))
    if index[0] != max_raw:
        if observ[turn_num][index[0] + 1][index[1]] == 'H':
            neighbours_H.append((index[0] + 1, index[1]))
    if index[1] != max_col:
        if observ[turn_num][index[0]][index[1] + 1] == 'H':
            neighbours_H.append((index[0], index[1] + 1))

    if len(neighbours_H) != 0:
        return neighbours_H
    else:
        return False


def count_s_in_turn(observ, turn_num):
    count_s = 0
    cur_turn = 0
    for turn in observ:
        if cur_turn == turn_num:
            for line in turn:
                for letter in line:
                    if letter == "S":
                        count_s += 1
        cur_turn += 1
    return count_s


def count_h_in_turn(observ, turn_num):
    count_h = 0
    cur_turn = 0
    for turn in observ:
        if cur_turn == turn_num:
            for line in turn:
                for letter in line:
                    if letter == "H":
                        count_h += 1
        cur_turn += 1
    return count_h


def count_i_in_turn(observ, turn_num):
    count_i = 0
    cur_turn = 0
    for turn in observ:
        if cur_turn == turn_num:
            for line in turn:
                for letter in line:
                    if letter == "I":
                        count_i += 1
        cur_turn += 1
    return count_i


def count_q_in_turn(observ, turn_num):
    count_q = 0
    cur_turn = 0
    for turn in observ:
        if cur_turn == turn_num:
            for line in turn:
                for letter in line:
                    if letter == "Q":
                        count_q += 1
        cur_turn += 1
    return count_q


def count_question_mark_in_turn(observ, turn_num):
    count_question = 0
    cur_turn = 0
    for turn in observ:
        if cur_turn == turn_num:
            for line in turn:
                for letter in line:
                    if letter == "?":
                        count_question += 1
        cur_turn += 1

    return count_question


def count_h_turned_into_i(observ, turn_num):
    count = 0
    cur_turn = 0
    line_num = 0
    letter_num = 0
    for turn in observ:
        if cur_turn == turn_num:
            for line in turn:
                for letter in line:
                    if letter == "H":
                        if check_if_letter_i(observ, turn_num + 1, (line_num, letter_num)):
                            count += 1
                    letter_num += 1
                line_num += 1
        cur_turn += 1
    return count


def check_if_letter_i(observ, turn_num, index):
    cur_turn = 0
    line_num = 0
    letter_num = 0
    for turn in observ:
        if cur_turn == turn_num:
            for line in turn:
                if line_num == index[0]:
                    for letter in line:
                        if letter_num == index[1]:
                            if letter == "I":
                                return True
                            else:
                                return False
                        letter_num += 1
                line_num += 1
        cur_turn += 1

def count_s_turned_into_q(observ, turn):
    count = 0
    for line in observ[turn]:
        for letter in observ[turn][line]:
            if letter == "S":
                if observ[turn + 1][line][letter] == "Q":
                    count += 1
    return count


def solve_problem(input):
    Dict = {}
    pol_team = input["police"]
    med_team = input["medics"]
    observ = input["observations"]
    queries = input["queries"]
    for query_number in queries:
        index = query_number[0]
        turn_num = query_number[1]
        letter = query_number[2]
        bool_check = '?'
        if letter == 'H':
            bool_check = query_if_h(pol_team, med_team, observ, turn_num, index)
        if letter == 'S':
            bool_check = query_if_s(pol_team, med_team, observ, turn_num, index)
        if letter == 'I':
            bool_check = query_if_i(pol_team, med_team, observ, turn_num, index)
        if letter == 'U':
            bool_check = query_if_u(pol_team, med_team, observ, turn_num, index)
        if letter == 'Q':
            bool_check = query_if_q(pol_team, med_team, observ, turn_num, index)
        Dict[query_number] = bool_check
    return Dict
