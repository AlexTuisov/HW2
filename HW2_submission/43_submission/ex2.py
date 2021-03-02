ids = ["931161715", "931158984"]
import numpy as np
import itertools
import copy

# retourne les subset de taille n d'une liste s
def findsubsets(s, n):
    if len(s)>= n: # eviter si on a par exemple findsubsets([1,2],3) la fonction renvoie []
        return [list(i) for i in itertools.combinations(s, n)]
    else:
        return [s]

# retourne une liste des coordonnees et action de tous les aera demandé dans la map (S ou H ...)
def aeraSearch(map, aera):

    ligne = map.shape[0]
    col = map.shape[1]
    listAera = []
    actionType = "quarantine"
    if aera == 2: #H
        actionType = "vaccinate"

    for i in range(ligne):
        for j in range(col):
            if map[i][j] == aera:
                listAera.append((actionType,(i,j)))
    return listAera


def IsInMap(map,i,j):
    if i >=0 and i<len(map) and j>=0 and j<len(map[0]):
        return True
    else:
        return False


def checkMod(state,i,j):
    newState = state
    if IsInMap(newState, i, j):
        if newState[i][j] == 2:#H
            newState[i][j] = 11#S special puisque celui ci va etre retrancher au expire
        return newState
    else:
        return newState

#regarde autour de la case(i,j), si il y a un H il le modifie en S


def checkAround(state,i,j):
    newState = state
    newState = checkMod(newState,i+1,j)
    newState = checkMod(newState,i-1,j)
    newState = checkMod(newState,i,j+1)
    newState = checkMod(newState,i,j-1)
    return newState

#recoit le state et rend un new state avec une nouvelle map en fonction des infections
#c à dire toute H qui sont à coté d'un S deviennent S
def infection(state):
    infectedState = state
    for i in range(len(infectedState)):
        for j in range(len(infectedState[0])):
            if infectedState[i][j] in [8,9,10]:#possible que le 7 ne serve à rien. j'hesite à inclure 11 mais ca voudrait dire que le H qui vient d'etre infecté peut au meme tour infecter d'autre.
                infectedState = checkAround(infectedState,i,j)
    return infectedState

def expire(state, type):
    newState = state

    for i in range(len(newState)):
        for j in range(len(newState[0])):
            if type == 10: #si c la sickness qui doit expirer
                if newState[i][j] in [7,8,9,10,11]:
                    newState[i][j] -= 1
                if newState[i][j] == 7:
                    newState[i][j] = 2



            elif type == 5: #si c la quarantaine qui doit expirer
                if newState[i][j] in [3,4,5,6]:
                    newState[i][j] -= 1
                if newState[i][j] == 3:
                    newState[i][j] = 2



    return newState

def actions(state,policeNb,medNb):
    """Returns all the actions that can be executed in the given
    state. The result should be a tuple (or other iterable) of actions
    as defined in the problem description file"""

    npState = np.array(state)
 # liste des actions des sick
    listOfSick4 = aeraSearch(npState, 10)
    listOfSick1 = aeraSearch(npState, 9)
    listOfSick2 = aeraSearch(npState, 8)
    listOfSick3 = aeraSearch(npState, 7)

    listOfSick = listOfSick1 + listOfSick2 + listOfSick3 + listOfSick4

    listOfHealthy = aeraSearch(npState, 2)

    sickSubset = findsubsets(listOfSick, policeNb)

    healthySubset = findsubsets(listOfHealthy, medNb)
    allActions = []

    if len(sickSubset) == 0:
        return healthySubset
    if len(healthySubset) == 0:
        return sickSubset


    for actionSick in sickSubset:
        for actionHealth in healthySubset:
            possibleAction = actionSick + actionHealth

            allActions.append(possibleAction)
    return allActions


