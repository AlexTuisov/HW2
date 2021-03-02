import pysat
from pysat.solvers import Solver

ids = ['315691451', '205756117']


# create the database
def create_database(days, row_size, colums_size, db):
    i = 1
    for day in range(days):
        for row in range(row_size):
            for column in range(colums_size):
                db.append([i, i + 1, i + 2, i + 3, i + 4, i + 5, i + 6, i + 7])
                i += 8

#set s to be s1 or s2 or s3
def set_relevant_s(location, day, db, board_size, data_knowlede):
        if day >= 2 and [db[location - board_size][2]] in data_knowlede and [db[location - 2 * board_size][1]] in data_knowlede:
            s3 = db[location][3]
            data_knowlede.append([s3])
            data_knowlede.extend(
                [[-s3, -(s3 - 1)], [-s3, -(s3 - 2)], [-s3, -(s3 - 3)], [-s3, -(s3 + 1)],
                 [-s3, -(s3 + 2)], [-s3, -(s3 + 3)], [-s3, -(s3 + 4)]])

        elif day >= 1 and ([db[location - board_size][1]] in data_knowlede):
            s2 = db[location][2]
            data_knowlede.append([s2])
            data_knowlede.extend(
                [[-s2, -(s2 - 1)], [-s2, -(s2 - 2)], [-s2, -(s2 + 1)], [-s2, -(s2 + 2)],
                 [-s2, -(s2 + 3)], [-s2, -(s2 + 4)], [-s2, -(s2 + 5)]])

        else:
            s = db[location][1]
            data_knowlede.append([s])
            data_knowlede.extend(
                [[-s, -(s - 1)], [-s, -(s + 1)], [-s, -(s + 2)], [-s, -(s + 3)], [-s, -(s + 4)],
                 [-s, -(s + 5)], [-s, -(s + 6)]])

#initial known states and set only one state possible per cell
def initial_states(board_size, days, row_size, colums_size, problem, db, data_knowlede ):
    # אתחול התאים הנתונים לערך אמת, וגם הגדרה שלכל תא יש רק מצב אפשרי אחד
    location = 0

    for day in range(days):
        for row in range(row_size):
            for column in range(colums_size):
                state = problem["observations"][day][row][column]
                h = db[location][0]
                s = db[location][1]
                q = db[location][4]
                i = db[location][6]
                u = db[location][7]

                if state == "H":
                    data_knowlede.append([h])
                    data_knowlede.extend(
                        [[-h, -(h + 1)], [-h, -(h + 2)], [-h, -(h + 3)], [-h, -(h + 4)],
                         [-h, -(h + 5)], [-h, -(h + 6)], [-h, -(h + 7)]])

                if state == "S":
                    set_relevant_s(location, day, db, board_size, data_knowlede)

                if state == "Q":
                    if day >= 1 and ([db[location - board_size][4]] in data_knowlede):
                        q2 = db[location][5]
                        data_knowlede.append([q2])
                        data_knowlede.extend(
                            [[-q2, -(q2 - 5)], [-q2, -(q2 - 4)], [-q2, -(q2 - 3)], [-q2, -(q2 - 2)],
                             [-q2, -(q2 - 1)], [-q2, -(q2 + 1)], [-q2, -(q2 + 2)]])
                    else:
                        data_knowlede.append([q])
                        data_knowlede.extend(
                            [[-q, -(q - 4)], [-q, -(q - 3)], [-q, -(q - 2)], [-q, -(q - 1)],
                             [-q, -(q + 1)], [-q, -(q + 2)], [-q, -(q + 3)]])

                if state == "I":
                    data_knowlede.append([i])
                    data_knowlede.extend(
                        [[-i, -(i - 6)], [-i, -(i - 5)], [-i, -(i - 4)], [-i, -(i - 3)],
                         [-i, -(i - 2)], [-i, -(i - 1)], [-i, -(i + 1)]])

                if state == "U":
                    data_knowlede.append([u])
                    data_knowlede.extend(
                        [[-u, -(u - 7)], [-u, -(u - 6)], [-u, -(u - 5)], [-u, -(u - 4)],
                         [-u, -(u - 3)], [-u, -(u - 2)], [-u, -(u - 1)]])

                if state == '?':
                    data_knowlede.extend(
                        [[-h, -(h + 1)], [-h, -(h + 2)], [-h, -(h + 3)], [-h, -(h + 4)],
                         [-h, -(h + 5)], [-h, -(h + 6)], [-h, -(h + 7)],
                         [-s, -(s - 1)], [-s, -(s + 1)], [-s, -(s + 2)], [-s, -(s + 3)],
                         [-s, -(s + 4)], [-s, -(s + 5)], [-s, -(s + 6)],
                         [-q, -(q - 4)], [-q, -(q - 3)], [-q, -(q - 2)], [-q, -(q - 1)],
                         [-q, -(q + 1)], [-q, -(q + 2)], [-q, -(q + 3)],
                         [-i, -(i - 6)], [-i, -(i - 5)], [-i, -(i - 4)], [-i, -(i - 3)],
                         [-i, -(i - 2)], [-i, -(i - 1)], [-i, -(i + 1)],
                         [-u, -(u - 7)], [-u, -(u - 6)], [-u, -(u - 5)], [-u, -(u - 4)],
                         [-u, -(u - 3)], [-u, -(u - 2)], [-u, -(u - 1)]])

                location += 1


