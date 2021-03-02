import itertools

from pysat.solvers import Glucose3
from pysat.card import CardEnc, EncType

ids = ['314923301', '206693665']


def solve_problem(inputs):
    solutionDict = {}
    nPolice, nMedics = inputs["police"], inputs["medics"]
    observations = inputs["observations"]
    b, nRows, nCols = len(observations), len(observations[0]), len(observations[0][0])
    clauses, atomsToIndex = calcAllClauses(b, nRows, nCols, nPolice, nMedics, observations)
    for query in inputs["queries"]:
        querynum = atomsToIndex[(query[1], query[0], query[2])]
        solver = Glucose3()
        for clause in clauses:
            solver.add_clause(clause)
        withquery = solver.solve(assumptions=[querynum])
        withoutquery = solver.solve(assumptions=[-querynum])
        if withquery and withoutquery:
            solutionDict[query] = "?"
        elif withquery:
            solutionDict[query] = "T"
        else:
            solutionDict[query] = "F"
    return solutionDict


def calcAllClauses(b, nRows, nCols, nPolice, nMedics, observations):
    totalclauses = []
    atomsToIndex, len1 = AtomsToIndexMatching(b, nRows, nCols, nPolice, nMedics)
    allActionsToIndex, _ = actionToIndexMatching(b, nPolice, nMedics, len1, nRows, nCols, atomsToIndex)
    initialClauses = BuildInitialClauses(b, nRows, nCols, atomsToIndex, observations)
    totalclauses += initialClauses
    actionClauses = buildClausesAndEffects(b, nRows, nCols, nPolice, nMedics, allActionsToIndex, atomsToIndex)
    totalclauses += actionClauses
    return totalclauses, atomsToIndex


def AllPossibleInfectionIndices(nRows, nCols):
    indices = []
    for row in range(nRows):
        for col in range(nCols):
            for neighbor in [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]:
                if 0 <= neighbor[0] <= nRows - 1 and 0 <= neighbor[1] <= nCols - 1:
                    indices.append(((row, col), neighbor))
    return indices


def buildMapIndices(nRows, nCols):
    indices = []
    for i in range(nRows):
        for j in range(nCols):
            indices.append((i, j))
    return indices


def AtomsToIndexMatching(b, nRows, nCols, nPolice, nMedics):
    atomsToIndex = {}
    count = 1
    states = ["U", "H", "S", "I", "Q"]
    for roundT in range(b):
        for row in range(nRows):
            for col in range(nCols):
                for state in states:
                    atom = (roundT, (row, col), state)
                    atomsToIndex[atom] = count
                    count += 1
    for roundT in range(b - 1):
        for p in range(nPolice):
            atomsToIndex[("Q", p, roundT)] = count
            count += 1
        for m in range(nMedics):
            atomsToIndex[("V", m, roundT)] = count
            count += 1
    return atomsToIndex, count


def actionToIndexMatching(b, nPolice, nMedics, len3, nRows, nCols, atomsToIndex):
    count = len3 + 1
    actionToIndex = {}
    mapIndicesList = buildMapIndices(nRows, nCols)
    DeseaseSpread = AllPossibleInfectionIndices(nRows, nCols)
    for roundT in range(b - 1):
        for row in range(nRows):
            for col in range(nCols):
                for p in range(nPolice):
                    actionToIndex[("Q", p, roundT, (row, col))] = count
                    count += 1
                for m in range(nMedics):
                    actionToIndex[("V", m, roundT, (row, col))] = count
                    count += 1

    for roundT in range(b - 1):
        for pair in DeseaseSpread:
            actionToIndex[(roundT, pair)] = count
            count += 1

    for atom, atomIdx in atomsToIndex.items():
        actionToIndex[atomIdx] = count
        count += 1

    for roundT in range(2, b):
        for idx in mapIndicesList:
            actionToIndex[("heal", roundT, idx)] = count
            count += 1

    for roundT in range(1, b):
        for idx in mapIndicesList:
            actionToIndex[("exitQ", roundT, idx)] = count
            count += 1

    return actionToIndex, count