def result(state, action):
    """Return the state that results from executing the given
    action in the given state. The action must be one of
    self.actions(state)."""
    npState = np.array(state)
    if action != None:


        # actions take effect
        for act in action:
            type = act[0]  # quarantine or vaccinate
            row = act[1][0]  # position de la ligne du area à modifié
            col = act[1][1]  # position de la colonne du area

            if (type == "quarantine"):
                npState[row][col] = 6

            elif (type == "vaccinate"):
                npState[row][col] = 1

    # infection spread
    listState1 = infection(npState)

    # sickness expires
    listState2 = expire(listState1, 10)

    # quarantine expires
    listState = expire(listState2, 5)

    return listState

class State:
    def __init__(self, map, time, oldMap):
        self.map, self.point = self.buildState(map, time, oldMap)
        self.time = time

    def buildState(self, init, t, oldInit):

        if t==0:
            point = []
            map = np.zeros((len(init), len(init[0])), int)
            for i in range(len(map)):
                for j in range(len(map[0])):
                    if init[i][j] == 'U':
                        map[i][j] = 20
                    if init[i][j] == 'I':
                        map[i][j] = 1
                    if init[i][j] == 'H':
                        map[i][j] = 2
                    if init[i][j] == 'Q':
                        map[i][j] = 5
                    if init[i][j] == 'S':
                        map[i][j] = 10
                    if init[i][j] == '?':
                        map[i][j] = 100
                        point.append((i, j))
            return map, point
        else:
            point = []
            map = np.zeros((len(init), len(init[0])), int)
            for i in range(len(map)):
                for j in range(len(map[0])):
                    if init[i][j] == 'U':
                        map[i][j] = 20
                    if init[i][j] == 'I':
                        map[i][j] = 1
                    if init[i][j] == 'H':
                        map[i][j] = 2
                    if init[i][j] == 'Q' and oldInit[i][j] == 5:#Si ya un Q de 2eme generation
                        map[i][j] = oldInit[i][j] - 1
                    if init[i][j] == 'Q' and oldInit[i][j] != 5:#si c un nouveau Q
                        map[i][j] = 5
                    if init[i][j] == 'S' and oldInit[i][j] in [10,9]: #si ya un S et qu'au tour d'avant c'etait aussi un S
                        map[i][j] = oldInit[i][j] - 1
                    if init[i][j] == 'S' and oldInit[i][j] not in [10,9]: #si c'est un nouveau S
                        map[i][j] = 10
                    if init[i][j] == '?':
                        map[i][j] = 100
                        point.append((i, j))
            return map, point

def compare(a,b):
    for i in range(len(a)):
        for j in range(len(a[0])):
            if a[i][j] in [8,9,10] and b[i][j] in [8,9,10]: #si c un S dans les 2 cases
                continue
            if a[i][j] in [5,4] and b[i][j] in [5,4]: #si c un S dans les 2 cases
                continue
            if a[i][j] != b[i][j] and b[i][j] != 100:
                return False
    return True

def compare2(a,b):
    if a == b:
        return True
    if a in [8, 9] and b ==10:  # si c un S dans les 2 cases
        return True
    if a == 4 and b == 5:  # si c un S dans les 2 cases
        return True
    else:
        return False

def buildChild(possibleMap,subMap,police,medics): #crée la couche inferieur de l'arbre des map possible, possibleMap est une liste de map de la couche actuelle, subMap est la map input au temps d'apres.
    turnPossibleMap = []
    if police == 0 and medics == 0:
        for mp in possibleMap:
            afterState = result(mp, None)  # regarder ce que ca fait au prochain tour
            if compare(afterState, subMap) == True:
                turnPossibleMap.append(afterState)
    else:
        for mp in possibleMap:
            possibleActions = actions(mp, police, medics)
            for act in possibleActions:
                afterState = result(mp, act)  # regarder ce que ca fait au prochain tour
                if compare(afterState, subMap) == True:
                    turnPossibleMap.append(afterState)
    return turnPossibleMap

