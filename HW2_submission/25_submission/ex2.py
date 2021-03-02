from pysat.solvers import Minisat22
ids = ['209294503', '316597574']
def neighbors(x, y, m, n):
    l = []
    if x > 0:
        l.append(tuple([x - 1, y]))
    if x < m - 1:
        l.append(tuple([x + 1, y]))
    if y > 0:
        l.append(tuple([x, y - 1]))
    if y < n - 1:
        l.append(tuple([x, y + 1]))
    return l


def solve_problem(input):
    police = input['police']

    actions_police = []
    i = 1
    for p in range(police):
        actions_police.append('P' + str(i))
        i += 1

    medics = input['medics']
    actions_medics = []
    j = 1
    for m in range(medics):
        actions_medics.append('M' + str(j))
        j += 1

    states = {}
    for turn in range(len(input['observations'])):
        states[turn] = input['observations'][turn]

    KB = []

    r = len(states[0])
    c = len(states[0][0])
    state_p = ['U', 'H', 'S', '?', 'Q', 'I']
    max_turns = len(input['observations'])
    p = {}
    inital_state = []
    max_index = 1
    dict_p_to_int = {}
    all_p_a = {}

    for turn in range(max_turns):
        p_0 = []
        for i in range(r):
            for j in range(c):
                inital_state.append(tuple([tuple([i, j]), turn, states[turn][i][j]]))
                for state in state_p:
                    p_0.append(tuple([tuple([i, j]), turn, state]))
                    dict_p_to_int[tuple([tuple([i, j]), turn, state])] = max_index
                    all_p_a[tuple([tuple([i, j]), turn, state])] = max_index
                    if tuple([tuple([i, j]), turn, state]) in inital_state:
                        KB.append([max_index])
                    else:
                        if tuple([tuple([i, j]), turn, '?']) not in inital_state:
                            KB.append([-1 * max_index])
                    max_index += 1
        p[turn] = p_0

    all_actions={}
    # add actions to dict_p_to_int
    for turn in range(max_turns):
        for i in range(r):
            for j in range(c):
                for ac1 in actions_police:
                    max_index = max_index + 1
                    dict_p_to_int[tuple([tuple([i, j]), turn, ac1])] = max_index
                    all_p_a[tuple([tuple([i, j]), turn, ac1])] = max_index
                    all_actions[tuple([tuple([i, j]), turn, ac1])] = max_index

                for ac2 in actions_medics:
                    max_index = max_index + 1
                    dict_p_to_int[tuple([tuple([i, j]), turn, ac2])] = max_index
                    all_p_a[tuple([tuple([i, j]), turn, ac2])] = max_index
                    all_actions[tuple([tuple([i, j]), turn, ac2])] = max_index

    # S -> ~H,~I,~Q,~U
    for turn in range(max_turns):
        for i in range(r):
            for j in range(c):
                x1 = dict_p_to_int[tuple([tuple([i, j]), turn, 'Q'])]
                x2 = dict_p_to_int[tuple([tuple([i, j]), turn, 'H'])]
                x3 = dict_p_to_int[tuple([tuple([i, j]), turn, 'I'])]
                x4 = dict_p_to_int[tuple([tuple([i, j]), turn, 'S'])]
                x5 = dict_p_to_int[tuple([tuple([i, j]), turn, 'U'])]
                x6 = dict_p_to_int[tuple([tuple([i, j]), turn, '?'])]

                for s in state_p:
                    if s == 'Q':
                        KB.extend([[-1 * x1, -1 * x2],[ -1 * x1,-1 * x3], [-1 * x1,-1 * x4], [-1 * x1,-1 * x5]])
                    if s == 'H':
                        KB.extend([[-1 * x2, -1 * x1], [-1 * x2, -1 * x3], [-1 * x2, -1 * x4], [-1 * x2, -1 * x5]])
                    if s == 'I':
                        KB.extend([[-1 * x3, -1 * x1], [-1 * x3, -1 * x2], [-1 * x3, -1 * x4], [-1 * x3, -1 * x5]])
                    if s == 'S':
                        KB.extend([[-1 * x4, -1 * x1], [-1 * x4, -1 * x2], [-1 * x4, -1 * x3], [-1 * x4, -1 * x5]])
                    if s == 'U':
                        KB.extend([[-1 * x5, -1 * x1], [-1 * x5, -1 * x2], [-1 * x5, -1 * x3], [-1 * x5, -1 * x4]])
                    if s == '?':
                        KB.append([-1 * x6, x1, x2, x3, x4, x5])
   # KB.append(["S -> ~H,~I,~Q,~U Done"])

    goals = input['queries']

    add_effect_all_actions = {}
    for action in actions_police:
        for turn in range(max_turns):
            for i in range(r):
                for j in range(c):

                    add = []
                    if turn + 1 < max_turns:
                        Q1 = dict_p_to_int[tuple([tuple([i, j]), turn + 1, 'Q'])]
                        add.append(Q1)
                    elif turn + 2 <= max_turns:
                        Q2 = dict_p_to_int[tuple([tuple([i, j]), turn + 2, 'Q'])]
                        add.append(Q2)
                    elif turn + 3 <= max_turns:
                        H3 = dict_p_to_int[tuple([tuple([i, j]), turn + 3, 'H'])]
                        add.append(H3)
                    add_effect_all_actions[max_index] = add
                    # {~a_t,p_t}
                    a_t = dict_p_to_int[tuple([tuple([i, j]), turn, action])]
                    p_t = dict_p_to_int[tuple([tuple([i, j]), turn, 'S'])]
                    KB.append([-1 * a_t, p_t])
    #KB.append(["-1 * a_t, p_t police Done"])

    for action in actions_medics:
        for turn in range(max_turns):
            for i in range(r):
                for j in range(c):

                    if turn + 1 <= max_turns:
                        add_effect_all_actions[max_index] = [tuple([tuple([i, j]), turn + 1, 'I'])]
                    # {~a_t,p_t}
                    a_t = dict_p_to_int[tuple([tuple([i, j]), turn, action])]
                    p_t = dict_p_to_int[tuple([tuple([i, j]), turn, 'H'])]
                    KB.append([-1 * a_t, p_t])
    #KB.append(["-1 * a_t, p_t med Done"])

    # don't apply interfering actions at the same time
    # {~a_t,a_t'}

