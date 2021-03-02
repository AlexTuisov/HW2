from pysat.solvers import Glucose3,Solver
from itertools import combinations
ids = ['207406638', '318188984']

def add_to_cluase(g, place, a):
    for i in range(1,9):
        if i == a :
            g.add_clause([place + i])
        else:
            g.add_clause([-(place + i)])



def solve_problem(input):
    g = Solver()
    obs0 = input["observations"][0]
    n = len(obs0)
    m = len(obs0[0])
    obs = input["observations"]

    x = m*n*len(obs)*8+1
    g.add_clause([-x])
    police = input["police"]
    medics = input["medics"]
    for k in range(len(input["observations"])):
        sList =[]
        iList = []
        for i in range(n):
            for j in range(m):

                place = k * m * n * 8 + (i * m + j) * 8

                if input["police"] == 0:
                    g.add_clause([-(place + 6)])
                    g.add_clause([-(place + 7)])
                if input["medics"] == 0:
                    g.add_clause([-(place + 8)])

                if (obs[k][i][j] == "S" or obs[k][i][j] == "?") and k < len(input["observations"]) - 1:
                    sList.append(place + m * n * 8 + 6)
                if (obs[k][i][j] == "H" or obs[k][i][j] == "?")and k < len(input["observations"])-1:
                    iList.append(place+m*n*8 +8)
                g.add_clause([place + 1, place + 2, place + 3, place + 4, place + 5,place+6,place+7,place+8])
                for l in range(1,9):
                    for o in range(1,9):
                        if (o!=l):
                            g.add_clause([-(place+l),-(place+o)])

                if k < len(input["observations"]) - 1:
                    g.add_clause([-(place + 5),(place + m * n * 8 + 5)])
                    g.add_clause([-(place + 8),(place + m * n * 8 + 8)])

                    g.add_clause([-(place + 6), place + m * n * 8 + 7])
                    g.add_clause([-(place + 7), place + m * n * 8 + 1])


                    g.add_clause([-(place + 2), place + m * n * 8 + 3, place + m * n * 8 + 6])
                    g.add_clause([-(place + 3), place + m * n * 8 + 4, place + m * n * 8 + 6])
                    g.add_clause([-(place + 4), place + m * n * 8 + 1, place + m * n * 8 + 6])

                    if i > 0:
                        g.add_clause([-(place+2),-(place - m * 8 + 1),(place + m * n * 8 - m * 8 + 2),(place + m * n * 8 - m * 8 + 8),(place + m * n * 8 + 6)])
                        g.add_clause([-(place+3),-(place - m * 8 + 1),(place + m * n * 8 - m * 8 + 2),(place + m * n * 8 - m * 8 + 8),(place + m * n * 8 + 6)])
                    if j > 0:
                        g.add_clause([-(place+2),-(place - 8 + 1),(place + m * n * 8 - 8 + 2),(place + m * n * 8 - 8 + 8),(place + m * n * 8 + 6)])
                        g.add_clause([-(place+3),-(place - 8 + 1),(place + m * n * 8 - 8 + 2),(place + m * n * 8 - 8 + 8),(place + m * n * 8 + 6)])
                    if i < n-1:
                        g.add_clause([-(place+2),-(place + m * 8 + 1),(place + m * n * 8 + m * 8 + 2),(place + m * n * 8 + m * 8 + 8),(place + m * n * 8 + 6)])
                        g.add_clause([-(place+3),-(place + m * 8 + 1),(place + m * n * 8 + m * 8 + 2),(place + m * n * 8 + m * 8 + 8),(place + m * n * 8 + 6)])
                    if j < m-1:
                        g.add_clause([-(place+2),-(place + 8 + 1),(place + m * n * 8 + 8 + 2),(place + m * n * 8 + 8 + 8),(place + m * n * 8 + 6)])
                        g.add_clause([-(place+3),-(place + 8 + 1),(place + m * n * 8 + 8 + 2),(place + m * n * 8 + 8 + 8),(place + m * n * 8 + 6)])

                # zkanu s1 fkan fi 7da 7wale s
                if k >= 1:


                    g.add_clause([-(place+7),place - m * n * 8+6])
                    g.add_clause([-(place+6),place - m * n * 8+2,place - m * n * 8+3,place - m * n * 8+4])
                    g.add_clause([-(place+3),place - m * n * 8 +2])
                    g.add_clause([-(place+4),place - m * n * 8 +3])
                    g.add_clause([-(place+2),place - m * n * 8 +1])

                    g.add_clause([-(place+5),(place - m * n * 8 + 5)])
                    g.add_clause([-(place+8),(place - m * n * 8 + 8),(place - m * n * 8 + 1)])

                    g.add_clause([-(place+2), (i>0)*(place - m * n * 8 - m * 8 + 2) + x*(i<=0),
                                  (i>0)*(place - m * n * 8 - m * 8 + 3)+x*(i<=0),#(i>0)*(place - m * n * 8 - m * 8 + 4)+x*(i<=0),
                                  (j>0)*(place - m * n * 8 - 8 + 2)+x*(j<=0),(j>0)*(place - m * n * 8 - 8 + 3)+x*(j<=0),
                                  #(j>0)*(place - m * n * 8 - 8 + 4)+x*(j<=0),
                                  (i<n-1)*(place - m * n * 8 + m * 8 + 2)+x*(i>=n-1),
                                  (i<n-1)*(place - m * n * 8 + m * 8 + 3)+x*(i>=n-1),
                                  #(i<n-1)*(place - m * n * 8 + m * 8 + 4)+x*(i>=n-1),
                                  (j<m-1)*(place - m * n * 8 + 8 + 2)+x*(j>=m-1),(j<m-1)*(place - m * n * 8 + 8 + 3)+x*(j>=m-1),
                                  #(j<m-1)*(place - m * n * 8 + 8 + 4)+x*(j>=m-1)
                                    ])

                if obs[k][i][j] == "H":
                    g.add_clause([place +1])

                if obs[k][i][j] == "U":
                    g.add_clause([place+5])
                if obs[k][i][j] == "I":
                    g.add_clause([place+8])
                if obs[k][i][j] == "S":
                    g.add_clause([place+2,place+3,place+4])

                if obs[k][i][j] == "Q":
                    g.add_clause([place+6,place+7])


                #
                if k==0:
                    if obs[k][i][j] == "S":
                        g.add_clause([place+2])

                    if obs[k][i][j] == "?":
                        g.add_clause([place+1,place+2,place+5])

        if (len(sList) != 0 and police>0):
            if len(sList) > police:
                qcombi = list(combinations(sList, police + 1))
                for i in range(len(qcombi)):
                    notcombi = []
                    for j in range(police + 1):
                        notcombi.append(-qcombi[i][j])
                    g.add_clause(notcombi)
                allqcombi = list(combinations(sList, len(sList) - police + 1))
                for i in range(len(allqcombi)):
                    g.add_clause(allqcombi[i])
            else:
                for i in range(len(sList)):
                    g.add_clause([sList[i]])

        if (len(iList) != 0 and medics>0):

            if len(iList) > medics:
                icombi = list(combinations(iList, medics+1))
                for i in range(len(icombi)):
                    notcombi = []
                    for j in range(medics+1):
                        notcombi.append(-icombi[i][j])
                    g.add_clause(notcombi)
                allqcombi = list(combinations(iList, len(iList)-medics+1))

                for i in range(len(allqcombi)):
                    g.add_clause(allqcombi[i])
            else:
                for i in range(len(iList)):
                    g.add_clause([iList[i]])


    obs0 = input["observations"][0]
    n = len(obs0)
    m = len(obs0[0])
    my_list = []
    my_list2 = []
    for i in range(len(input["queries"])):
        a = input["queries"][i][1] * m * n * 8 + (input["queries"][i][0][0] * m + input["queries"][i][0][1]) * 8
        if input["queries"][i][2] == 'H':
            my_list.append((input["queries"][i]))
            if g.solve(assumptions=[a + 1]) == True and not (g.solve(assumptions=[a +2]) == True or g.solve(assumptions=[a +3]) == True or g.solve(assumptions=[a +4]) == True or g.solve(assumptions=[a +5]) == True or g.solve(assumptions=[a +6]) == True or g.solve(assumptions=[a +7]) == True or g.solve(assumptions=[a +8]) == True):
                c = "T"
            elif g.solve(assumptions=[a + 1]) == True:
                c = "?"
            else:
                c = "F"
            my_list2.append(c)
        if input["queries"][i][2] == 'S':
            my_list.append(input["queries"][i])
            if (g.solve(assumptions=[a +2]) == True or g.solve(assumptions=[a+3]) == True or g.solve(assumptions=[a+4]) == True) and not(g.solve(assumptions=[a +1]) == True or g.solve(assumptions=[a +5]) == True or g.solve(assumptions=[a +6]) == True or g.solve(assumptions=[a +7]) == True or g.solve(assumptions=[a +8]) == True):
                c = "T"
            elif g.solve(assumptions=[a +2]) == True or g.solve(assumptions=[a+3]) == True or g.solve(assumptions=[a+4]) == True:
                c = "?"
            else:
                c = "F"
            my_list2.append(c)
        if input["queries"][i][2] == 'Q':
            my_list.append(input["queries"][i])
            if g.solve(assumptions=[a+6]) == True or g.solve(assumptions=[a+7]) == True and not(g.solve(assumptions=[a +1]) == True or g.solve(assumptions=[a +2]) == True or g.solve(assumptions=[a +3]) == True or g.solve(assumptions=[a +4]) == True or g.solve(assumptions=[a +5]) == True or g.solve(assumptions=[a +8]) == True):
                c = "T"
            elif g.solve(assumptions=[a+6]) == True or g.solve(assumptions=[a+7]) == True:
                c = "?"
            else:
                c = "F"
            my_list2.append(c)
        if input["queries"][i][2] == 'U':
            my_list.append(input["queries"][i])
            if g.solve(assumptions=[a + 5]) == True and not(g.solve(assumptions=[a +2]) == True or g.solve(assumptions=[a +3]) == True or g.solve(assumptions=[a +4]) == True or g.solve(assumptions=[a +1]) == True or g.solve(assumptions=[a +6]) == True or g.solve(assumptions=[a +7]) == True or g.solve(assumptions=[a +8]) == True):

                c = "T"
            elif g.solve(assumptions=[a + 5]) == True :
                c = "?"

            else:
                c = "F"
            my_list2.append(c)
        if input["queries"][i][2] == 'I':
            my_list.append(input["queries"][i])
            if g.solve(assumptions=[a + 8]) == True and not(g.solve(assumptions=[a + 2]) == True or g.solve(assumptions=[a + 3]) == True or g.solve(
                    assumptions=[a + 4]) == True or g.solve(assumptions=[a + 5]) == True or g.solve(
                    assumptions=[a + 6]) == True or g.solve(assumptions=[a + 7]) == True or g.solve(
                    assumptions=[a + 1]) == True):
                c = "T"
            elif g.solve(assumptions=[a + 8]) == True:
                c = "?"
            else:
                c = "F"
            my_list2.append(c)
    dic = {}
    for i in range(len(my_list)):
        dic[my_list[i]] = my_list2[i]
    return dic