def convert(query): #convertir la query
    x = query
    y = 0
    if x[2] == 'U':
        y = 20
    elif x[2] == 'I':
        y = 1
    elif x[2] == 'H':
        y = 2
    elif x[2] == 'Q':
        y = 5
    elif x[2] == 'S':
        y = 10
    return y

def solve_problem(input):
    pass
    # put your solution here, remember the format needed


    police = input["police"]
    medics = input["medics"]
    obs = np.array(input["observations"])
    query = input["queries"]

    listOfState = [] #liste de state recu
    for i in range(len(obs)):
        if i==0:
            state = State(obs[i], i, None)
        else:
            state = State(obs[i], i, listOfState[i-1].map)
        listOfState.append(state) #is a list of the state updated with relevant numbers

   # construction de l'arbre
    possibleMap = {} #dictionnaire des map possibles, en [0] se trouve une lise de toutes les map possible au t=0


    if len(listOfState[0].point) >= 1:  # si il ya un seul pt d'interrogation dans la 1ere map
        stMap = copy.deepcopy(listOfState[0].map)
        turnPossibleMap = []
        area = [1, 20, 2, 10]
        subset = findsubsets(area,len(listOfState[0].point))
        for whichArea in subset:
            permuta = list(itertools.permutations(whichArea))
            for permut in permuta:

                for u in range(len(listOfState[0].point)):
                    p = listOfState[0].point[u]
                    stMap[p[0]][p[1]] = permut[u]
                 # on remplace le point par un area puis on voit ce que ca donne à t+1. on ne remplace pas par 5 parce qu'il nya pas de q au t0

                if police==0 and medics==0:
                    afterState = result(stMap, None)  # regarder ce que ca fait au prochain tour
                    x = copy.deepcopy(stMap)#ATTENTION si on ne fait pas ca il y aura plusieurs elements en multiple dans turnPossibleMap
                    if compare(afterState, listOfState[1].map) == True:
                        turnPossibleMap.append(x)
                else: #si ya des ressources, donc prendre en compte les differentes actions possibles
                    possibleActions = actions(stMap, police, medics)
                    for act in possibleActions:
                        afterState = result(stMap, act)
                        x = copy.deepcopy(stMap)  # ATTENTION si on ne fait pas ca il y aura plusieurs elements en multiple dans turnPossibleMap
                        if compare(afterState, listOfState[1].map) == True:
                            turnPossibleMap.append(x)
                            break #pas besoin de continuer à voir pour toute les actions sinon ca va ajouter des state en double
                                #il suffit qu'au moins une action possible sur la map donnee entraine une map identique au tour suivant


        possibleMap[0] = turnPossibleMap

    if len(listOfState[0].point) == 0:  # si il ya pas de pt d'interrogation dans la 1ere map
        stMap = listOfState[0].map
        turnPossibleMap = []
        turnPossibleMap.append(stMap)
        possibleMap[0]=turnPossibleMap


#à partir du deuxieme tour jusqu'a l'avant dernier
    for i in range(len(obs)-1):
        possibleMap[i+1]=buildChild(possibleMap[i],listOfState[i+1].map,police,medics)

    #(possibleMap[0])
    #print(possibleMap[1])

#--------predict----------

    finalResult = {}

    for q in query:
        qConvert = convert(q)
        counter = 0
        for map in possibleMap[q[1]]:
            if compare2(map[q[0][0]][q[0][1]], qConvert): #si on voit dans une des map de la couhe de l'arbre correspondante le aera recherché ajouter 1 au compteur
                counter = counter+1

        if counter == len(possibleMap[q[1]]):#si toutes les maps contiennent le area donnée
            finalResult[q] = 'T'
        elif counter < len(possibleMap[q[1]]) and  counter>0 : #si ya parmi les maps certaines qui ne contiennent pas le area donnée
            finalResult[q] = '?'
        elif counter == 0: #si il n'y a aucune map avec le area de la query
            finalResult[q] = 'F'

    return finalResult