def curr_h_next_s_then_neighbor_s(board_size, days, row_size, colums_size, problem, db, data_knowlede):
    # אם תא בריא עכשיו ובתור הבא יהיה חולה, אזי אחד מהשכנים שלו היה חולה

    location = 0

    for day in range(days - 1):
        for row in range(row_size):
            for column in range(colums_size):
                state = problem["observations"][day][row][column]
                curr_h = db[location][0]
                next_s = db[location + board_size][1]

                if [curr_h] in data_knowlede and [next_s] in data_knowlede:

                    # אם אני לא ידוע וכל השכנים שלי פרט ל1 הם לא חולים, אז זה אומר שאני חולה בוודאות
                    # ? right
                    num_nighbors = 0
                    count = 0
                    if column < (colums_size - 1) and problem["observations"][day][row][
                        column + 1] == '?':
                        num_nighbors += 1

                        if row < (row_size - 1):
                            num_nighbors += 1
                            if problem["observations"][day][row + 1][column] != 'S':
                                count += 1

                        if column <= (colums_size - 1) and column >= 1:
                            num_nighbors += 1
                            if problem["observations"][day][row][column - 1] != 'S':
                                count += 1

                        if row <= (row_size - 1) and row >= 1:
                            num_nighbors += 1
                            if problem["observations"][day][row - 1][column] != 'S':
                                count += 1

                        if (num_nighbors - count == 1):
                            loc = location + 1
                            set_relevant_s(loc, day, db, board_size, data_knowlede)

                    # ? down
                    num_nighbors_d = 0
                    count_d = 0
                    if row < (row_size - 1) and problem["observations"][day][row + 1][
                        column] == '?':
                        num_nighbors_d += 1

                        if column < (colums_size - 1):
                            num_nighbors_d += 1
                            if problem["observations"][day][row][column + 1] != 'S':
                                count_d += 1

                        if column <= (colums_size - 1) and column >= 1:
                            num_nighbors_d += 1
                            if problem["observations"][day][row][column - 1] != 'S':
                                count_d += 1

                        if row <= (row_size - 1) and row >= 1:
                            num_nighbors_d += 1
                            if problem["observations"][day][row - 1][column] != 'S':
                                count_d += 1

                        if (num_nighbors_d - count_d == 1):
                            loc = location + colums_size
                            set_relevant_s(loc, day, db, board_size, data_knowlede)

                    # ? up
                    num_nighbors_u = 0
                    count_u = 0
                    if row <= (row_size - 1) and row >= 1 and problem["observations"][day][row - 1][
                        column] == '?':
                        num_nighbors_u += 1

                        if row < (row_size - 1):
                            num_nighbors_u += 1
                            if problem["observations"][day][row + 1][column] != 'S':
                                count_u += 1

                        if column <= (colums_size - 1) and column >= 1:
                            num_nighbors_u += 1
                            if problem["observations"][day][row][column - 1] != 'S':
                                count_u += 1

                        if column < (colums_size - 1):
                            num_nighbors_u += 1
                            if problem["observations"][day][row][column + 1] != 'S':
                                count_u += 1

                        if (num_nighbors_u - count_u == 1):
                            loc = location - colums_size
                            set_relevant_s(loc, day, db, board_size, data_knowlede)

                    # ? left
                    num_nighbors_l = 0
                    count_l = 0
                    if column <= (colums_size - 1) and column >= 1 and \
                            problem["observations"][day][row][column - 1] == '?':
                        num_nighbors_l += 1

                        if row < (row_size - 1):
                            num_nighbors_l += 1
                            if problem["observations"][day][row + 1][column] != 'S':
                                count_l += 1

                        if column < (colums_size - 1):
                            num_nighbors_l += 1
                            if problem["observations"][day][row][column + 1] != 'S':
                                count_l += 1

                        if row <= (row_size - 1) and row >= 1:
                            num_nighbors_l += 1
                            if problem["observations"][day][row - 1][column] != 'S':
                                count_l += 1

                        if (num_nighbors_l - count_l == 1):
                            loc = location - 1
                            set_relevant_s(loc, day, db, board_size, data_knowlede)

                location += 1


