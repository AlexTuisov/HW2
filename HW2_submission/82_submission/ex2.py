import itertools
import copy

ids = ['321019879', '307916346']

level = {}
global n_police, n_medics, queries, observe

class Node:
    def __init__(self, map, time_map, father, level):
        self.map = map
        self.time_map = time_map
        self.father = father
        self.sons = []
        self.level = level

    def print(self):
        print(self)
        for i in range(len(self.map)):
            print(self.map[i], '\t', self.time_map[i])
        print("father:", self.father)
        print("sons:", self.sons)


def disolve(input):
    global n_police, n_medics, queries, observe
    queries = input["queries"]
    n_police = input["police"]
    n_medics = input["medics"]
    observe = input["observations"]


def first_step():
    global level
    first_map = [list(row) for row in observe[0]]
    first_time_map = copy.deepcopy(first_map)
    for i, row in enumerate(first_time_map):
        for j, col in enumerate(row):
            if first_map[i][j] == 'S':
                first_time_map[i][j] = 3
            else:
                first_time_map[i][j] = 0

    num_q_marks = 0
    q_marks_indices = []
    for i, row in enumerate(first_map):
        for j, state in enumerate(row):
            if state == "?":
                num_q_marks += 1
                q_marks_indices.append([i, j])

    begin_states = ["S", "H", "U"]
    comb = [states_comb for states_comb in itertools.product(begin_states, repeat=num_q_marks)]

    level = {0: []}

    for c in comb:
        new_map = copy.deepcopy(first_map)
        new_time_map = copy.deepcopy(first_time_map)
        for i, state in enumerate(c):
            #print(type(q_marks_indices[i][1]))
            new_map[q_marks_indices[i][0]][q_marks_indices[i][1]] = state
            if state == 'S':
                new_time_map[q_marks_indices[i][0]][q_marks_indices[i][1]] = 3
            else:
                new_time_map[q_marks_indices[i][0]][q_marks_indices[i][1]] = 0
        #print("map:",new_map)
        #print("time map:", new_time_map)
        new_Node = Node(new_map, new_time_map, None, 0)
        level[0].append(new_Node)