def BuildInitialClauses(b, nRows, nCols, atomsToIndex, observations):
    states = ["U", "H", "S", "I", "Q"]
    initialConstraints = []

    for row in range(nRows):
        for col in range(nCols):
            for state in ["Q", "I"]:
                idx = atomsToIndex[(0, (row, col), state)]
                initialConstraints.append([-idx])

    for roundT in range(b):
        for row in range(nRows):
            for col in range(nCols):
                cur_state = observations[roundT][row][col]
                if cur_state != "?":
                    for state in states:
                        curIdx = atomsToIndex[(roundT, (row, col), state)]
                        if cur_state == state:
                            initialConstraints.append([curIdx])
                        else:
                            initialConstraints.append([-curIdx])
                    atleastOne = [atomsToIndex[(roundT, (row, col), x)] for x in states]
                else:
                    if roundT == 0:
                        atleastOne = [atomsToIndex[(roundT, (row, col), x)] for x in ["U", "H", "S"]]
                    else:
                        atleastOne = [atomsToIndex[(roundT, (row, col), x)] for x in ["U", "H", "S", "I", "Q"]]
                onlyOne = negateLinearConstraints(atleastOne)
                initialConstraints += [atleastOne]
                initialConstraints += onlyOne

    return initialConstraints


def negateLinearConstraints(actionsList: list):
    return list(list(x) for x in list(itertools.combinations([-x for x in actionsList], 2)))


