import logic
import utils

ids = ['305276693']


def list_negations(tag, i, j, time, tag_list):
    new_tag_list = [x for x in tag_list if x != tag]
    negtions_list = []
    for x in new_tag_list:
        negtions_list.append(("~{}{}{}{}".format(x, i, j, time)))

    return negtions_list


def solve_problem(input):
    police = input['police']
    medics = input['medics']

    covid_kb = logic.PropKB()

    tag_list = ['H', 'S', 'U']

    if police or medics:
        return 'Sorry, simulation for teams is not available'

    row_num = len(input['observations'][0])
    col_num = len(input['observations'][0][0])
    time_frame = len(input['observations'])
    clause_list = []
    time = 0
    for obs in input['observations']:
        for i in range(row_num):
            for j in range(col_num):
                for tag in tag_list:
                    var = "{}{}{}{}".format(tag, i, j, time)

                    if tag == obs[i][j]:
                        covid_kb.tell(utils.expr(var))
                    elif tag != '?':
                        negate_var = '~' + var
                        covid_kb.tell(utils.expr(negate_var))

                clause_list.append("H{row}{col}{curr} <=> (~S{row}{col}{curr} & ~U{row}{col}{curr})".format(
                    row=i, col=j, curr=time))
                clause_list.append("S{row}{col}{curr} <=> (~H{row}{col}{curr} & ~U{row}{col}{curr})".format(
                    row=i, col=j, curr=time))
                clause_list.append("U{row}{col}{curr} <=> (~H{row}{col}{curr} & ~S{row}{col}{curr})".format(
                    row=i, col=j, curr=time))

                if time > 2:
                    clause_list.append(
                        "S{row}{col}{curr} ==> ((S{row}{col}{prev1} & S{row}{col}{prev2} & H{row}{col}{prev3})"
                        "| (S{row}{col}{prev1} & H{row}{col}{prev2}) | (H{row}{col}{prev1}))".format(
                            row=i, col=j, curr=time, prev1=time - 1, prev2=time - 2, prev3=time - 3))

                if 0 < time < time_frame - 2:
                    clause_list.append(
                        "(H{row}{col}{prev} & S{row}{col}{curr}) ==> (S{row}{col}{next1} & S{row}{col}{next2} & H{row}{col}{next3})".format(
                            row=i, col=j, prev=time - 1, curr=time, next1=time + 1, next2=time + 2, next3=time + 3))

                if time < time_frame:
                    clause_list.append(
                        "U{row}{col}{curr} <=> U{row}{col}{next}".format(row=i, col=j, curr=time, next=time + 1))
                    if i == 0:
                        if j == 0:
                            clause_list.append(
                                "(~S{under}{col}{curr} & ~S{row}{right}{curr} & H{row}{col}{curr}) <=> H{row}{col}{next}".format(
                                    row=i, col=j, curr=time, under=i + 1, right=j + 1, next=time + 1))
                        elif j == col_num - 1:
                            clause_list.append(
                                "(~S{under}{col}{curr} & ~S{row}{left}{curr} & H{row}{col}{curr}) <=> H{row}{col}{next}".format(
                                    row=i, col=j, curr=time, under=i + 1, left=j - 1, next=time + 1))
                        else:
                            clause_list.append(
                                "(~S{under}{col}{curr} & ~S{row}{right}{curr} & ~S{row}{left}{curr} & H{row}{col}{curr}) <=> H{row}{col}{next}".format(
                                    row=i, col=j, curr=time, under=i + 1, right=j + 1, left=j - 1, next=time + 1))
                    elif i == row_num - 1:
                        if j == 0:
                            clause_list.append(
                                "(~S{over}{col}{curr} & ~S{row}{right}{curr} & H{row}{col}{curr}) <=> H{row}{col}{next}".format(
                                    row=i, col=j, curr=time, over=i - 1, right=j + 1, next=time + 1))
                        elif j == col_num - 1:
                            clause_list.append(
                                "(~S{over}{col}{curr} & ~S{row}{left}{curr} & H{row}{col}{curr}) <=> H{row}{col}{next}".format(
                                    row=i, col=j, curr=time, over=i - 1, left=j - 1, next=time + 1))
                        else:
                            clause_list.append(
                                "((~S{over}{col}{curr}) & (~S{row}{right}{curr}) & (~S{row}{left}{curr}) & (H{row}{col}{curr})) <=> H{row}{col}{next}".format(
                                    row=i, col=j, curr=time, over=i - 1, right=j + 1, left=j - 1, next=time + 1))
                    elif j == 0:
                        clause_list.append(
                            "(~S{over}{col}{curr} & ~S{row}{right}{curr} & ~S{under}{col}{curr} & H{row}{col}{curr}) <=> H{row}{col}{next}".format(
                                row=i, col=j, curr=time, over=i - 1, right=j + 1, under=i + 1, next=time + 1))
                    elif j == col_num - 1:
                        clause_list.append(
                            "(~S{over}{col}{curr} & ~S{row}{left}{curr} & ~S{under}{col}{curr} & H{row}{col}{curr}) <=> H{row}{col}{next}".format(
                                row=i, col=j, curr=time, over=i - 1, left=j - 1, under=i + 1, next=time + 1))
                    else:
                        clause_list.append(
                            "(~S{over}{col}{curr} & ~S{row}{left}{curr} & ~S{row}{right}{curr} & ~S{under}{col}{curr} & H{row}{col}{curr}) <=> H{row}{col}{next}".format(
                                row=i, col=j, curr=time, over=i - 1, left=j - 1, right=j + 1, under=i + 1,
                                next=time + 1))

        time += 1

    for clause in clause_list:
        covid_kb.tell(utils.expr(clause))

    answer_dict = {}
    for query in input['queries']:
        ((i, j), t, slot) = query
        if slot == "Q" or slot == "I":
            answer_dict.update({query: 'F'})
            continue

        alpha = utils.expr("{}{}{}{}".format(slot, i, j, t))
        negate_alpha = utils.expr("~{}{}{}{}".format(slot, i, j, t))

        if logic.pl_resolution(covid_kb, alpha):
            answer_dict.update({query: 'T'})
        elif logic.pl_resolution(covid_kb, negate_alpha):
            answer_dict.update({query: 'F'})
        else:
            answer_dict.update({query: '?'})

    return answer_dict