def curr_h_neibor_s_then_next_s(board_size, days, row_size, colums_size, problem, db, data_knowlede):
    # הדבקה:אם תא בריא ואחד השכנים חולה, אזי התא יהפוך לחולה
    # אם תא בריא ואין לו שכנים חולים הוא לא יהפוך לחולה

    location = 0

    for day in range(days - 1):
        for row in range(row_size):
            for column in range(colums_size):
                state = problem["observations"][day][row][column]
                curr_h = db[location][0]

                if [curr_h] in data_knowlede:
                    loc_r = location + 1
                    loc_d = location + colums_size
                    loc_l = location - 1
                    loc_u = location - colums_size

                    next_s = db[location + board_size][1]

                    # set the nieghbers if there are exists, each nieghbor could be either of the 3 states:s1,s2,s3
                    if column < (colums_size - 1) and (
                            [db[loc_r][1]] in data_knowlede or [db[loc_r][2]] in data_knowlede or [db[loc_r][3]] in data_knowlede):
                        data_knowlede.append([next_s])
                        data_knowlede.extend([[-next_s, -(next_s - 1)], [-next_s, -(next_s + 1)],
                                              [-next_s, -(next_s + 2)], [-next_s, -(next_s + 3)],
                                              [-next_s, -(next_s + 4)], [-next_s, -(next_s + 5)],
                                              [-next_s, -(next_s + 6)]])

                    elif row < (row_size - 1) and (
                            [db[loc_d][1]] in data_knowlede or [db[loc_d][2]] in data_knowlede or [db[loc_d][3]] in data_knowlede):
                        data_knowlede.append([next_s])
                        data_knowlede.extend([[-next_s, -(next_s - 1)], [-next_s, -(next_s + 1)],
                                              [-next_s, -(next_s + 2)], [-next_s, -(next_s + 3)],
                                              [-next_s, -(next_s + 4)], [-next_s, -(next_s + 5)],
                                              [-next_s, -(next_s + 6)]])


                    elif column <= (colums_size - 1) and column >= 1 and (
                            [db[loc_l][1]] in data_knowlede or [db[loc_l][2]] in data_knowlede or [db[loc_l][3]] in data_knowlede):
                        data_knowlede.append([next_s])
                        data_knowlede.extend([[-next_s, -(next_s - 1)], [-next_s, -(next_s + 1)],
                                              [-next_s, -(next_s + 2)], [-next_s, -(next_s + 3)],
                                              [-next_s, -(next_s + 4)], [-next_s, -(next_s + 5)],
                                              [-next_s, -(next_s + 6)]])


                    elif row <= (row_size - 1) and row >= 1 and (
                            [db[loc_u][1]] in data_knowlede or [db[loc_u][2]] in data_knowlede or [db[loc_u][3]] in data_knowlede):
                        data_knowlede.append([next_s])
                        data_knowlede.extend([[-next_s, -(next_s - 1)], [-next_s, -(next_s + 1)],
                                              [-next_s, -(next_s + 2)], [-next_s, -(next_s + 3)],
                                              [-next_s, -(next_s + 4)], [-next_s, -(next_s + 5)],
                                              [-next_s, -(next_s + 6)]])


                    else:
                        next_h = db[location + board_size][0]
                        data_knowlede.append([next_h])
                        data_knowlede.extend([[-next_h, -(next_h + 1)], [-next_h, -(next_h + 2)],
                                              [-next_h, -(next_h + 3)], [-next_h, -(next_h + 4)],
                                              [-next_h, -(next_h + 5)], [-next_h, -(next_h + 6)],
                                              [-next_h, -(next_h + 7)]])

                location += 1