def action(obs_num):
    #print("#############", obs_num, "#############")
    global level, n_police, n_medics, observe

    level[obs_num + 1] = []
    #print(level[obs_num])
    ##########################ACTIONS#############################################
    remove_list = []
    for n, node in enumerate(level[obs_num]):
        #node.print()
        single_actions = {'police': [], 'medics': []}
        for i in range(len(node.map)):
            for j in range(len(node.map[i])):
                # print(i, j, '-', col)
                if node.map[i][j] == 'S':
                    single_actions['police'].append(["quarantine", [i, j]])
                elif node.map[i][j] == 'H':
                    single_actions['medics'].append(["vaccinate", [i, j]])
        police_comb = itertools.combinations(single_actions['police'], n_police)
        medics_comb = itertools.combinations(single_actions['medics'], n_medics)
        police_actions = []
        medic_actions = []

        for c in police_comb:
            police_actions.append([c[n] for n in range(n_police)])
        for c in medics_comb:
            medic_actions.append([c[n] for n in range(n_medics)])
        # print("medic_actions:",medic_actions)
        # print("\npolice_actions",police_actions)

        all_actions = []
        if police_actions == []:
            all_actions = medic_actions
        elif medic_actions == []:
            all_actions = police_actions
        else:
            for p_act in police_actions:
                for m_act in medic_actions:
                    all_actions.append(p_act + m_act)
        #print("all_actions:", all_actions)

        ##########################Result#############################################
        for action_set in all_actions:
            #print("action_set:", action_set)
            temp_map = copy.deepcopy(node.map)
            temp_time_map = copy.deepcopy(node.time_map)
            for action in action_set:
                #print("action[1][0]",action[1][0])
                #print("action[1][1]", action[1][1])
                if action[0] == "vaccinate":
                    temp_map[action[1][0]][action[1][1]] = 'I'
                else:
                    temp_map[action[1][0]][action[1][1]] = 'Q'
                    temp_time_map[action[1][0]][action[1][1]] = 2
            #print(temp_map)
            ##########################INFECT#############################################
            change_list = []
            for i, row in enumerate(temp_map):
                for j, col in enumerate(row):
                    if temp_map[i][j] == 'S':
                        if i > 0 and temp_map[i - 1][j] == 'H':
                            change_list.append([i - 1, j])
                        if i < len(temp_map) - 1 and temp_map[i + 1][j] == 'H':
                            change_list.append([i + 1, j])
                        if j > 0 and temp_map[i][j - 1] == 'H':
                            change_list.append([i, j - 1])
                        if j < len(temp_map[0]) - 1 and temp_map[i][j + 1] == 'H':
                            change_list.append([i, j + 1])
            for c in change_list:
                temp_map[c[0]][c[1]] = 'S'
                temp_time_map[c[0]][c[1]] = 4
            #print(temp_map)
            ##########################ADJTIME#############################################
            for i in range(len((temp_time_map))):
                for j in range(len((temp_time_map[i]))):
                    if temp_time_map[i][j] > 0:
                        temp_time_map[i][j] -= 1
                        if temp_time_map[i][j] == 0:
                            temp_map[i][j] = 'H'
            #print(temp_map)
            ##########################COMPARE#############################################
            is_looping = True
            for i, row in enumerate(observe[obs_num + 1]):
                for j, state in enumerate(row):
                    # print("observed:", observe[obs_num+1][i][j])
                    if observe[obs_num + 1][i][j] == temp_map[i][j] or observe[obs_num + 1][i][j] == "?":
                        #print(observe[obs_num + 1][i][j], "==", temp_map[i][j])
                        continue
                    else:
                        is_looping = False
                        break
                if not is_looping:
                    break
            if not is_looping:
                continue

            new_node = Node(temp_map, temp_time_map, node, obs_num+1)
            level[obs_num + 1].append(new_node)
            node.sons.append(new_node)

    #print("before:", level[obs_num])
    for node in level[obs_num]:
        if node.sons == []:
            update_fathers(obs_num, node, remove_list)


    for node in remove_list:
        level[node.level].remove(node)
        if node.father:
            node.father.sons.remove(node)
            #print("end update")
    #print("after:", level[obs_num])


def update_fathers(obs_num, node, to_remove):
    #print(obs_num)
    #print(node)
    #print(node.father)
    to_remove.append(node)
    #print(node)
    if node.father:
        if len(node.father.sons) == 1:      #if has one child, which is going to be removed
            update_fathers(obs_num - 1, node.father, to_remove)
    return to_remove


def check_queries():
    global level, queries
    #print("\n\nqueries:", queries)
    ret_dict = {}
    for q in queries:
        #print("cehcking:", q)
        #print(level[q[1]])
        #print("query:", q)
        #print("query time:", q[1])
        true = False
        false = False
        for n, node in enumerate(level[q[1]]):
            #node.print()
            if node.map[q[0][0]][q[0][1]] == q[2]:
                true = True
            if node.map[q[0][0]][q[0][1]] != q[2]:
                false = True
            if true and false:
                ret_dict[q] = '?'
                break
        if true and false:
            continue
        if true:
            ret_dict[q] = 'T'
        elif false:
            ret_dict[q] = 'F'
        #print()
    if ret_dict == {}:
        for q in queries:
            ret_dict[q] = 'F'
    return ret_dict

def solve_problem(input):
    disolve(input)
    first_step()
   # for node in level[0]:
      #  node.print()
       # print()
    for num in range(len(observe)-1):
        to_remove = action(num)

    #print("___________________________")
    #print_all()
    return check_queries()



def print_all():
    global level
    for i in level:
        print("#############", i, "#############")
        for node in level[i]:
            node.print()
