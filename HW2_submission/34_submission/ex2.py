ids = ['315880575', '205847932']


def get_neighbors(coordinates, board_size, exclude=tuple()):
    # gets the coordinates of the neighboring tile
    neighbors = list()
    if coordinates[0] != 0 and (coordinates[0] - 1, coordinates[1]) not in exclude:
        neighbors.append((coordinates[0] - 1, coordinates[1]))
    if coordinates[1] != 0 and (coordinates[0], coordinates[1] - 1) not in exclude:
        neighbors.append((coordinates[0], coordinates[1] - 1))
    if coordinates[0] != board_size[0] - 1 and (coordinates[0] + 1, coordinates[1]) not in exclude:
        neighbors.append((coordinates[0] + 1, coordinates[1]))
    if coordinates[1] != board_size[1] - 1 and (coordinates[0], coordinates[1] + 1) not in exclude:
        neighbors.append((coordinates[0], coordinates[1] + 1))
    return neighbors  # left down right up


def get_neighbors_neighbors(coordinates, board_size, exclude=tuple()):
    non = list()
    neighbors = get_neighbors(coordinates, board_size, exclude)
    for n in neighbors:
        nn = get_neighbors(n, board_size, exclude)
        non.append([])
        for tile in nn:
            if tile not in non and tile != coordinates:
                non[-1].append(tile)
    return non  # [[LL, LD, LU], [DL, DD, DR], [RD, RR, RU], [UL, UU, UR]]


def get_tile_status(input, tile, turn=0, exclude=tuple()):  # input is input and tile is a tuple representing the tile requested
    if input["observations"][turn][tile[0]][tile[1]] != '?':
        return input["observations"][turn][tile[0]][tile[1]]

    unknown = True
    for n in range(len(input["observations"])):
        if input["observations"][n][tile[0]][tile[1]] == 'U':
            return "U"
        if input["observations"][n][tile[0]][tile[1]] != '?':
            unknown = False

    exclude += tuple([tile])
    neighbors = get_neighbors(tile, (len(input["observations"][0]), len(input["observations"][0][0])), exclude)
    neighbors_neighbors = get_neighbors_neighbors(tile,
                                                  (len(input["observations"][0]), len(input["observations"][0][0])),
                                                  exclude)
    n_curr_status = [n for n in [get_tile_status(input, t, turn, exclude) for t in neighbors]]
    nn_curr_status = list()
    for nn in neighbors_neighbors:
        nn_curr_status.append([n for n in [get_tile_status(input, t, turn, exclude) for t in nn]])

    # attempting to see if at any point the tiles around it were affected
    infected = (False, 0)
    ever_infected = False
    tn = 0
    while unknown and tn < len(input["observations"]):
        infected = (True, infected[1]-1) if infected[1] > 1 else (False, 0)
        n_cr_stts = [n for n in [get_tile_status(input, t, tn, exclude) for t in neighbors]]
        nn_cr_stts = list()
        for nn in neighbors_neighbors:
            nn_cr_stts.append([n for n in [get_tile_status(input, t, tn, exclude) for t in nn]])

        if tn > 0:
            n_pre_stts = [n for n in [get_tile_status(input, t, tn - 1, exclude) for t in neighbors]]
            if any([n == "S" for n in n_pre_stts]):
                if not infected[0]:
                    infected = (True, 3)
                    ever_infected = True

        if tn < len(input["observations"]) - 1:
            n_nxt_stts = [n for n in [get_tile_status(input, t, tn + 1, exclude) for t in neighbors]]
            for i in range(len(neighbors)):
                # if a nieghbor becomes sick and its for certain that it wasnt any other tile that infected it
                if n_cr_stts[i] == "H" and n_nxt_stts[i] == "S" and all([n != "S" for n in nn_cr_stts[i]]):
                    unknown = False  # not Uninhabited situation
                elif infected[0] and n_cr_stts[i] == "H" and n_nxt_stts[i] == "H" \
                        and all([n != "S" for n in nn_cr_stts[i]]):
                    return "U"
        tn += 1
    if unknown:
        if turn > 2 and not ever_infected:
            return "Not S"
        return "None"

    if turn > 0:
        n_prev_status = [n for n in [get_tile_status(input, t, turn-1, exclude) for t in neighbors]]
        if get_tile_status(input, tile, turn-1, exclude) == 'S' and turn < 3:
            return "S"
        if get_tile_status(input, tile, turn-1, exclude) == 'H':
            if all([n != "S" for n in n_prev_status]):
                return "H"
        if turn >= 3:
            if all([i == "S" for i in [get_tile_status(input, tile, n, exclude) for n in range(turn-3, turn)]]):
                return "H"
            elif get_tile_status(input, tile, turn-1, exclude) == 'S':
                return "S"
        # did the tile get infected?
        if any([n == "S" for n in n_prev_status]):
            return "S"

    if turn < len(input["observations"]) - 1:
        n_next_status = [n for n in [get_tile_status(input, t, turn + 1, exclude) for t in neighbors]]
        for i in range(len(neighbors)):
            # if a nieghbor becomes sick and its for certain that it wasn't any other tile that infected it
            if n_curr_status[i] == "H" and n_next_status[i] == "S" and all([n != "S" for n in nn_curr_status[i]]):
                return "S"
            if n_curr_status[i] == "H" and n_next_status[i] == "H" and all([n != "S" for n in nn_curr_status[i]]):
                return "H"

    return "Not U"


def solve_problem(input):
    results = dict()
    for query in input["queries"]:
        result = get_tile_status(input, query[0], query[1])
        if result == "None":
            results[query] = '?'
        elif result == "Not S":
            results[query] = 'F' if query[2] == 'S' else '?'
        elif result == "Not U":
            results[query] = 'F' if query[2] == 'U' else '?'
        elif result == query[2]:
            results[query] = 'T'
        elif result != query[2]:
            results[query] = 'F'
        else:
            results[query] = '?'
    return results