def fix_mistakes(board_size, days, row_size, colums_size, problem, db, data_knowlede):
    # תיקון טעויות
    location = 0
    for day in range(days):
        for row in range(row_size):
            for column in range(colums_size):
                state = problem["observations"][day][row][column]
                s1 = db[location][1]
                s2 = db[location][2]
                s3 = db[location][3]

                if state == "S":
                    if day >= 2 and [db[location - board_size][2]] in data_knowlede and [
                        db[location - 2 * board_size][1]] in data_knowlede:
                        if [s2] in data_knowlede:
                            data_knowlede.remove([s2])
                            data_knowlede.append([s3])
                        elif [s1] in data_knowlede:
                            data_knowlede.remove([s1])
                            data_knowlede.append([s3])

                    elif day >= 1 and ([db[location - board_size][1]] in data_knowlede):
                        if [s1] in data_knowlede:
                            data_knowlede.remove([s1])
                            data_knowlede.append([s2])

                location += 1


def illness_expires(board_size, days, row_size, colums_size, db, data_knowlede):
    # פגות תוקף של המחלה
    location = days * row_size * colums_size - 1
    if days >= 4:
        for day in range(days, 3, -1):
            for row in range(row_size):
                for column in range(colums_size):
                    h = db[location][0]
                    s3 = db[location - board_size][3]
                    s2 = db[location - 2 * board_size][2]
                    s1 = db[location - 3 * board_size][1]

                    if [s1] in data_knowlede and [s2] in data_knowlede and [s3] in data_knowlede:
                        data_knowlede.append([h])
                    location -= 1

def quarentine_expires(board_size, days, row_size, colums_size, db, data_knowlede):
    # פגות תוקף של הבידודים
    location = days * row_size * colums_size - 1
    if days >= 3:
        for day in range(days, 2, -1):
            for row in range(row_size):
                for column in range(colums_size):
                    h = db[location][0]
                    q2 = db[location - board_size][5]
                    q1 = db[location - 2 * board_size][4]

                    if [q1] in data_knowlede and [q2] in data_knowlede:
                        data_knowlede.append([h])
                    location -= 1

def U_and_I_stay_this_way(board_size, days, row_size, colums_size, db, data_knowlede):
    # תאים ריקים ומחוסנים נשארים במצבם גם בתורות הבאים
    location = 0
    for day in range(days - 1):
        for row in range(row_size):
            for column in range(colums_size):
                curr_i = db[location][6]
                curr_u = db[location][7]
                if [curr_i] in data_knowlede:
                    next_i = db[location + board_size][6]
                    data_knowlede.append([next_i])
                elif [curr_u] in data_knowlede:
                    next_u = db[location + board_size][7]
                    data_knowlede.append([next_u])
                location += 1

def previues_to_U_and_I(board_size, days, row_size, colums_size, db, data_knowlede):
    # תאים ריקים היו כך גם בתור הקודם. תאים מחוסנים היו בתור הקודם מחוסנים או בריאים.
    location = days * row_size * colums_size - 1
    for day in range(days, 1, -1):
        for row in range(row_size):
            for column in range(colums_size):
                curr_u = db[location][7]
                if [curr_u] in data_knowlede:
                    prev_u = db[location - board_size][7]
                    data_knowlede.append([prev_u])

                curr_i = db[location][6]
                if [curr_i] in data_knowlede:
                    prev_i = db[location - board_size][6]
                    prev_h = db[location - board_size][0]
                    data_knowlede.append([prev_i, prev_h, -curr_i])

                location -= 1

def next_h(board_size, days, row_size, colums_size, db, data_knowlede):
    # תא בריא יכול להיות בתור הבא תא בריא, תא חולה או תא מחוסן
    location = 0
    for day in range(days - 1):
        for row in range(row_size):
            for column in range(colums_size):
                # next possible states for helthy cell
                curr_h = db[location][0]
                if [curr_h] in data_knowlede:
                    next_h = db[location + board_size][0]
                    next_s = db[location + board_size][1]
                    next_i = db[location + board_size][6]

                    data_knowlede.append([next_h, next_s, next_i, -curr_h])

                location += 1