def buildClausesAndEffects(b, nRows, nCols, nPolice, nMedics, actionToIndex, atomsToIndex):
    actionClauses = []
    mapIndicesList = buildMapIndices(nRows, nCols)
    DeseaseSpread = AllPossibleInfectionIndices(nRows, nCols)
    actionEffectsAtPreviousT = {}
    for roundT in range(b - 1):
        actionEffectsAtT = {}
        for idx in mapIndicesList:
            for p in range(nPolice):
                actionIndex = actionToIndex[("Q", p, roundT, idx)]
                curClauses, curPre, curAdd, curDel = modelAgentQAction(b, actionIndex,
                                                                       roundT, idx, atomsToIndex)
                actionEffectsAtT[actionIndex] = (curPre, curAdd, curDel)
                actionClauses += curClauses
            for m in range(nMedics):
                actionIndex = actionToIndex[("V", m, roundT, idx)]
                curClauses, curPre, curAdd, curDel = modelAgentVAction(b, actionIndex,
                                                                       roundT, idx, atomsToIndex)
                actionEffectsAtT[actionIndex] = (curPre, curAdd, curDel)
                actionClauses += curClauses
        for idx in mapIndicesList:  # at most 1 quarantine and at most 1 vaccination in each place in the map
            qvars = [actionToIndex[("Q", p, roundT, idx)] for p in range(nPolice)]
            ivars = [actionToIndex[("V", m, roundT, idx)] for m in range(nMedics)]
            actionClauses += CardEnc.atmost(lits=qvars, encoding=EncType.pairwise, bound=1).clauses
            actionClauses += CardEnc.atmost(lits=ivars, encoding=EncType.pairwise, bound=1).clauses
        for p in range(nPolice):  # each police can be used at most once each turn
            qvars = [actionToIndex[("Q", p, roundT, idx)] for idx in mapIndicesList]
            actionClauses += CardEnc.atmost(lits=qvars, encoding=EncType.pairwise, bound=1).clauses
        for m in range(nMedics):  # each medic can be used at most once each turn
            ivars = [actionToIndex[("V", m, roundT, idx)] for idx in mapIndicesList]
            actionClauses += CardEnc.atmost(lits=ivars, encoding=EncType.pairwise, bound=1).clauses
        for p in range(nPolice):
            actionClauses += [[-actionToIndex[("Q", p, roundT, idx)], atomsToIndex[("Q", p, roundT)]] for idx in
                              mapIndicesList]
            actionClauses += [
                [-atomsToIndex[("Q", p, roundT)]] + [actionToIndex[("Q", p, roundT, idx)] for idx in mapIndicesList]]
        for m in range(nMedics):
            actionClauses += [[-actionToIndex[("V", m, roundT, idx)], atomsToIndex[("V", m, roundT)]] for idx in
                              mapIndicesList]
            actionClauses += [
                [-atomsToIndex[("V", m, roundT)]] + [actionToIndex[("V", m, roundT, idx)] for idx in mapIndicesList]]


        for pair in DeseaseSpread:
            actionIndex = actionToIndex[(roundT, pair)]
            curClauses, curPre, curAdd, curDel = ModelInfection(b, roundT, pair, atomsToIndex, actionIndex)
            actionEffectsAtT[actionIndex] = (curPre, curAdd, curDel)
            actionClauses += curClauses

        for atom, atomIdx in atomsToIndex.items():
            if atom[0] == roundT:
                add = atomsToIndex[(atom[0] + 1, atom[1], atom[2])]
                cur_state = atom[2]
                actionIdx = actionToIndex[atomIdx]
                actionEffectsAtT[actionToIndex[atomIdx]] = ([atomIdx], [add], [])
                actionClauses.append([-actionIdx, atomIdx])
                if cur_state == "H":
                    required = [atomsToIndex[("V", m, roundT)] for m in range(nMedics)]
                    for req in required:
                        actionClauses.append([req, -actionIdx])
                    row, col = atom[1][0], atom[1][1]
                    for neighbor in [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]:
                        if 0 <= neighbor[0] <= nRows - 1 and 0 <= neighbor[1] <= nCols - 1:
                            actionClauses.append([-actionIdx, atomsToIndex[(roundT + 1, neighbor, "Q")],
                                                  -atomsToIndex[(roundT, neighbor, "S")]])
                if cur_state == "Q":
                    if roundT >= 1:
                        preC = [atomsToIndex[(roundT, atom[1], "Q")], atomsToIndex[(roundT - 1, atom[1], "Q")]]
                        clause = [-actionIdx]
                        for pre in preC:
                            clause.append(-pre)
                        actionClauses.append(clause)
                if cur_state == "S":
                    required = [atomsToIndex[("Q", p, roundT)] for p in range(nPolice)]
                    for req in required:
                        actionClauses.append([req, -actionIdx])
                    if roundT >= 2:
                        preC = [atomsToIndex[(roundT, atom[1], "S")], atomsToIndex[(roundT - 1, atom[1], "S")],
                                atomsToIndex[(roundT - 2, atom[1], "S")]]
                        clause = [-actionIdx]
                        for pre in preC:
                            clause.append(-pre)
                        actionClauses.append(clause)

        if roundT >= 2:
            for idx in mapIndicesList:
                actionIndex = actionToIndex[("heal", roundT, idx)]
                curClauses, curPre, curAdd, curDel = ModelHealing(roundT, idx, atomsToIndex, actionIndex)
                actionEffectsAtT[actionIndex] = (curPre, curAdd, curDel)
                actionClauses += curClauses

        if roundT >= 1:
            for idx in mapIndicesList:
                actionIndex = actionToIndex[("exitQ", roundT, idx)]
                curClauses, curPre, curAdd, curDel = ModelExitQ(roundT, idx, atomsToIndex, actionIndex)
                actionEffectsAtT[actionIndex] = (curPre, curAdd, curDel)
                actionClauses += curClauses

        interferClauses = BuildInterferClauses(actionEffectsAtT)
        actionClauses += interferClauses
        if roundT >= 1:
            factAchieveClauses = BuildFactAchieveClauses(actionEffectsAtPreviousT, atomsToIndex, roundT)
            actionClauses += factAchieveClauses

        actionEffectsAtPreviousT = actionEffectsAtT

    if actionEffectsAtPreviousT != {}:
        factAchieveClauses = BuildFactAchieveClauses(actionEffectsAtPreviousT, atomsToIndex, b - 1)
        actionClauses += factAchieveClauses

    return actionClauses


def ModelExitQ(roundT, idx, atomsToIndex, actionIdx):
    clauses, preC, addE, delE = [], [], [], []
    preC += [atomsToIndex[(roundT, idx, "Q")], atomsToIndex[(roundT - 1, idx, "Q")]]
    addE.append(atomsToIndex[(roundT + 1, idx, "H")])
    delE += [atomsToIndex[(roundT + 1, idx, "Q")], atomsToIndex[(roundT + 1, idx, "S")],
             atomsToIndex[(roundT + 1, idx, "I")], atomsToIndex[(roundT + 1, idx, "U")]]
    for pre in preC:
        clauses.append([-actionIdx, pre])
    return clauses, preC, addE, delE