# apply one action once each turn
    for ac in actions_medics:
        for turn in range(max_turns):
            for i in range(r):
                for j in range(c):
                    x1=dict_p_to_int[tuple([tuple([i,j]), turn, ac])]
                    for i_1 in range(r):
                        for j_1 in range(c):
                            if i !=i_1 and j != j_1:
                                x2=dict_p_to_int[tuple([tuple([i_1,j_1]), turn, ac])]
                                KB.append([-1*x1,-1*x2])

    for ac in actions_police:
        for turn in range(max_turns):
            for i in range(r):
                for j in range(c):
                    x1=dict_p_to_int[tuple([tuple([i,j]), turn, ac])]
                    for i_1 in range(r):
                        for j_1 in range(c):
                            if i !=i_1 and j != j_1:
                                x2=dict_p_to_int[tuple([tuple([i_1,j_1]), turn, ac])]
                                KB.append([-1*x1,-1*x2])

# apply action if can

    for ac in actions_medics:
        for turn in range(max_turns):
            l1=[]
            for i in range(r):
                for j in range(c):
                    l1.append(dict_p_to_int[tuple([tuple([i,j]), turn,ac])])
            KB.append(l1)

    for ac in actions_police:
        for turn in range(max_turns):
            l1=[]
            for i in range(r):
                for j in range(c):
                    l1.append(dict_p_to_int[tuple([tuple([i,j]), turn,ac])])
            KB.append(l1)


    # fact implies disjunction of its achevers
    # {~p_t} or {a_(t-1)|p in add(a)}
    if len(all_actions) != 0:
        for p, v1 in dict_p_to_int.items():
            l = [-1 * v1]
            for action, v2 in add_effect_all_actions.items():
                if v1 in v2:
                    l.append(action)
            if len(l)>1:
                KB.append(l)

    for turn in range(1, max_turns):
        for key, v in dict_p_to_int.items():
            ######### U ###########
            if turn != key[1]:
                continue
            if key[2] == 'U':
                KB.append([-1 * v ,dict_p_to_int[tuple([key[0], key[1] - 1, key[2]])]])
            ######### I ###########
            if key[2] == 'I':
                l2 = [v * -1]
                if len(actions_medics)>0:
                    if turn + 1 < max_turns:
                        KB.append([-1 * v, dict_p_to_int[tuple([key[0], key[1] + 1, key[2]])]])

                    for i in range(turn):
                        for ac in actions_medics:
                            l2.append(dict_p_to_int[tuple([key[0], i, ac])])
                KB.append(l2)

            ######### ? ###########
            if key[2] == '?':
                x1 = v
                x2 = dict_p_to_int[tuple([key[0], key[1], 'H'])]
                x3 = dict_p_to_int[tuple([key[0], key[1] , 'U'])]
                x4 = dict_p_to_int[tuple([key[0], key[1], 'S'])]
                x5 = dict_p_to_int[tuple([key[0], key[1], 'I'])]
                x6 = dict_p_to_int[tuple([key[0], key[1] , 'Q'])]
                KB.append([-1*x1,x2,x3,x4,x5,x6])


            ######### H ###########
            if key[2] == 'H':
                x1 = v
                x2 = dict_p_to_int[tuple([key[0], key[1] - 1, key[2]])]  # H in i-1
                N = neighbors(key[0][0], key[0][1], r, c)

                ############# turn < 3 ############

                if turn < 3:
                    if len(N) == 1:
                        x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                        # (x2 | ~x1) & (~x1 | ~x3)
                        KB.extend([[x2, -1 * x1], [-1 * x1, -1 * x3]])  # x1-> x2 & ~x3
                    elif len(N) == 2:
                        x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                        x4 = dict_p_to_int[tuple([N[1], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                        # (x2 | ~x1) & (~x1 | ~x3) & (~x1 | ~x4)
                        KB.extend([[x2, -1 * x1], [-1 * x1, -1 * x3], [-1 * x1, -1 * x4]])  # x1-> x2 & ~x3 & ~x4
                    elif len(N) == 3:
                        x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                        x4 = dict_p_to_int[tuple([N[1], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                        x5 = dict_p_to_int[tuple([N[2], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                        # (x2 | ~x1) & (~x1 | ~x3) & (~x1 | ~x4) & (~x1 | ~x5)
                        KB.extend([[x2, -1 * x1], [-1 * x1, -1 * x3], [-1 * x1, -1 * x4],
                                   [-1 * x1, -1 * x5]])  # x1-> x2 & ~x3 & ~x4 & ~x5
                    else:
                        x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                        x4 = dict_p_to_int[tuple([N[1], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                        x5 = dict_p_to_int[tuple([N[2], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor3 was S
                        x6 = dict_p_to_int[tuple([N[3], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor4 was S
                        # (x2 | ~x1) & (~x1 | ~x3) & (~x1 | ~x4) & (~x1 | ~x5) & (~x1 | ~x6)
                        KB.extend([[x2, -1 * x1], [-1 * x1, -1 * x3], [-1 * x1, -1 * x4], [-1 * x1, -1 * x5],
                                   [-1 * x1, -1 * x6]])  # x1-> x2 & ~x3 & ~x4 & ~x5

                ########## turn >= 3 ##########

                else:
                    # i was sick for 3 turns
                    x7 = dict_p_to_int[tuple([key[0], key[1] - 1, 'S'])]
                    x8 = dict_p_to_int[tuple([key[0], key[1] - 2, 'S'])]
                    x9 = dict_p_to_int[tuple([key[0], key[1] - 3, 'S'])]

                    if police>0:
                        # i was in quarantine for 2 turns
                        x10 = dict_p_to_int[tuple([key[0], key[1] - 1, 'Q'])]
                        x11 = dict_p_to_int[tuple([key[0], key[1] - 2, 'Q'])]

                        if len(N) == 1:
                            x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                            # x1-> (x2 & ~x3) or (x7 & x8 & x9) or (x10 & x11)
                            KB.extend([[x10, x2, x7, -1 * x1], [x10, x2, x8, -1 * x1],
                                    [x10, x2, x9, -1 * x1], [x11, x2, x7, -1 * x1],
                                    [x11, x2, x8, ~x1], [x11, x2, x9, -1 * x1],
                                    [x10, x7, -1 * x1, -1 * x3], [x10, x8, -1 * x1, -1 * x3],
                                    [x10, x9, -1 * x1, -1 * x3], [x11, x7, -1 * x1, -1 * x3],
                                    [x11, x8, ~x1, -1 * x3], [x11, x9, -1 * x1, -1 * x3]])
                        elif len(N) == 2:
                            x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                            x4 = dict_p_to_int[tuple([N[1], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                            # x1-> (x2 & ~x3 & ~x4 )or (x7 & x8 & x9) or (x10 & x11)

                            KB.extend([[x10, x2, x7, -1 * x1], [x10, x2, x8, -1 * x1], [x10, x2, x9, -1 * x1],
                                    [x11, x2, x7, -1 * x1], [x11, x2, x8, -1 * x1], [x11, x2, x9, -1 * x1],
                                    [x10, x7, -1 * x1, -1 * x3], [x10, x7, -1 * x1, -1 * x4],
                                    [x10, x8, -1 * x1, -1 * x3],
                                    [x10, x8, -1 * x1, -1 * x4], [x10, x9, -1 * x1, -1 * x3],
                                    [x10, x9, -1 * x1, -1 * x4],
                                    [x11, x7, -1 * x1, -1 * x3], [x11, x7, -1 * x1, -1 * x4],
                                    [x11, x8, -1 * x1, -1 * x3],
                                    [x11, x8, -1 * x1, -1 * x4], [x11, x9, -1 * x1, -1 * x3], [x11, x9, ~x1, -1 * x4]])
                        elif len(N) == 3:
                            x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                            x4 = dict_p_to_int[tuple([N[1], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                            x5 = dict_p_to_int[tuple([N[2], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                            # x1-> (x2 & ~x3 & ~x4 & ~x5 )or (x7 & x8 & x9) or (x10 & x11)

                            KB.extend([[x10, x2, x7, -1 * x1], [x10, x2, x8, -1 * x1], [x10, x2, x9, -1 * x1],
                                    [x11, x2, x7, -1 * x1], [x11, x2, x8, -1 * x1], [x11, x2, x9, -1 * x1],
                                    [x10, x7, -1 * x1, ~x3], [x10, x7, -1 * x1, -1 * x4], [x10, x7, -1 * x1, -1 * x5],
                                    [x10, x8, -1 * x1, -1 * x3], [x10, x8, -1 * x1, -1 * x4],
                                    [x10, x8, -1 * x1, -1 * x5],
                                    [x10, x9, -1 * x1, -1 * x3], [x10, x9, -1 * x1, -1 * x4],
                                    [x10, x9, -1 * x1, -1 * x5],
                                    [x11, x7, -1 * x1, -1 * x3], [x11, x7, -1 * x1, -1 * x4],
                                    [x11, x7, -1 * x1, -1 * x5],
                                    [x11, x8, -1 * x1, -1 * x3], [x11, x8, -1 * x1, -1 * x4],
                                    [x11, x8, -1 * x1, -1 * x5],
                                    [x11, x9, -1 * x1, -1 * x3], [x11, x9, -1 * x1, -1 * x4],
                                    [x11, x9, -1 * x1, -1 * x5]])
                        else:
                            # x1-> (x2 & ~x3 & ~x4 & ~x5 & ~x6 )or (x7 & x8 & x9) or (x10 & x11)
                            x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                            x4 = dict_p_to_int[tuple([N[1], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                            x5 = dict_p_to_int[tuple([N[2], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor3 was S
                            x6 = dict_p_to_int[tuple([N[3], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor4 was S

                            KB.extend([[x10, x2, x7, -1 * x1], [x10, x2, x8, -1 * x1], [x10, x2, x9, -1 * x1],
                                    [x11, x2, x7, -1 * x1], [x11, x2, x8, -1 * x1], [x11, x2, x9, -1 * x1],
                                    [x10, x7, -1 * x1, -1 * x3], [x10, x7, -1 * x1, -1 * x4],
                                    [x10, x7, -1 * x1, -1 * x5],
                                    [x10, x7, ~x1, -1 * x6], [x10, x8, -1 * x1, -1 * x3], [x10, x8, -1 * x1, -1 * x4],
                                    [x10, x8, -1 * x1, -1 * x5], [x10, x8, -1 * x1, -1 * x6],
                                    [x10, x9, -1 * x1, -1 * x3],
                                    [x10, x9, -1 * x1, -1 * x4], [x10, x9, -1 * x1, -1 * x5],
                                    [x10, x9, -1 * x1, -1 * x6],
                                    [x11, x7, -1 * x1, -1 * x3], [x11, x7, -1 * x1, -1 * x4],
                                    [x11, x7, -1 * x1, -1 * x5],
                                    [x11, x7, -1 * x1, -1 * x6], [x11, x8, -1 * x1, -1 * x3],
                                    [x11, x8, -1 * x1, -1 * x4],
                                    [x11, x8, -1 * x1, -1 * x5], [x11, x8, -1 * x1, -1 * x6],
                                    [x11, x9, -1 * x1, -1 * x3],
                                    [x11, x9, -1 * x1, -1 * x4], [x11, x9, -1 * x1, -1 * x5],
                                    [x11, x9, -1 * x1, -1 * x6]])
                    else:
                        if len(N) == 1:
                            x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                            # x1-> (x2 & ~x3) or (x7 & x8 & x9)
                            KB.extend([[x2, x7, -1 * x1], [x2, x8, -1 * x1], [x2, x9, -1 * x1], [x7, -1 * x1, ~x3],
                                       [x8, -1 * x1, -1 * x3], [x9, -1 * x1, -1 * x3]])
                        elif len(N) == 2:
                            x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                            x4 = dict_p_to_int[tuple([N[1], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                            # x1-> (x2 & ~x3 & ~x4 )or (x7 & x8 & x9)

                            KB.extend([[x2 , x7 , -1*x1] , [x2 , x8 , -1*x1] , [x2 , x9 , -1*x1] , [x7 , -1*x1 , -1*x3] ,
                                       [x7 , -1*x1 , -1*x4] , [x8 , -1*x1 , -1*x3] , [x8 , -1*x1 , -1*x4] ,
                                       [x9 , -1*x1 , -1*x3] , [x9 , -1*x1 , -1*x4]])

                        elif len(N) == 3:
                            x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                            x4 = dict_p_to_int[tuple([N[1], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                            x5 = dict_p_to_int[tuple([N[2], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                            # x1-> (x2 & ~x3 & ~x4 & ~x5 )or (x7 & x8 & x9)
                            KB.extend([[x2 , x7 , -1*x1] , [x2 , x8 , -1*x1] , [x2 , x9 , -1*x1] , [x7 , -1*x1 , -1*x3] ,
                                       [x7 , -1*x1 , -1*x4] , [x7 , -1*x1 , -1*x5] , [x8 , -1*x1 , -1*x3] , [x8 , -1*x1 , -1*x4] ,
                                       [x8 , -1*x1 , -1*x5] , [x9 , -1*x1 , -1*x3] , [x9 , -1*x1 , -1*x4] , [x9 , -1*x1 , -1*x5]])
                        else:
                            # x1-> (x2 & ~x3 & ~x4 & ~x5 & ~x6 )or (x7 & x8 & x9)
                            x3 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                            x4 = dict_p_to_int[tuple([N[1], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor2 was S
                            x5 = dict_p_to_int[tuple([N[2], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor3 was S
                            x6 = dict_p_to_int[tuple([N[3], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor4 was S

                            KB.extend([[x2 , x7 , -1*x1] , [x2 , x8 , -1*x1] , [x2 , x9 , -1*x1] , [x7 , -1*x1 , -1*x3] ,
                                       [x7 , -1*x1 , -1*x4] , [x7 , -1*x1 , -1*x5] , [x7 , -1*x1 , -1*x6 ],
                                       [x8 , -1*x1 , -1*x3] , [x8 , -1*x1 , -1*x4] , [x8 , -1*x1 , -1*x5] ,
                                       [x8 , -1*x1 , -1*x6] , [x9 , -1*x1 , -1*x3] , [x9 , -1*x1 , -1*x4] ,
                                       [x9 , -1*x1 , -1*x5] , [x9 , -1*x1 , -1*x6]])
                #KB.append(["H Done"])

            ######### S ###########
            if key[2] == 'S':
                x1 = v
                x2 = dict_p_to_int[tuple([key[0], key[1] - 1, key[2]])]  # i was S in the last turn (i-1)
                x3 = dict_p_to_int[tuple([key[0], key[1] - 1, 'H'])]  # i was H in the last turn (i-1)
                N = neighbors(key[0][0], key[0][1], r, c)

                ###### turn < 3 #####

                if len(N) == 1:
                    # x1 -> (x2) or (x3 and x4)
                    x4 = dict_p_to_int[tuple([N[0], key[1] - 1, 'S'])]  # in i-1 :i was  H , my neighbor1 was S
                    KB.extend([[x2, x3, -1 * x1], [x2, x4, -1 * x1]])


                elif (len(N) == 2):
                    # x1 -> (x2) or ((x3 and x4) or (x3 and x5))
                    x4 = dict_p_to_int[tuple([N[0], key[1] - 1, key[2]])]  # in i-1 :i was  H , my neighbor1 was S
                    x5 = dict_p_to_int[tuple([N[1], key[1] - 1, key[2]])]  # in i-1 :i was  H , my neighbor2 was S
                    KB.extend([[x2, x3, -1 * x1], [x2, x3, x4, -1 * x1], [x2, x3, x5, -1 * x1], [x2, x4, x5, -1 * x1]])


                elif (len(N) == 3):
                    # x1 -> (x2) or ((x3 and x4) or (x3 and x5) or (x3 and x6)
                    x4 = dict_p_to_int[tuple([N[0], key[1] - 1, key[2]])]  # in i-1 :i was  H , my neighbor1 was S
                    x5 = dict_p_to_int[tuple([N[1], key[1] - 1, key[2]])]  # in i-1 :i was  H , my neighbor2 was S
                    x6 = dict_p_to_int[tuple([N[2], key[1] - 1, key[2]])]  # in i-1 :i was  H , my neighbor3 was S
                    KB.extend([[x2, x3, -1 * x1], [x2, x3, x4, -1 * x1], [x2, x3, x5, -1 * x1], [x2, x3, x6, -1 * x1],
                             [x2, x3, x4, x5, -1 * x1], [x2, x3, x4, x6, -1 * x1], [x2, x3, x5, x6, -1 * x1],
                             [x2, x4, x5, x6, -1 * x1]])

                else:
                    # x1 -> (x2) or ((x3 and x4) or (x3 and x4) or (x3 and x5) or (x3 and x6)
                    x4 = dict_p_to_int[tuple([N[0], key[1] - 1, key[2]])]  # in i-1 :i was  H , my neighbor1 was S
                    x5 = dict_p_to_int[tuple([N[1], key[1] - 1, key[2]])]  # in i-1 :i was  H , my neighbor2 was S
                    x6 = dict_p_to_int[tuple([N[2], key[1] - 1, key[2]])]  # in i-1 :i was  H , my neighbor3 was S
                    x7 = dict_p_to_int[tuple([N[3], key[1] - 1, key[2]])]  # in i-1 :i was  H , my neighbor4 was S
                    KB.extend([[x2, x3, -1 * x1], [x2, x3, x4, -1 * x1], [x2, x3, x5, -1 * x1], [x2, x3, x6, -1 * x1],
                             [x2, x3, x7, -1 * x1], [x2, x3, x4, x5, -1 * x1], [x2, x3, x4, x6, -1 * x1],
                             [x2, x3, x4, x7, -1 * x1], [x2, x3, x5, x6, -1 * x1], [x2, x3, x5, x7, -1 * x1],
                             [x2, x3, x6, x7, -1 * x1], [x2, x3, x4, x5, x6, -1 * x1], [x2, x3, x4, x5, x7, -1 * x1],
                             [x2, x3, x4, x6, x7, -1 * x1], [x2, x3, x5, x6, x7, -1 * x1],
                             [x2, x4, x5, x6, x7, -1 * x1]])

                if turn >2 and turn+1 < max_turns:
                    x1=v
                    x2=dict_p_to_int[tuple([key[0], key[1] - 1, key[2]])]
                    x3 = dict_p_to_int[tuple([key[0], key[1] - 2, key[2]])]
                    x4=dict_p_to_int[tuple([key[0], key[1] +1 , "H"])]
                    KB.append([x4 , -1*x1 , -1*x2 , -1*x3])

    ######### Q ###########
            if key[2] == 'Q':
                l2=[v*-1]
                if len(actions_police)>0:
                    for action in actions_police:
                        l2.append(dict_p_to_int[tuple([key[0], key[1] - 1, action])])
                        if turn>2:
                            l2.append(dict_p_to_int[tuple([key[0], key[1] - 2, action])])
                KB.append(l2)
    result={}
    with Minisat22(bootstrap_with=KB) as m:
        for q in goals:
            r1=m.solve(assumptions=[dict_p_to_int[q]])
            r2=m.solve(assumptions=[-1*dict_p_to_int[q]])
            if r1==False:
                result[q] = 'F'
            elif  r1 == r2:
                result[q] = '?'
            else:
                result[q] = 'T'
    return result