def previues_h(board_size, days, row_size, colums_size, db, data_knowlede):
    # תא בריא היה בתור הקודם בריא או חולה או מבודד
    location = days * row_size * colums_size - 1
    for day in range(days, 1, -1):
        for row in range(row_size):
            for column in range(colums_size):
                curr_h = db[location][0]
                prev_q2 = db[location - board_size][5]
                prev_s3 = db[location - board_size][3]
                prev_h = db[location - board_size][0]

                data_knowlede.append([prev_h, prev_s3, prev_q2, -curr_h])

                location -= 1

def previues_s(board_size, days, row_size, colums_size, db, data_knowlede):
    # תא חולה היה בתור הקודם חולה או בריא
    location = days * row_size * colums_size - 1
    for day in range(days, 1, -1):
        for row in range(row_size):
            for column in range(colums_size):
                curr_s3 = db[location][3]
                curr_s2 = db[location][2]
                curr_s1 = db[location][1]

                prev_s1 = db[location - board_size][1]
                prev_s2 = db[location - board_size][2]
                prev_h = db[location - board_size][0]

                data_knowlede.extend([[prev_h, -curr_s1], [prev_s2, -curr_s3], [prev_s1, -curr_s2]])

                location -= 1

def previues_q(board_size, days, row_size, colums_size, db, data_knowlede):
    # תא מבודד היה בתור הקודם מבודד או חולה
    location = days * row_size * colums_size - 1
    for day in range(days, 1, -1):
        for row in range(row_size):
            for column in range(colums_size):
                curr_q1 = db[location][4]
                curr_q2 = db[location][5]

                prev_q1 = db[location - board_size][4]
                prev_s1 = db[location - board_size][1]
                prev_s2 = db[location - board_size][2]
                prev_s3 = db[location - board_size][3]

                data_knowlede.extend([[prev_q1, -curr_q2], [prev_s1, prev_s2, prev_s3, -curr_q1]])

                location -= 1

def next_q(board_size, days, row_size, colums_size, db, data_knowlede):
    # תא מבודד יכול להיות בתור הבא מבודד או בריא, בהתאם ליום הבידוד שלו
    location = 0
    for day in range(days - 1):
        for row in range(row_size):
            for column in range(colums_size):
                # next possible states for sick cell
                curr_q1 = db[location][4]
                curr_q2 = db[location][5]

                next_q2 = db[location + board_size][5]
                next_h = db[location + board_size][0]

                data_knowlede.extend([[next_q2, -curr_q1], [next_h, -curr_q2]])

                location += 1

def next_s(board_size, days, row_size, colums_size, db, data_knowlede):
    # תא חולה יכול להיות בתור הבא: חולה, בריא, או מבודד בהתאם ליום החולי שלו
    location = 0
    for day in range(days - 1):
        for row in range(row_size):
            for column in range(colums_size):
                # next possible states for sick cell
                curr_s1 = db[location][1]
                curr_s2 = db[location][2]
                curr_s3 = db[location][3]

                if [curr_s1] in data_knowlede:
                    next_s2 = db[location + board_size][2]
                    data_knowlede.append([next_s2])
                elif [curr_s2] in data_knowlede:
                    next_s3 = db[location + board_size][3]
                    data_knowlede.append([next_s3])
                elif [curr_s3] in data_knowlede:
                    next_h = db[location + board_size][0]

                location += 1