def ModelHealing(roundT, idx, atomsToIndex, actionIdx):
    clauses, preC, addE, delE = [], [], [], []
    preC += [atomsToIndex[(roundT, idx, "S")], atomsToIndex[(roundT - 1, idx, "S")],
             atomsToIndex[(roundT - 2, idx, "S")]]
    addE.append(atomsToIndex[(roundT + 1, idx, "H")])
    delE += [atomsToIndex[(roundT + 1, idx, "S")], atomsToIndex[(roundT + 1, idx, "Q")],
             atomsToIndex[(roundT + 1, idx, "I")], atomsToIndex[(roundT + 1, idx, "U")]]
    for pre in preC:
        clauses.append([-actionIdx, pre])
    return clauses, preC, addE, delE


def BuildFactAchieveClauses(actionEffectsAtPreviousT, atomsToIndex, roundT):
    clauses = []
    for atom, atomIdx in atomsToIndex.items():
        clause = [-atomIdx]
        if atom[0] == roundT:
            for actionIdx, actionEffects in actionEffectsAtPreviousT.items():
                if atomIdx in actionEffects[1]:
                    clause.append(actionIdx)
            clauses.append(clause)
    return clauses


def BuildInterferClauses(actionEffectsAtT):
    clauses = []
    for actionidx1, action1Effects in actionEffectsAtT.items():
        for actionidx2, action2Effects in actionEffectsAtT.items():
            interfering = AreInterfering(action1Effects, action2Effects)
            if actionidx1 != actionidx2 and interfering:
                clauses.append([-actionidx1, -actionidx2])
    return clauses


def AreInterfering(action1Effects, action2Effects):
    set1 = set(set(action1Effects[2]) & (set(action2Effects[0]) | set(action2Effects[1])))
    set2 = set(set(action2Effects[2]) & (set(action1Effects[0]) | set(action1Effects[1])))
    return set1 != set() or set2 != set()


def ModelInfection(b, roundT, pair, atomsToIndex, actionIndex):
    clauses = []
    preConditions, addEffects, deleteEffects = [], [], []
    preConditions += [atomsToIndex[(roundT, pair[1], "H")], atomsToIndex[(roundT, pair[0], "S")],
                      -atomsToIndex[(roundT + 1, pair[0], "Q")]]
    # [atomsToIndex[(roundT + 1, neighbor, "Q")],    atomsToIndex[(roundT, neighbor, "S")]]
    if roundT + 1 <= b - 1:
        deleteEffects += [atomsToIndex[(roundT + 1, pair[1], "H")], atomsToIndex[(roundT + 1, pair[1], "Q")],
                          atomsToIndex[(roundT + 1, pair[1], "I")],
                          atomsToIndex[(roundT + 1, pair[1], "U")]]
        addEffects += [atomsToIndex[(roundT + 1, pair[1], "S")]]
    for condition in preConditions:
        clauses.append([-actionIndex, condition])
    return clauses, preConditions, addEffects, deleteEffects


def modelAgentQAction(b, actionIdx, roundT, indexQ, atomsToIndex):
    actionClauses, deleteEffects, addEffects, preConditions = [], [], [], []
    preConditions.append(atomsToIndex[(roundT, indexQ, "S")])
    if roundT + 1 <= b - 1:
        addEffects.append(atomsToIndex[(roundT + 1, indexQ, "Q")])
        deleteEffects += [atomsToIndex[(roundT + 1, indexQ, "S")], atomsToIndex[(roundT + 1, indexQ, "H")],
                          atomsToIndex[(roundT + 1, indexQ, "I")], atomsToIndex[(roundT + 1, indexQ, "U")]]

    for condition in preConditions:
        actionClauses.append([-actionIdx, condition])
    return actionClauses, preConditions, addEffects, deleteEffects


def modelAgentVAction(b, actionIdx, roundT, indexV, atomsToIndex):
    actionClauses, deleteEffects, addEffects, preConditions = [], [], [], []
    preConditions.append(atomsToIndex[(roundT, indexV, "H")])
    for t in range(1, b):
        if roundT + t <= b - 1:
            addEffects.append(atomsToIndex[(roundT + t, indexV, "I")])
            deleteEffects += [atomsToIndex[(roundT + t, indexV, "H")], atomsToIndex[(roundT + t, indexV, "Q")],
                              atomsToIndex[(roundT + t, indexV, "H")], atomsToIndex[(roundT + t, indexV, "U")]]

    for condition in preConditions:
        actionClauses.append([-actionIdx, condition])
    return actionClauses, preConditions, addEffects, deleteEffects
