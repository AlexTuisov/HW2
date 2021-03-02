ids = ['314936568']

def neighbors(x, y, x_range, y_range):
    lis = []
    
    if x != 0:
        lis.append([x-1, y])
    if x != x_range-1:
        lis.append([x+1, y])
        
    if y != 0:
        lis.append([x, y-1])
    if y != y_range-1:
        lis.append([x, y+1])
        
        
    return lis

def make_board(board, args):
    #print(board, args)
    if len(args) == 0:
        yield board
    elif len(args) == 1:
        for i in args[0][2]:
            board[args[0][0]][args[0][1]] = i
            yield board
    else:
        for i in args[0][2]:
            board[args[0][0]][args[0][1]] = i
            options = make_board(board, args[1:])
            for t in options:
                yield t 
                

def check_next(board, nxt, x_range, y_range):
    can = True
    HtS = []
    HtH = []
    
    changes = {}
    
    for x in range(x_range):
        for y in range(y_range):
            if nxt[x][y] == 'U' and board[x][y] != 'U':
                can = False
                return can
            elif nxt[x][y] != 'U' and board[x][y] == 'U':
                can = False
                return can
            if board[x][y] == 'H' and nxt[x][y] =='S':
                HtS.append([(x,y)])
            elif board[x][y] == 'H' and nxt[x][y] =='H':
                HtH.append([(x,y)])
            elif board[x][y] in ['IH', 'I'] and nxt[x][y] == '?':
                changes[(x,y)] = 'I'
            elif board[x][y] in ['IH', 'I'] and nxt[x][y] != 'I':
                can = False
                return can
            elif board[x][y] not in ['Q', 'QS'] and nxt[x][y] == 'Q':
                can = False
                return can
            elif board[x][y] == 'QS' and nxt[x][y] == '?':
                changes[(x,y)] = 'Q'
            elif board[x][y] == 'QS' and nxt[x][y] != 'Q':
                can = False
                return can
            elif board[x][y] != 'U' and nxt[x][y] == 'U':
                can = False
                return can
            elif nxt[x][y] == '?':
                changes[(x,y)] = ['H', 'S', 'U']
    
    for point in HtS:
        n = neighbors(point[0][0], point[0][1], x_range, y_range)
        flag = True
        for ne in n:
            if board[ne[0]][ne[1]] == 'S':
                flag = False
                
        if flag:
            can = False
            return can
    
    for point in HtH:
        n = neighbors(point[0][0], point[0][1], x_range, y_range)
        flag = True
        for ne in n:
            if board[ne[0]][ne[1]] == 'S':
                flag = False
                
        if not flag:
            can = False
            return can
        
    if can:
        return changes

def replace(board, r, w, num, lis, must_use = True):
    if num == 0:
        #print('non', num)
        yield board
    elif num >= len(lis):
        #print('ere', num)
        if (len(lis) == 1 and not must_use) or lis == []:
            yield board
        elif not must_use:
            opt_out = replace(board, r, w, num, lis[1:])
            for op in opt_out:
                yield board
        for i in lis:
            board[i[0]][i[1]] = w
        yield board
        
        for i in lis:
            board[i[0]][i[1]] = r
    else:
        #print('der', num)
        opt = replace(board, r, w, num, lis[1:])
        #print('rec', lis[0])
        for op in opt:
            yield op
        board[lis[0][0]][lis[0][1]] = w
        #print('other rec', lis[0])
        opt = replace(board, r, w, num-1, lis[1:])
        for op in opt:
            yield op
            
        board[lis[0][0]][lis[0][1]] = r
            


