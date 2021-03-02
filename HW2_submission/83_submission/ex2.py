from pysat.solvers import Solver
import sympy
from itertools import combinations

ids = ['211428941']
INF = -1

def solve_problem(input):
    poss_dict = dict()
    s = Solver(name='g3')
    poss_list = []
    loc_list = []
    known_h = []
    known_s = []
    known_q = []
    known_i = []
    known_u = []
    unknown = []
    act_start = 0
    count = 1
    round = 0
    for observation in input["observations"]:
        known_h.append(list())
        known_s.append(list())
        known_q.append(list())
        known_i.append(list())
        known_u.append(list())
        unknown.append(list())
        i=0
        for row in observation:
            j=0
            for item in row:
                if item == 'H':
                    known_h[round].append((i,j))
                    poss_dict[((i,j),round,'H',INF)] = count
                    s.add_clause([count])
                    count += 1
                    poss_dict[((i,j),round,'S',3)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',2)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',1)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'Q',2)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'Q',1)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'I',INF)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'U',INF)] = count
                    s.add_clause([-count])
                    count += 1
                elif item == 'S':
                    known_s[round].append((i,j))
                    poss_dict[((i,j),round,'H',INF)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',3)] = count
                    count += 1
                    poss_dict[((i,j),round,'S',2)] = count
                    count += 1
                    poss_dict[((i,j),round,'S',1)] = count
                    if round == 0:
                        s.add_clause([count-2])
                    s.add_clause([count,count-1,count-2])
                    s.add_clause([-count,-(count-1)])
                    s.add_clause([-count,-(count-2)])
                    s.add_clause([-(count-1),-(count-2)])
                    count += 1
                    poss_dict[((i,j),round,'Q',2)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'Q',1)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'I',INF)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'U',INF)] = count
                    s.add_clause([-count])
                    count += 1
                elif item == 'Q':
                    known_q[round].append((i,j))
                    poss_dict[((i,j),round,'H',INF)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',3)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',2)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',1)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'Q',2)] = count
                    count += 1
                    poss_dict[((i,j),round,'Q',1)] = count
                    if round == 0:
                        s.add_clause([count-1])
                    s.add_clause([count,count-1])
                    s.add_clause([-count,-(count-1)])
                    count += 1
                    poss_dict[((i,j),round,'I',INF)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'U',INF)] = count
                    s.add_clause([-count])
                    count += 1
                elif item == 'I':
                    known_i[round].append((i,j))
                    poss_dict[((i,j),round,'H',INF)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',3)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',2)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',1)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'Q',2)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'Q',1)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'I',INF)] = count
                    s.add_clause([count])
                    count += 1
                    poss_dict[((i,j),round,'U',INF)] = count
                    s.add_clause([-count])
                    count += 1
                elif item == 'U':
                    known_u[round].append((i,j))
                    poss_dict[((i,j),round,'H',INF)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',3)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',2)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',1)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'Q',2)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'Q',1)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'I',INF)] = count
                    s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'U',INF)] = count
                    s.add_clause([count])
                    count += 1
                elif item == "?":
                    unknown[round].append((i,j))
                    poss_dict[((i,j),round,'H',INF)] = count
                    count += 1
                    poss_dict[((i,j),round,'S',3)] = count
                    count += 1
                    poss_dict[((i,j),round,'S',2)] = count
                    if round == 0:
                        s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'S',1)] = count
                    if round == 0:
                        s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'Q',2)] = count
                    count += 1
                    poss_dict[((i,j),round,'Q',1)] = count
                    if round == 0:
                        s.add_clause([-count])
                    count += 1
                    poss_dict[((i,j),round,'I',INF)] = count
                    count += 1
                    poss_dict[((i,j),round,'U',INF)] = count
                    s.add_clause([count,count-1,count-2,count-3,count-4,count-5,count-6,count-7])
                    for k in range(8):
                        for l in range(k,8): 
                            if l != k:
                                s.add_clause([-(count-k),-(count-l)])
                    count += 1

                poss_list.append(((i,j),round,'H',INF))
                poss_list.append(((i,j),round,'S',3))
                poss_list.append(((i,j),round,'S',2))
                poss_list.append(((i,j),round,'S',1))
                poss_list.append(((i,j),round,'Q',2))
                poss_list.append(((i,j),round,'Q',1))
                poss_list.append(((i,j),round,'I',INF))
                poss_list.append(((i,j),round,'U',INF))
                if round == 0:
                    loc_list.append((i,j))
                #if item == 'H':
                #    known_h_count[round] += 1
                #elif item == 'S':
                #    known_s_count[round] += 1
                j+=1
            i+=1
        round+=1
    med = input["medics"]
    pol = input["police"]
    med_possibilities = list()
    pol_possibilities = list()
    for round in range(len(input["observations"])):
        act_start = count
        if round < len(input["observations"]) - 1:
            possibly_healthy = known_h[round]+unknown[round]
            possibly_sick = known_s[round] + unknown[round]
            med_possibilities.append(list())
            if med < len(known_h[round]):
                med_possibilities[round].extend(combinations(possibly_healthy,med))
            else:
                for i in range(len(known_h[round]),med+1):
                    med_possibilities[round].extend(combinations(possibly_healthy,i))
            pol_possibilities.append(list())
            if pol < len(known_s[round]):
                pol_possibilities[round].extend(combinations(possibly_sick,pol))
            else:
                for i in range(len(known_s[round]),pol+1):
                    pol_possibilities[round].extend(combinations(possibly_sick,i))
        
            act_list = []
            act_item = []
            for med_pos in med_possibilities[round]:
                if med_pos == ():
                    for pol_pos in pol_possibilities[round]:
                        if pol_pos == ():
                            act_list.append(((),round))
                            poss_dict[((),round)] = count
                            poss_list.append(((),round))
                            count+=1
                        else:
                            act_item = []
                            for single_pol in pol_pos:
                                act_item.append(('quarantine',single_pol))
                            poss_dict[(tuple(act_item),round)] = count
                            count+=1
                            act_list.append((tuple(act_item),round))
                            poss_list.append((tuple(act_item),round))
                else:
                    for pol_pos in pol_possibilities[round]:
                        if pol_pos == ():
                            act_item = []
                            for single_med in med_pos:
                                act_item.append(('vaccinate',single_med))
                            poss_dict[(tuple(act_item),round)] = count
                            count+=1
                            act_list.append((tuple(act_item),round))
                            poss_list.append((tuple(act_item),round))
                        else:
                            flag = False
                            for single_med in med_pos:
                                for single_pol in pol_pos:
                                    if single_med == single_pol:
                                        flag = True
                                        break
                                if flag:
                                    break
                            if flag:
                                continue
                            act_item = []
                            for single_med in med_pos:
                                act_item.append(('vaccinate',single_med))
                            for single_pol in pol_pos:
                                act_item.append(('quarantine',single_pol))
                            poss_dict[(tuple(act_item),round)] = count
                            count+=1
                            act_list.append((tuple(act_item),round))
                            poss_list.append((tuple(act_item),round))
            if len(act_list) == 1:
                s.add_clause([poss_dict[act_list[0]]])
            else:
                s.add_clause(list(range(act_start,count)))
                for k in range(act_start,count):
                    for l in range(k+1, count):
                        s.add_clause([-k,-l])
            for action in act_list:
                
                quarred = []
                immune = []
                for act in action[0]:
                    if act[0] == 'quarantine':
                        quarred.append(act[1])
                        s.add_clause([-poss_dict[action], poss_dict[(act[1], round, 'S',3)], poss_dict[(act[1], round, 'S',2)], poss_dict[(act[1], round, 'S',1)]])
                        s.add_clause([-poss_dict[action], poss_dict[(act[1], round+1, 'Q',2)]])
                    else:
                        immune.append(act[1])
                        s.add_clause([-poss_dict[action],poss_dict[(act[1],round,'H',INF)]])
                        s.add_clause([-poss_dict[action], poss_dict[(act[1], round+1, 'I',INF)]])
                for i in range(len(input['observations'][round])):
                    for j in range(len(input['observations'][round][i])):
                        if (i,j) in quarred or (i,j) in immune:
                            continue
                        s.add_clause([-poss_dict[((i,j),round,'S',3)],-poss_dict[action],poss_dict[((i,j),round+1,'S',2)]])
                        s.add_clause([-poss_dict[((i,j),round+1,'S',3)],-poss_dict[action],poss_dict[((i,j),round,'H',INF)]])
                        s.add_clause([poss_dict[((i,j),round,'S',3)],-poss_dict[action],-poss_dict[((i,j),round+1,'S',2)]])
                        s.add_clause([-poss_dict[((i,j),round,'S',2)],-poss_dict[action],poss_dict[((i,j),round+1,'S',1)]])
                        s.add_clause([poss_dict[((i,j),round,'S',2)],-poss_dict[action],-poss_dict[((i,j),round+1,'S',1)]])
                        s.add_clause([-poss_dict[((i,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                        s.add_clause([-poss_dict[((i,j),round,'Q',2)],-poss_dict[action],poss_dict[((i,j),round+1,'Q',1)]])
                        s.add_clause([poss_dict[((i,j),round,'Q',2)],-poss_dict[action],-poss_dict[((i,j),round+1,'Q',1)]])
                        s.add_clause([-poss_dict[((i,j),round,'Q',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                        s.add_clause([-poss_dict[((i,j),round,'I',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'I',INF)]])
                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j),round,'I',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'I',INF)]])
                        s.add_clause([-poss_dict[((i,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'U',INF)]])
                        s.add_clause([poss_dict[((i,j),round,'U',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'U',INF)]])
                        s.add_clause([poss_dict[((i,j),round,'Q',1)],poss_dict[((i,j),round,'S',1)],poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                        if i > 0 and (i-1,j) not in immune:
                            s.add_clause([-poss_dict[((i,j),round,'S',3)],-poss_dict[((i-1,j),round,'H',INF)],-poss_dict[action],poss_dict[((i-1,j),round+1,'S',3)]])
                            s.add_clause([-poss_dict[((i,j),round,'S',2)],-poss_dict[((i-1,j),round,'H',INF)],-poss_dict[action],poss_dict[((i-1,j),round+1,'S',3)]])
                            s.add_clause([-poss_dict[((i,j),round,'S',1)],-poss_dict[((i-1,j),round,'H',INF)],-poss_dict[action],poss_dict[((i-1,j),round+1,'S',3)]])
                            if i < len(input['observations'][round])-1:
                                if j > 0:
                                    if j < len(input['observations'][round][i])-1:
                                        # i-1, i+1, j-1, j+1
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        # i-1, i+1, j-1
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])  
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])  
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                else:
                                    if j < len(input['observations'][round][i])-1:
                                        #i-1, i+1, j+1
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])   
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])   
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])   
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])   
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                    
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                            else:
                                if j > 0:
                                    if j < len(input['observations'][round][i])-1:
                                        #i-1, j-1, j+1
                                        if (i-1,j) not in quarred:
                                                
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                                
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i-1, j-1
                                        if (i-1,j) not in quarred:
                                            if (i,j-1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if(i,j-1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                else:
                                    if j < len(input['observations'][round][i])-1:
                                        if (i-1,j) not in quarred:
                                            
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                               
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i-1
                                        if (i-1,j) not in quarred:
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                        if i < len(input['observations'][round])-1 and (i+1,j) not in immune:
                            s.add_clause([-poss_dict[((i,j),round,'S',3)],-poss_dict[((i+1,j),round,'H',INF)],-poss_dict[action],poss_dict[((i+1,j),round+1,'S',3)]])
                            s.add_clause([-poss_dict[((i,j),round,'S',2)],-poss_dict[((i+1,j),round,'H',INF)],-poss_dict[action],poss_dict[((i+1,j),round+1,'S',3)]])
                            s.add_clause([-poss_dict[((i,j),round,'S',1)],-poss_dict[((i+1,j),round,'H',INF)],-poss_dict[action],poss_dict[((i+1,j),round+1,'S',3)]])
                            if i > 0:
                                if j > 0:
                                    if j < len(input['observations'][round][i])-1:
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i-1, i+1, j-1
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                        
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                else:
                                    if j < len(input['observations'][round][i])-1:
                                        #i-1, i+1, j+1
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                    
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                    
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                    
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                    
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i-1, i+1
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])  
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                        
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                            else:
                                if j > 0:
                                    if j < len(input['observations'][round][i])-1:
                                        #i+1, j-1,j+1
                                            
                                        if (i+1,j) not in quarred:
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i+1, j-1
                                        if (i+1,j) not in quarred:
                                            if (i,j-1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i,j-1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                    
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                else:
                                    if j < len(input['observations'][round][i])-1:
                                        #i+1, j+1
                                        if (i+1,j) not in quarred:
                                                
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                                
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i+1
                                        if (i+1,j) not in quarred:
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                        if j > 0 and (i,j-1) not in immune:
                            s.add_clause([-poss_dict[((i,j),round,'S',3)],-poss_dict[((i,j-1),round,'H',INF)],-poss_dict[action],poss_dict[((i,j-1),round+1,'S',3)]])
                            s.add_clause([-poss_dict[((i,j),round,'S',2)],-poss_dict[((i,j-1),round,'H',INF)],-poss_dict[action],poss_dict[((i,j-1),round+1,'S',3)]])
                            s.add_clause([-poss_dict[((i,j),round,'S',1)],-poss_dict[((i,j-1),round,'H',INF)],-poss_dict[action],poss_dict[((i,j-1),round+1,'S',3)]])
                            if i > 0:
                                if i < len(input['observations'][round])-1:
                                    if j < len(input['observations'][round][i])-1:
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i+1, i-1, j-1
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                        
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                else:
                                    if j < len(input['observations'][round][i])-1:
                                        #i-1, j+1, j-1
                                        if (i-1,j) not in quarred:
                                                
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                                
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i-1, j-1
                                        if (i-1,j) not in quarred:
                                                
                                            if (i,j-1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                                
                                            if (i,j-1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                    
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                            else:
                                if i < len(input['observations'][round])-1:
                                    if j < len(input['observations'][round][i])-1:
                                        #i+1, j+1, j-1
                                            
                                        if (i+1,j) not in quarred:
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i+1, j-1
                                        if (i+1,j) not in quarred:
                                            if (i,j-1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i,j-1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                 
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                else:
                                    if j < len(input['observations'][round][i])-1:
                                        #j+1, j-1
                                            
                                        if (i,j-1) not in quarred:
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #j-1
                                        if (i,j-1) not in quarred:
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                                
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                        if j < len(input['observations'][round]) -1 and (i,j+1) not in immune:
                            s.add_clause([-poss_dict[((i,j),round,'S',3)],-poss_dict[((i,j+1),round,'H',INF)],-poss_dict[action],poss_dict[((i,j+1),round+1,'S',3)]])
                            s.add_clause([-poss_dict[((i,j),round,'S',2)],-poss_dict[((i,j+1),round,'H',INF)],-poss_dict[action],poss_dict[((i,j+1),round+1,'S',3)]])
                            s.add_clause([-poss_dict[((i,j),round,'S',1)],-poss_dict[((i,j+1),round,'H',INF)],-poss_dict[action],poss_dict[((i,j+1),round+1,'S',3)]])
                            if i > 0:
                                if i <len(input['observations'][round])-1:
                                    if j > 0:
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j-1) not in quarred:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    if (i,j+1) not in quarred:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                    else:
                                                        s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                        s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i-1, i+1, j+1
                                        if (i-1,j) not in quarred:
                                            if (i+1,j) not in quarred:
                                                    
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                    
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i+1,j) not in quarred:
                                                    
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                    
                                                if (i,j+1) not in quarred:
                                                    
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                else:
                                    if j > 0:
                                        #i-1, j+1, j-1
                                        if (i-1,j) not in quarred:
                                                
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                                
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i-1, j+1
                                            
                                                
                                        if (i-1,j) not in quarred:
                                                
                                                
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'Q',2)],poss_dict[((i-1,j),round,'Q',1)],poss_dict[((i-1,j),round,'H',INF)],poss_dict[((i-1,j),round,'I',INF)],poss_dict[((i-1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i-1,j),round,'S',3)],poss_dict[((i-1,j),round,'S',2)],poss_dict[((i-1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                                
                                                
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),-round+1,'H',INF)]])
                            else:
                                if i <len(input['observations'][round])-1:
                                    if j > 0: 
                                        #i+1, j-1, j+1
                                            
                                        if (i+1,j) not in quarred:
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i,j-1) not in quarred:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                if (i,j+1) not in quarred:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                                else:
                                                    s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                    s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #i+1, j+1
                                        if (i+1,j) not in quarred:
                                                
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'Q',2)],poss_dict[((i+1,j),round,'Q',1)],poss_dict[((i+1,j),round,'H',INF)],poss_dict[((i+1,j),round,'I',INF)],poss_dict[((i+1,j),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i+1,j),round,'S',3)],poss_dict[((i+1,j),round,'S',2)],poss_dict[((i+1,j),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                                
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                else:
                                    if j > 0:
                                        #j-1, j+1
                                            
                                        if (i,j-1) not in quarred:
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'Q',2)],poss_dict[((i,j-1),round,'Q',1)],poss_dict[((i,j-1),round,'H',INF)],poss_dict[((i,j-1),round,'I',INF)],poss_dict[((i,j-1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j-1),round,'S',3)],poss_dict[((i,j-1),round,'S',2)],poss_dict[((i,j-1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            if (i,j+1) not in quarred:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                            else:
                                                s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                                s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                    else:
                                        #j+1
                                            
                                        if (i,j+1) not in quarred:
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'Q',2)],poss_dict[((i,j+1),round,'Q',1)],poss_dict[((i,j+1),round,'H',INF)],poss_dict[((i,j+1),round,'I',INF)],poss_dict[((i,j+1),round,'U',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'S',3)]])
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            s.add_clause([poss_dict[((i,j),round,'H',INF)],poss_dict[((i,j+1),round,'S',3)],poss_dict[((i,j+1),round,'S',2)],poss_dict[((i,j+1),round,'S',1)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                                        else:
                                            s.add_clause([-poss_dict[((i,j),round,'H',INF)],-poss_dict[action],poss_dict[((i,j),round+1,'H',INF)]])
                                            s.add_clause([poss_dict[((i,j),round,'H',INF)],-poss_dict[action],-poss_dict[((i,j),round+1,'H',INF)]])
                            
    answer_dict = dict()
    for query in input['queries']:
        q = list(query)
        if q[2] == 'H' or q[2] =='I' or q[2] == 'U':
            q_1 = q + [INF]
            a_pos = s.solve(assumptions=[poss_dict[tuple(q_1)]])
            a_neg = s.solve(assumptions=[-poss_dict[tuple(q_1)]])
            if not a_pos:
                answer_dict[tuple(q)] = 'F'
            elif a_pos and a_neg:
                answer_dict[tuple(q)] = '?'
            else:
                answer_dict[tuple(q)] = 'T'
        elif q[2] == 'S':
            q_1 = q + [1]
            q_2 = q + [2]
            q_3 = q + [3]
            a_1_pos = s.solve(assumptions=[poss_dict[tuple(q_1)]])
            a_1_neg = s.solve(assumptions=[-poss_dict[tuple(q_1)]])
            a_2_pos = s.solve(assumptions=[poss_dict[tuple(q_2)]])
            a_2_neg = s.solve(assumptions=[-poss_dict[tuple(q_2)]])
            a_3_pos = s.solve(assumptions=[poss_dict[tuple(q_3)]])
            a_3_neg = s.solve(assumptions=[-poss_dict[tuple(q_3)]])
            a_h_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'H',INF)]])
            a_i_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'I',INF)]])
            a_u_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'U',INF)]])
            a_q_2_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'Q',2)]])
            a_q_1_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'Q',1)]])
            if not a_1_pos and not a_2_pos and not a_3_pos:
                answer_dict[tuple(q)] = 'F'
            elif a_h_pos or a_i_pos or a_u_pos or a_q_2_pos or a_q_1_pos:
                answer_dict[tuple(q)] = '?'
            else:
                answer_dict[tuple(q)] = 'T'
        elif q[2] == 'Q':
            q_1 = q + [1]
            q_2 = q + [2]
            a_1_pos = s.solve(assumptions=[poss_dict[tuple(q_1)]])
            a_1_neg = s.solve(assumptions=[-poss_dict[tuple(q_1)]])
            a_2_pos = s.solve(assumptions=[poss_dict[tuple(q_2)]])
            a_2_neg = s.solve(assumptions=[-poss_dict[tuple(q_2)]])
            a_h_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'H',INF)]])
            a_i_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'I',INF)]])
            a_u_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'U',INF)]])
            a_s_1_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'S',1)]])
            a_s_2_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'S',2)]])
            a_s_3_pos = s.solve(assumptions=[poss_dict[(q[0],q[1],'S',3)]])
            if not a_1_pos and not a_2_pos:
                answer_dict[tuple(q)] = 'F'
            elif a_h_pos or a_i_pos or a_u_pos or a_s_2_pos or a_s_1_pos or a_s_3_pos:
                answer_dict[tuple(q)] = '?'
            else:
                answer_dict[tuple(q)] = 'T'
    return answer_dict
        

           


    pass
    # put your solution here, remember the format needed