def set_dictionary_according_to_queries(days, row_size, colums_size, queries, db, sulotion, sulotion_exist, s, dict):
    # פתרון הבעיה והחזרת המילון המתאים עם התשובות לשאילתות
    location = 0

    for i in range(len(queries)):
        for day in range(days):
            for row in range(row_size):
                for column in range(colums_size):
                    query_row = queries[i][0][0]
                    query_culumn = queries[i][0][1]
                    query_day = queries[i][1]
                    query_check = queries[i][2]

                    if query_row == row and query_culumn == column and query_day == day:

                        if sulotion_exist:

                            if query_check == 'H':
                                check_h = db[location][0]
                                if check_h in sulotion:
                                    dict[((query_row, query_culumn), query_day, 'H')] = 'T'
                                elif s.solve(assumptions=[check_h]) == True:
                                    dict[((query_row, query_culumn), query_day, 'H')] = '?'
                                else:
                                    dict[((query_row, query_culumn), query_day, 'H')] = 'F'


                            elif query_check == 'S':
                                check_s1 = db[location][1]
                                check_s2 = db[location][2]
                                check_s3 = db[location][3]
                                if check_s1 in sulotion or check_s2 in sulotion or check_s3 in sulotion:
                                    dict[((query_row, query_culumn), query_day, 'S')] = 'T'
                                elif (s.solve(assumptions=[check_s1])) == True or s.solve(
                                        assumptions=[check_s2]) == True or s.solve(
                                        assumptions=[check_s3]) == True:
                                    dict[((query_row, query_culumn), query_day, 'S')] = '?'
                                else:
                                    dict[((query_row, query_culumn), query_day, 'S')] = 'F'


                            elif query_check == 'Q':
                                check_q1 = db[location][4]
                                check_q2 = db[location][5]
                                if check_q1 in sulotion or check_q2 in sulotion:
                                    dict[((query_row, query_culumn), query_day, 'Q')] = 'T'
                                elif (s.solve(assumptions=[check_q1])) == True or s.solve(
                                        assumptions=[check_q2]) == True:
                                    dict[((query_row, query_culumn), query_day, 'Q')] = '?'
                                else:
                                    dict[((query_row, query_culumn), query_day, 'Q')] = 'F'


                            elif query_check == 'I':
                                check_i = db[location][6]
                                if check_i in sulotion:
                                    dict[((query_row, query_culumn), query_day, 'I')] = 'T'
                                elif s.solve(assumptions=[check_i]) == True:
                                    dict[((query_row, query_culumn), query_day, 'I')] = '?'
                                else:
                                    dict[((query_row, query_culumn), query_day, 'I')] = 'F'


                            elif query_check == 'U':
                                check_u = db[location][7]
                                if check_u in sulotion:
                                    dict[((query_row, query_culumn), query_day, 'U')] = 'T'
                                elif s.solve(assumptions=[check_u]) == True:
                                    dict[((query_row, query_culumn), query_day, 'U')] = '?'
                                else:
                                    dict[((query_row, query_culumn), query_day, 'U')] = 'F'


                        # sulotion is None
                        else:
                            if query_check == 'H':
                                dict[((query_row, query_culumn), query_day, 'H')] = '?'
                            elif query_check == 'S':
                                dict[((query_row, query_culumn), query_day, 'S')] = '?'
                            elif query_check == 'Q':
                                dict[((query_row, query_culumn), query_day, 'Q')] = '?'
                            elif query_check == 'I':
                                dict[((query_row, query_culumn), query_day, 'I')] = '?'
                            elif query_check == 'U':
                                dict[((query_row, query_culumn), query_day, 'U')] = '?'

                    location += 1
        location = 0



def solve_problem(input):

    """initialize variables"""
    num_police = input["police"]
    num_medics = input["medics"]
    days = len(input["observations"])
    colums_size = len(input["observations"][0][0])
    row_size = len(input["observations"][0])
    queries = input["queries"]
    board_size = row_size * colums_size

    """create the database"""
    db = []
    create_database(days, row_size, colums_size, db)

    """create the data_knowlede"""
    data_knowlede = []

    initial_states(board_size, days, row_size, colums_size, input, db, data_knowlede)
    curr_h_next_s_then_neighbor_s(board_size, days, row_size, colums_size, input, db, data_knowlede)
    curr_h_neibor_s_then_next_s(board_size, days, row_size, colums_size, input, db, data_knowlede)
    fix_mistakes(board_size, days, row_size, colums_size, input, db, data_knowlede)
    illness_expires(board_size, days, row_size, colums_size, db, data_knowlede)
    quarentine_expires(board_size, days, row_size, colums_size, db, data_knowlede)
    U_and_I_stay_this_way(board_size, days, row_size, colums_size, db, data_knowlede)
    previues_to_U_and_I(board_size, days, row_size, colums_size, db, data_knowlede)
    next_h(board_size, days, row_size, colums_size, db, data_knowlede)
    previues_h(board_size, days, row_size, colums_size, db, data_knowlede)
    previues_s(board_size, days, row_size, colums_size, db, data_knowlede)
    previues_q(board_size, days, row_size, colums_size, db, data_knowlede)
    next_q(board_size, days, row_size, colums_size, db, data_knowlede)
    next_s(board_size, days, row_size, colums_size, db, data_knowlede)

    """"solve the problem"""
    s = Solver()
    dict={}

    for i in data_knowlede:
        s.add_clause(i)

    sulotion_exist = s.solve()
    sulotion = s.get_model()

    set_dictionary_according_to_queries(days, row_size, colums_size, queries, db, sulotion, sulotion_exist, s, dict)

    return(dict)