def solve_problem(input):
    # put your solution here, remember the format needed
    
    
    pol = input['police']
    med = input['medics']
    
    battleground = input['observations']
    
    x_range = len(battleground[0])
    y_range = len(battleground[0][0])
    
    a = [list(c) for c in battleground]
    
    for index, value in enumerate(a):
        a[index] = [list(x) for x in value]
        
    for num in range(len(battleground)-1):
        for x in range(x_range):
            for y in range(y_range):
                if a[num][x][y] == 'S' and a[num+1][x][y] == 'H':
                    try:
                        a[num-2][x][y] = 'S'
                        a[num-1][x][y] = 'S'
                        a[num-3][x][y] = 'H'
                    except:
                        pass
                if a[num][x][y] == 'Q' and a[num+1][x][y] == 'H':
                    try:
                        a[num-2][x][y] = 'S'
                        a[num-1][x][y] = 'Q'
                    except:
                        pass
                    
    lis_start = []
    for x in range(x_range):
        for y in range(y_range):
            if a[0][x][y] == '?':
                lis_start.append([x, y, ['H', 'S', 'U']])
            
    maker = make_board(a[0], lis_start)
    
    turns = []
    
    turns.append({})
    
    for board in maker:
        s = []
        h = []
        if med + pol >= 0:
            for i in range(x_range):
                for t in range(y_range):
                    if board[i][t] == 'S':
                        s.append([i, t])
                    if board[i][t] == 'H':
                        h.append([i, t])
        
                        
        qs = replace(board, 'S', 'QS', pol, s)
        
        for boardi in qs:
            hi = replace(boardi, 'H', 'IH', med, h)
            
            for boardello in hi:
                res = check_next(boardello, battleground[1], x_range, y_range)
                if res != False:
                    index = (tuple([tuple(t) for t in boardello]))
                    if index not in turns[0].keys():    
                        turns[0][index] = [res, None]
                    else:
                        turns[0][index].append(None)
        
    turns.append({})
    turn = 1
    
    #for board in turns[turn]:
    #    #print(board)
    #    turns[turn][board] = check_next(board, battleground[turn+1], x_range, y_range)
    
    
    while turn < len(battleground)-1:
        for old_board in turns[turn-1]:
            lis_start = []
            for x in range(x_range):
                for y in range(y_range):
                    if battleground[turn][x][y] == '?':
                        if old_board[x][y] == 'U':
                            lis_start.append([x, y, ['U']])
                        elif old_board[x][y] == 'Q':
                            if turns[turn-1][old_board][1] != None:
                                if turns[turn-1][old_board][1][x][y] == 'QS':
                                    lis_start.append([x, y, ['Q']])
                                else:
                                    lis_start.append([x, y, ['H']])
                        elif old_board[x][y] == 'QS':
                            lis_start.append([x, y, ['Q']])
                        elif old_board[x][y] == 'IH':
                            lis_start.append([x, y, ['H']])
                        elif old_board[x][y] == 'H':
                            lis_start.append([x, y, ['H', 'S']])
                        elif old_board[x][y] == 'S':
                            if turns[turn-1][old_board][1] != None:
                                for old in range(1, len(turns[turn-1][old_board])):
                                    if turns[turn-1][old_board][old][x][y] == 'S':
                                        if turns[turn-2][turns[turn-1][old_board][old]][1] != None:
                                            for older in range(1, len(turns[turn-2][turns[turn-1][old_board][old]])):
                                                if turns[turn-2][turns[turn-1][old_board][old]][older][x][y] == 'S': ## the tower of sick people
                                                    if len(lis_start) != 0 and lis_start[-1][0] == x and lis_start[-1][1] == y and 'H' not in lis_start[-1][2]:
                                                        lis_start[-1][2].append('H')
                                                    else:
                                                        lis_start.append([x, y, ['H']])
                                                else:
                                                    if len(lis_start) != 0 and lis_start[-1][0] == x and lis_start[-1][1] == y and 'S' not in lis_start[-1][2]:
                                                        lis_start[-1][2].append('S')
                                                    else:
                                                        lis_start.append([x, y, ['S']])
                                        else:
                                            if len(lis_start) != 0 and lis_start[-1][0] == x and lis_start[-1][1] == y and 'S' not in lis_start[-1][2]:
                                                lis_start[-1][2].append('S')
                                            else:
                                                lis_start.append([x, y, ['S']])
                                    else:
                                        if len(lis_start) != 0 and lis_start[-1][0] == x and lis_start[-1][1] == y and 'S' not in lis_start[-1][2]:
                                            lis_start[-1][2].append('S')
                                        else:
                                            lis_start.append([x, y, ['S']])
                            else:
                                lis_start.append([x, y, ['S']])
                            
            if len(lis_start) == 0:
                if battleground[turn] not in turns[turn].keys():
                    turns[turn][battleground[turn]] = [False, old_board]
                else:
                    turns[turn][battleground[turn]].append(old_board)
                continue
            maker = make_board(a[turn], lis_start)
            
            for board in maker:
                #print(board)
                s = []
                h = []
                if med + pol >= 0:
                    for i in range(x_range):
                        for t in range(y_range):
                            if board[i][t] == 'S':
                                s.append([i, t])
                            if board[i][t] == 'H':
                                h.append([i, t])
        
                        
                qs = replace(board, 'S', 'QS', pol, s)
        
                for boardi in qs:
                    hi = replace(boardi, 'H', 'IH', med, h)
            
                    for boardello in hi:
                        res1 = check_next(boardello, battleground[turn+1], x_range, y_range)
                        res2 = check_next(old_board, boardello, x_range, y_range)
                        if res1 != False and res2 != False:
                            index = (tuple([tuple(t) for t in boardello]))
                            if index not in turns[0].keys():    
                                turns[turn][index] = [False, old_board]
                            else:
                                turns[turn][index].append(old_board)
                            
        turn += 1
        turns.append({})
    
    for old_board in turns[turn-1]:
        lis_start = []
        for x in range(x_range):
            for y in range(y_range):
                if battleground[turn][x][y] == '?':
                    if old_board[x][y] == 'U':
                        lis_start.append([x, y, ['U']])
                    elif old_board[x][y] == 'Q':
                        if turns[turn-1][old_board][1] != None:
                            if turns[turn-1][old_board][1][x][y] == 'QS':
                                lis_start.append([x, y, ['Q']])
                            else:
                                lis_start.append([x, y, ['H']])
                    elif old_board[x][y] == 'QS':
                        lis_start.append([x, y, ['Q']])
                    elif old_board[x][y] == 'IH':
                        lis_start.append([x, y, ['H']])
                    elif old_board[x][y] == 'H':
                        lis_start.append([x, y, ['H', 'S']])
                    elif old_board[x][y] == 'S':
                        if turns[turn-1][old_board][1] != None:
                            for old in range(1, len(turns[turn-1][old_board])):
                                if turns[turn-1][old_board][old][x][y] == 'S':
                                    if turns[turn-2][turns[turn-1][old_board][old]][1] != None:
                                        for older in range(1, len(turns[turn-2][turns[turn-1][old_board][old]])):
                                            if turns[turn-2][turns[turn-1][old_board][old]][older][x][y] == 'S': ## the tower of sick people
                                                if len(lis_start) != 0 and lis_start[-1][0] == x and lis_start[-1][1] == y and 'H' not in lis_start[-1][2]:
                                                    lis_start[-1][2].append('H')
                                                else:
                                                    lis_start.append([x, y, ['H']])
                                            else:
                                                if len(lis_start) != 0 and lis_start[-1][0] == x and lis_start[-1][1] == y and 'S' not in lis_start[-1][2]:
                                                    lis_start[-1][2].append('S')
                                                else:
                                                    lis_start.append([x, y, ['S']])
                                    else:
                                        if len(lis_start) != 0 and lis_start[-1][0] == x and lis_start[-1][1] == y and 'S' not in lis_start[-1][2]:
                                            lis_start[-1][2].append('S')
                                        else:
                                            lis_start.append([x, y, ['S']])
                                else:
                                    if len(lis_start) != 0 and lis_start[-1][0] == x and lis_start[-1][1] == y and 'S' not in lis_start[-1][2]:
                                        lis_start[-1][2].append('S')
                                    else:
                                        lis_start.append([x, y, ['S']])
                        else:
                            lis_start.append([x, y, ['S']])
                            
                        
            
        if len(lis_start) == 0:
            if battleground[turn] not in turns[turn].keys():
                turns[turn][battleground[turn]] = [True, old_board]
            else:
                turns[turn][battleground[turn]].append(old_board)
            continue
        
        maker = make_board(a[turn], lis_start)
        
        for board in maker:
            s = []
            h = []
            if med + pol >= 0:
                for i in range(x_range):
                    for t in range(y_range):
                        if board[i][t] == 'S':
                            s.append([i, t])
                        if board[i][t] == 'H':
                            h.append([i, t])
            
            
            qs = replace(board, 'S', 'QS', pol, s)
            
            for boardi in qs:
                hi = replace(boardi, 'H', 'IH', med, h)
                
                for boardello in hi:
                    res = check_next(old_board, boardello, x_range, y_range)
                    if res != False:
                        index = (tuple([tuple(t) for t in boardello]))
                        if index not in turns[0].keys():    
                            turns[turn][index] = [True, old_board]
                        else:
                            turns[turn][index].append(old_board)   
    
    qry_dic = {}
    dic_qry = {}
    dic_allowed = {'H': ['H', 'IH'], 'S':['S', 'QS'], 'I':['I'], 'U' : ['U'], 'Q':['Q']}
    
    for i in reversed(range(1, len(turns))):
        for board in turns[i]:
            if turns[i][board][0] == True:
                for ind in range(1, len(turns[i][board])):
                    turns[i-1][turns[i][board][ind]][0] = True
                    
    
    queries = input['queries']
    queries = queries if type(queries[0]) == tuple else queries[0]
    for i in queries:
        other = False
        me = False
        found_board = False
        dic_qry[i] = []
        for board in turns[i[1]]:
            if turns[i[1]][board][0] == True:
                found_board = True
                dic_qry[i].append(board[i[0][0]][i[0][1]])
                if board[i[0][0]][i[0][1]] not in dic_allowed[i[2]]:
                    other = True
                else:
                    me = True
        if not found_board:
            #print("did not find, searching more")
            for board in turns[i[1]]:
                dic_qry[i].append(board[i[0][0]][i[0][1]])
                if board[i[0][0]][i[0][1]] not in dic_allowed[i[2]]:
                    other = True
                else:
                    me = True
        
            
        qry_dic[i] = 'F' if not me else '?' if other else 'T'
            
        
        
    
    #return turns, dic_qry, qry_dic
    return qry_dic
