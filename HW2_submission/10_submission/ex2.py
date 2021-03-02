import itertools
import math
import collections
from pysat.solvers import Glucose3
from pysat.formula import CNF
import sys
sys.setrecursionlimit(20000)


ids = ['209405067', '345134696']

# MAKE SURE IF THERE AT LEAST N SICKERS, N OF THEM WILL BE IMMUNIZED
# MAYBE ADD VARIABLES WHICH COUNTS THE SICK EAH ROUND

def solve_problem(input):
    wumpus=CNF()
    basic_structure = state_structure(input)
    main_table=create_main_table(basic_structure)
    create_state_table(wumpus, basic_structure, main_table)
    # with Glucose3(bootstrap_with=wumpus.clauses) as m:
    # #     # print(len(wumpus.clauses))
    #      print(m.solve())
    res=solve_queries(input['queries'], main_table, wumpus, basic_structure)
    return res
    # put your solution here, remember the format needed

def solve_queries(query_dic, state_table, wumpus, structure):

    res_dic={}
    for query in query_dic:
        pos_wumpus=wumpus.copy()
        nu_clause=str(query[2])+str(query[0][0])+str(query[0][1])+'_'+str(query[1])
        numerized=[state_table[nu_clause]]
        bad_numerized=[-state_table[nu_clause]]
        with Glucose3(bootstrap_with=pos_wumpus.clauses) as m:
            truca=m.solve(assumptions=numerized)
            if(truca==True):
                     falska= m.solve(assumptions=bad_numerized)
                     if(truca==falska):
                          res_dic[query]="?"
                     else:
                          res_dic[query]="T"
            else:
                 res_dic[query]="F"
    return res_dic

class state_structure():
    def __init__(self, input):
        self.medic_num = input["medics"]
        self.cop_num = input["police"]
        self.width = len(input['observations'][0][0])
        self.height = len(input['observations'][0])
        self.observations = input['observations']
        self.possible_states = ['U', 'I', 'H', 'S', 'Q']
        self.number_of_turns = len(self.observations)
        # states also include not visited by cop 1 i.e M1_11_0 means vistied by cop 1



def create_state_table(wumpus, structure,state_table):
    #ADDD if exactly the number were immunized/ vaccinated/ none of the other are ill
    add_docs_and_cops(state_table, wumpus, structure)
    unknown_list=[]
    sick_list=[]
    helthy_list=[]
    for turn_number in (range(len(structure.observations))):
        unknown_this_round=[]
        sick_this_round=0
        healthy_this_roun=0
        new_immunzez=0
        not_immuned=[]
        new_quaranzez=0
        not_quaraned=[]
        if(turn_number>0):
            immune_ill_last_round=0
            sck_now=0
        if(turn_number<structure.number_of_turns-1):
            sick_countr=0
        for row in range(structure.height):
            for col in range(structure.width):
                if (structure.observations[turn_number][row][col] != '?'):

                    if(structure.observations[turn_number][row][col] == 'S'):
                        sick_this_round +=1
                    if (structure.observations[turn_number][row][col] == 'H'):
                        healthy_this_roun += 1
                    if(turn_number>0):
                        if (structure.observations[turn_number][row][col] == 'I' and
                                structure.observations[turn_number-1][row][col]=='H'):
                            new_immunzez += 1
                        if (structure.observations[turn_number][row][col] == 'Q' and
                                structure.observations[turn_number - 1][row][col] == 'S'):
                            new_quaranzez += 1
                    # print('working on cell', row , ",", col, "at turn", turn_number)
                    condi_name = (structure.observations[turn_number][row][col] + str(row)
                                  + str(col) + '_' + str(turn_number))
                    temp_var = [state_table[condi_name]]
                    wumpus.append(temp_var)
                    prop_clause(turn_number, row, col, structure.observations[turn_number][row][col], structure, wumpus, state_table)
                else:
                    if (turn_number > 0):
                        if (    structure.observations[turn_number - 1][row][col] == 'H'):
                            not_immuned.append(str(row)
                               + str(col) + '_' + str(turn_number-1))
                        if (    structure.observations[turn_number - 1][row][col] == 'S'):
                            not_quaraned.append( str(row)
                               + str(col) + '_' + str(turn_number-1))
                    prop_clause(turn_number, row, col, structure.observations[turn_number][row][col], structure, wumpus,
                                state_table, unknown=True)
                    unknown_this_round.append(str(row) + str(col) + '_' + str(turn_number))
        if(turn_number>0):
          unknown_list[turn_number-1] += (not_quaraned + not_immuned)
        unknown_list.append(unknown_this_round)
        sick_list.append(sick_this_round)
        helthy_list.append(healthy_this_roun)
        if(turn_number>0):
             make_sure_correct_immunized_quaarntined(structure, state_table, sick_list[turn_number-1],
                                                     unknown_list[turn_number-1],
                                                     new_immunzez, not_quaraned, not_immuned,
                                                     helthy_list[turn_number-1], new_quaranzez, wumpus)
             # print('unknowns_last_round:',  len(unknown_list[turn_number-1]), 'healthis last round:', helthy_list[turn_number-1], 'new immunzis:', new_immunzez)



def prop_clause(turn_number, row, col, condition, structure, wumpus, state_table, unknown=False):
    prop_dic = {}
    prop_dic['U'] = prop_clause_U
    prop_dic['S'] = prop_clause_S
    prop_dic['H'] = prop_clause_H
    prop_dic['I'] = prop_clause_I
    prop_dic['Q'] = prop_clause_Q
    if(condition=='?'):
        all_clausa=[]
        for item1 in range(len(structure.possible_states)):
                all_clausa.append((structure.possible_states[item1] + str(row)
                               + str(col) + '_' + str(turn_number)))
        all_clausa=str(to_cnf(expr(" | ".join(all_clausa))))
        all_clausa=Convert_to_literal(all_clausa, state_table)
        for clause in all_clausa:
            wumpus.append(clause)
        prop_dic['U'](turn_number, row, col, condition, structure, wumpus, state_table, unknown)
        prop_dic['H'](turn_number, row, col, condition, structure, wumpus, state_table, unknown)
        prop_dic['S'](turn_number, row, col, condition, structure, wumpus, state_table, unknown)
        prop_dic['Q'](turn_number, row, col, condition, structure, wumpus, state_table, unknown)
        prop_dic['I'](turn_number, row, col, condition, structure, wumpus, state_table, unknown)
    else:
        prop_dic[condition](turn_number, row, col, condition, structure, wumpus,state_table)

    return


def prop_clause_U(turn_number, row, col, condition, structure, wumpus, state_table, unknown=False):
    maybe_u=""
    nigrar = []
    if(unknown):
        maybe_u=('U' + str(row)
                      + str(col) + '_' + str(turn_number))+ " ==> "
    for turn_id in range(structure.number_of_turns):
        condi_name = ('U'+ str(row)
                      + str(col) + '_' + str(turn_id))
        if(unknown):
            nigrar.append(condi_name)
        else:
            temp_var = state_table[condi_name]
            wumpus.append([temp_var])
    if(unknown):
        maybe_u= maybe_u + "( "+ " & ".join(nigrar)+ " )"
        maybe_u = str(to_cnf(expr(maybe_u)))
        maybe_u = Convert_to_literal(maybe_u, state_table)
        for clause in maybe_u:
            wumpus.append(clause)

    return

def make_sure_correct_immunized_quaarntined(structure, state_table, sick_last_round, unknown_last_round,
                                            immuned_this_round, sick_this_round, healthy_this_round,
                                            healthy_last_round, quaraned_this_round, wumpus):
    #to do- add xor for  the conditions, and also add that they are quarantined now / they are immunized now
    cop_num=structure.cop_num
    medic_num=structure.medic_num
    if((sick_last_round>=cop_num and quaraned_this_round<cop_num) or (sick_last_round<cop_num and quaraned_this_round<sick_last_round)):
        for cell in unknown_last_round:
            sicko=[]
        sick_cells=[]
        #one of the earlier ones is sick fo sho and was visited by a cop
        for cell in unknown_last_round:
            sicko=[]
            copss=[]
            sicko.append('S'+cell)
            for cop_id in range(cop_num):
                copss.append('P' + str(cop_id)+'_' + cell)
            copss = '( ' + ' | '.join(copss) + ' )'
            sicko.append(copss)
            sicko.append('Q'+cell[:-1]+str(int(cell[-1])+1))
            sicko='( '+' & '.join(sicko)+ ' )'
            sick_cells.append(sicko)
        sick_cells=str(to_cnf(expr(' | '.join(sick_cells))))
        sick_cells=Convert_to_literal(sick_cells, state_table)
        for sickkk in sick_cells:
            wumpus.append(sickkk)
    else:
        for cell in unknown_last_round:
            for cop_id in range(cop_num):
                 not_sick=state_table[('~P' + str(cop_id)+'_' + cell)]
                 wumpus.append([not_sick])



    #and is quaraned now

    if (healthy_last_round >= medic_num and immuned_this_round< medic_num) or (healthy_last_round >= medic_num and immuned_this_round< medic_num):
        helt_cells=[]
        #one of the earlier ones is sick fo sho and was visited by a cop
        for cell in unknown_last_round:
            helto=[]
            copss=[]
            helto.append('H'+cell)
            for medic_id in range(medic_num):
                copss.append('M'+str(medic_id)+'_'+cell)
            copss='( '+' | '.join(copss)+ ' )'
            helto.append(copss)
            helto.append('I'+cell[:-1]+str(int(cell[-1])+1))
            helto='( '+' & '.join(helto)+ ' )'
            helt_cells.append(helto)
        helt_cells=str(to_cnf(expr(' | '.join(helt_cells))))
        helt_cells=Convert_to_literal(helt_cells, state_table)
        for helttt in helt_cells:
            wumpus.append(helttt)
        # one of the earlier ones is healthy fo sho and was visited by a medic
        #and is
    else:
        for cell in unknown_last_round:
            for medic_id in range(medic_num):
                not_sick = state_table[('~M' + str(medic_id) + '_' + cell)]
                wumpus.append([not_sick])


def prop_clause_H(turn_number, row, col, condition, structure, wumpus, state_table, unknown=False):
    '''helthy if and only if:
    1. was sick for the last 3 turns
    2. was quarantined for 2 turns
    3. was healthy last turn and no neighbours were sick, and wasn't immunized
    4. it's the first turn'''

    # ADD CLAUSE PEOPLE AROUND HIM WERE SICK BUT WERE QUARANTINED!!!!!!!!!!!!!!!!!!!!!!
    # ADD FORWARD CLAUSE- ADD WILL BE SICK IF HAS AT LEAST ONE NOT QUARANTINED
    maybe_H=('H' + str(row)
                      + str(col) + '_' + str(turn_number))+ " ==> "
    if(turn_number>0):
        all_condis=[]
        if(turn_number>=3):
            sick_prev_turns=[]
            for prev_turn in range(turn_number-3, turn_number):
                sick_prev_turns.append(('S' + str(row)    + str(col) + '_' + str(prev_turn)))
            sick_prev_turns=str(expr((" & ").join(sick_prev_turns)))
            all_condis.append(sick_prev_turns)
        if(turn_number>=2):
            quaraend_prev_turns=[]
            for prev_turn in range(turn_number - 2, turn_number):
                quaraend_prev_turns.append(('Q' + str(row) + str(col) + '_' + str(prev_turn)))
            quaraend_prev_turns = str(expr((" & ").join(quaraend_prev_turns)))
            all_condis.append(quaraend_prev_turns)
        if(turn_number>=1):
            healthy_last_turn=('H' + str(row)    + str(col) + '_' + str(turn_number-1))
            sick_neighbs=[healthy_last_turn]
            if ((row - 1) >= 0):
                barja=visited_by_cop(structure, str(row - 1), str(col), turn_number - 1)
                barja.append('~' + 'S' + str(row - 1) + str(col) + '_' + str(turn_number - 1))
                barja=str(expr(' | '.join(barja)))
                sick_neighbs.append(barja)
            if ((row + 1) < structure.height):
                barja = visited_by_cop(structure, str(row + 1), str(col), turn_number - 1)
                barja.append('~' + 'S' + str(row + 1) + str(col) + '_' + str(turn_number - 1))
                barja = str(expr(' | '.join(barja)))
                sick_neighbs.append(barja)
            if ((col - 1) >= 0):
                barja = visited_by_cop(structure, str(row), str(col - 1), turn_number - 1)
                barja.append('~' + 'S' + str(row) + str(col-1) + '_' + str(turn_number - 1))
                barja = str(expr(' | '.join(barja)))
                sick_neighbs.append(barja)
            if ((col + 1) < structure.width):
                barja = (visited_by_cop(structure, str(row), str(col + 1), turn_number - 1))
                barja.append('~' + 'S' + str(row) + str(col + 1) + '_' + str(turn_number - 1))
                barja = str(expr(' | '.join(barja)))
                sick_neighbs.append(barja)
            for medic_id in range(structure.medic_num):
               sick_neighbs.append('~'+'M' + str(medic_id) + '_' + str(row)
                                  + str(col) + '_' + str(turn_number-1))
            sick_neighbs=str(expr((" & ").join(sick_neighbs)))
            all_condis.append(sick_neighbs)
        all_condis = str(to_cnf(expr(" | ".join(all_condis))))
        if (unknown):
            maybe_H = maybe_H + "( " + all_condis+ " )"
            maybe_H = str(to_cnf(expr(maybe_H)))
            maybe_H = Convert_to_literal(maybe_H, state_table)
            for clause in maybe_H:
                wumpus.append(clause)
        else:
            all_condis=Convert_to_literal(all_condis, state_table)
            for clause in all_condis:
                wumpus.append(clause)

        #find way to propogate the quarantine

    return

def visited_by_cop(structure, row, col, turn_number, for_sick=False):
    was_sick=[('S' + row + col + '_' + str(turn_number))]
    medic_list=[]
    for cop_id in range(structure.cop_num):
        medic_list.append('P' + str(cop_id) + '_' + (row)
                            + col + '_' + str(turn_number))
    if(structure.cop_num>0):
        if(for_sick==False):
            was_sick.append('( '+' | '.join(medic_list)+ ' )')
            was_sick=' & '.join(was_sick)
            return [str(expr(was_sick))]
        else:
            medic_list=('~( '+' | '.join(medic_list)+ ' )')
            return [str(expr(medic_list))]


    else:
        return []

def visited_by_medic(structure, row, col, turn_number):
    was_sick=[('S' + row + col + '_' + str(turn_number))]
    medic_list=[]
    for cop_id in range(structure.cop_num):
        medic_list.append('P' + str(cop_id) + '_' + (row)
                            + col + '_' + str(turn_number))
    if(structure.cop_num>0):
        was_sick.append('( '+' | '.join(medic_list)+ ' )')
        was_sick=' & '.join(was_sick)
        return [str(expr(was_sick))]
    else:
        return []





def prop_clause_S(turn_number, row, col, condition, structure, wumpus, state_table, unknown=False):
    ''' a person is sick if and only if:
    1. was sick for the last turn, and wasn't quarantined
    2. was sick in the la

    st 2 turns and wasn't quarantined
    3. was healthy in the last turn and was infected by stupid neighbour
    4. wasb't sick for 3 turns in a row'''
    maybe_S=('S' + str(row)
                      + str(col) + '_' + str(turn_number))+ " ==> "

    if turn_number>0:
        all_condis=[]
        if turn_number>0:
            sick_prev_turn=[]
            sick_prev_turn.append(('S' + str(row)    + str(col) + '_' + str(turn_number-1)))
            for cop_id in range(structure.cop_num):
              sick_prev_turn.append('~'+'P' + str(cop_id) + '_' + str(row)
                                  + str(col) + '_' + str(turn_number-1))
            sick_prev_turn=str(expr((" & ").join(sick_prev_turn)))
            all_condis.append(sick_prev_turn)
        if turn_number>1:
            sick_prev_turns = []
            sick_prev_turns.append(('S' + str(row) + str(col) + '_' + str(turn_number - 1)))
            sick_prev_turns.append(('S' + str(row) + str(col) + '_' + str(turn_number - 2)))
            for cop_id in range(structure.cop_num):
                sick_prev_turns.append('~' + 'P' + str(cop_id) + '_' + str(row)
                                      + str(col) + '_' + str(turn_number - 1))
            sick_prev_turns = str(expr((" & ").join(sick_prev_turns)))
            all_condis.append(sick_prev_turns)
        if turn_number>0:
            healthy_last_turn = ('H' + str(row) + str(col) + '_' + str(turn_number - 1))
            sick_neighbs = [healthy_last_turn]
            unhealthy_list=[]
            #or was near sick but they were quarantined
            if ((row - 1) >= 0):
                sicky=[('S' + str(row - 1) + str(col) + '_' + str(turn_number - 1))]
                if(turn_number<structure.number_of_turns-1):
                  sicky+=[('~Q' + str(row - 1) + str(col) + '_' + str(turn_number))]
                sicky = str(expr(' & '.join(sicky)))
                unhealthy_list.append(sicky)
            if ((row + 1) < structure.height):
                sicky = [('S' + str(row + 1) + str(col) + '_' + str(turn_number - 1))]
                if (turn_number < structure.number_of_turns - 1):
                    sicky += [('~Q' + str(row + 1) + str(col) + '_' + str(turn_number))]
                sicky = str(expr(' & '.join(sicky)))
                unhealthy_list.append(sicky)
            if ((col - 1) >= 0):
                sicky=[('S' + str(row) + str(col-1) + '_' + str(turn_number - 1))]
                if(turn_number<structure.number_of_turns-1):
                  sicky+=[('~Q' + str(row ) + str(col-1) + '_' + str(turn_number))]
                sicky = str(expr(' & '.join(sicky)))
                unhealthy_list.append(sicky)
            if ((col + 1) < structure.width):
                sicky = [('S' + str(row) + str(col+1) + '_' + str(turn_number - 1))]
                if (turn_number < structure.number_of_turns - 1):
                    sicky += [('~Q' + str(row) + str(col+1) + '_' + str(turn_number))]
                sicky = str(expr(' & '.join(sicky)))
                unhealthy_list.append(sicky)
            unhealthy_list=str(expr((" | ").join(unhealthy_list)))
            sick_neighbs.append(unhealthy_list)
            for medic_id in range(structure.medic_num):
                sick_neighbs.append('~' + 'M' + str(medic_id) + '_' + str(row)
                                    + str(col) + '_' + str(turn_number - 1))
            sick_neighbs = str(expr((" & ").join(sick_neighbs)))
            all_condis.append(sick_neighbs)
        if turn_number>3:
            all_condis = [str(expr((" | ").join(all_condis)))]
            sick3_turns=[]
            sick3_turns.append(('S' + str(row) + str(col) + '_' + str(turn_number - 1)))
            sick3_turns.append(('S' + str(row) + str(col) + '_' + str(turn_number - 2)))
            sick3_turns.append(('S' + str(row) + str(col) + '_' + str(turn_number - 3)))
            sick3_turns = ('~'+str(expr((" & ").join(sick3_turns))))
            all_condis.append(sick3_turns)
            all_condis=(expr((" & ").join(all_condis)))
        else:
            all_condis =(expr((" | ").join(all_condis)))
        all_condis = str(to_cnf(all_condis))
        if (unknown):
            maybe_S = maybe_S + "( " + all_condis+ " )"
            maybe_S = str(to_cnf(expr(maybe_S)))
            maybe_S = Convert_to_literal(maybe_S, state_table)
            for clause in maybe_S:
                wumpus.append(clause)
        else:
            all_condis = Convert_to_literal(all_condis, state_table)
            for clause in all_condis:
                wumpus.append(clause)
    return


def prop_clause_I(turn_number, row, col, condition, structure, wumpus, state_table, unknown=False):
    '''if she is immune, she was either immunized last turn or was immune last turn..'''
    nigrar=[]
    maybe_I = ('I' + str(row)
               + str(col) + '_' + str(turn_number)) + " ==> "
    ############################33
    for turn_id in range(turn_number, structure.number_of_turns):
        condi_name = ('I'+ str(row)
                      + str(col) + '_' + str(turn_id))
        if(unknown):
            nigrar.append(condi_name)
        else:
            temp_var = state_table[condi_name]
            wumpus.append([temp_var])
    #############################
    if turn_number > 0 and structure.medic_num>0:
        all_condis = []
        for (turn_id) in range(turn_number):
            medic_list = []
            for medic_id in range(structure.medic_num):
                condi_name = ('M' + str(medic_id) + '_' + str(row)
                              + str(col) + '_' + str(turn_id))
                medic_list.append(condi_name)

            medic_list = (" | ".join(medic_list))
            medic_var = str(expr(medic_list))
            unsick_prev = str(expr('H' + str(row)
                                   + str(col) + '_' + str(turn_id)))
            all_condis.append(str(expr(str(unsick_prev + '&' + medic_var))))
        all_condis = str(to_cnf(expr(" | ".join(all_condis))))
        if (unknown):
            maybe_I = maybe_I + "(( " + " & ".join(nigrar) + " )"
            maybe_I = maybe_I + " & ( " + all_condis + " ))"
            maybe_I = str(to_cnf(expr(maybe_I)))
            maybe_I = Convert_to_literal(maybe_I, state_table)
            for clause in maybe_I:
                wumpus.append(clause)
        else:
            all_condis = Convert_to_literal(all_condis, state_table)
            for clause in all_condis:
                wumpus.append(clause)
        # add condition didn't visit anybody else

    # immune--> (was healthy at turn 0 &&&&& (had medic0(and didn't visit anyone else) or medic1(and didn't visit anyone else) or....medicN))  or\
    # (was healthy at turn 1 &&&&& (had medic0 or medic1 or....medicN)
    return

def Convert_to_literal(condis, state_table):
    nobracks=True
    brun=False
    if(condis[1]=='('):
         no_brackets = condis[2:-2]
         nobracks=False
    elif((condis[-2]=='(')):
        no_brackets = condis[1:-2]
        brun=True
    else:
        no_brackets = condis[1:-1]
    no_ands = Convert_ands(no_brackets, nobracks, brun)
    nulis = []
    for ite in no_ands:
        nulis.append(Convert_ors(ite, state_table))
    return nulis


def Convert_ands(string, nobracks, brun):
    if(nobracks and brun):
        firsi=string.split( " & (")[0]
        li = list(string.split(") & ("))
        li[0]=firsi
    elif(nobracks and not brun):
        li = list(string.split(" & "))
    else:
        li = list(string.split(") & ("))
    return li

def Convert_ors(string, state_table):
    li = list(string.split(" | "))
    num_list=[]
    for item in li:
        item=item.replace("(","")
        item=item.replace(")", "")
        num_list.append(state_table[item])
    return num_list

def prop_clause_Q(turn_number, row, col, condition, structure, wumpus, state_table, unknown=False):
    maybe_Q = ('Q' + str(row)
               + str(col) + '_' + str(turn_number)) + " ==> "

    all_condis=[]
    if turn_number>0 and structure.cop_num>0:
        sick_last_turn=('S' + str(row)    + str(col) + '_' + str(turn_number-1))
        for cop_id in range(structure.cop_num):
            condi_name = ('P' + str(cop_id) + '_' + str(row)
                          + str(col) + '_' + str(turn_number-1))
            condi_name = sick_last_turn + ' & ' + condi_name
            if(turn_number<structure.number_of_turns-1):
                quaraned_next_turn = ('Q' + str(row) + str(col) + '_' + str(turn_number + 1))
                condi_name = condi_name + ' & ' + quaraned_next_turn
            if (turn_number < structure.number_of_turns - 2):
                not_quarened_2_turns=('~Q' + str(row) + str(col) + '_' + str(turn_number + 2))
                condi_name = condi_name + ' & ' + not_quarened_2_turns
            condi_name = str(to_cnf(expr(condi_name)))
            all_condis.append(condi_name)
    if turn_number>1 and structure.cop_num>0:
        sick_last_turn = ('S' + str(row) + str(col) + '_' + str(turn_number - 2))
        quarened_last_turn=('Q' + str(row) + str(col) + '_' + str(turn_number - 1))
        quarened_last__2turn = ('~Q' + str(row) + str(col) + '_' + str(turn_number - 2))
        sick_last_turn=sick_last_turn+ ' & '+ quarened_last_turn+ ' & '+ quarened_last__2turn
        for cop_id in range(structure.cop_num):
            condi_name = ('P' + str(cop_id) + '_' + str(row)
                          + str(col) + '_' + str(turn_number - 2))
            condi_name = sick_last_turn + ' & ' + condi_name
            condi_name=str(to_cnf(expr(condi_name)))
            all_condis.append(condi_name)
    if(all_condis):
        all_condis = str(to_cnf(expr(" | ".join(all_condis))))
        if (unknown):
            maybe_Q = maybe_Q + "( " + all_condis + " )"
            maybe_Q = str(to_cnf(expr(maybe_Q)))
            maybe_Q = Convert_to_literal(maybe_Q, state_table)
            for clause in maybe_Q:
                wumpus.append(clause)
        else:
            all_condis = Convert_to_literal(all_condis, state_table)
            for clause in all_condis:
                wumpus.append(clause)
    return
#quarantined --> was sick either last turn and was visited by cop, or in the 2nd to last turn and visited by cop and was quarantined last turn.


def add_docs_and_cops(state_table, wumpus, structure):

    if(structure.cop_num==0):
        for turn_number in range(1, structure.number_of_turns):
            for i in range(structure.height):
                for j in range(structure.width):
                    condi_name = ('~Q' + str(i)
                                  + str(j) + '_' + str(turn_number))
                    wumpus.append([state_table[condi_name]])
    if (structure.medic_num == 0):
        for turn_number in range(1, structure.number_of_turns):
            for i in range(structure.height):
                for j in range(structure.width):
                    condi_name = ('~I' + str(i)
                                  + str(j) + '_' + str(turn_number))
                    wumpus.append([state_table[condi_name]])


    #ADDD IF NUMBER OF COPS IS ZERO, NO QAURANTINES WILL HAPPEN.
    #ADDD IF NUMBER OF MEDICS IS ZERO, NO VACCINATIONS WILL HAPPEN
    #######################################################################
    for turn_number in range(structure.number_of_turns):
        for i in range(structure.height):
            for j in range(structure.width):
                for condition in range(len(structure.possible_states)):
                    condi_name=(structure.possible_states[condition] + str(i)
                               + str(j) + '_' + str(turn_number))
                    if (structure.possible_states[condition] != 'S'):
                        if(structure.cop_num>0):
                            cop_items = []
                            for cop_id in range(structure.cop_num):
                                cop_name = ('~' + 'P' + str(cop_id) + '_' + str(i)
                                              + str(j) + '_' + str(turn_number))
                                cop_items.append(cop_name)
                            joined=(" & ".join(cop_items))
                            cop_items=str(to_cnf(expr(condi_name+" ==> "+joined)))
                            cop_items=Convert_to_literal(cop_items, state_table)
                            for cop in cop_items:
                                wumpus.append(cop)
                    if (structure.possible_states[condition] != 'H'):
                        if (structure.medic_num > 0):
                            medic_items = []
                            for medic_id in range(structure.medic_num):
                                medic_name = ('~' + 'M' + str(medic_id) + '_' + str(i)
                                            + str(j) + '_' + str(turn_number))
                                medic_items.append(medic_name)
                            joined = (" & ".join(medic_items))

                            medic_items = str(to_cnf(expr(condi_name + " ==> " + joined)))
                            medic_items = Convert_to_literal(medic_items, state_table)
                            for medic in medic_items:
                                wumpus.append(medic)
    #######################################################################




    for turn_number in range(structure.number_of_turns):
        for i in range(structure.height):
            for j in range(structure.width):
                for item1 in range(len(structure.possible_states)):
                    condi_1 = ('~' + structure.possible_states[item1] + str(i)
                               + str(j) + '_' + str(turn_number))
                    for item2 in range(item1+1, len(structure.possible_states)):
                        condi_2 = ('~' + structure.possible_states[item2] + str(i)
                                   + str(j) + '_' + str(turn_number))
                        hau = str(to_cnf(condi_1 + ' | ' + condi_2))
                        hau = Convert_to_literal(hau, state_table)
                        for clasu in hau:
                            wumpus.append(clasu)

    for turn_number in range(structure.number_of_turns):
        for cop_id in range(structure.cop_num):
            for i in range(structure.height):
                for j in range(structure.width):
                    condi_name = ('~P' + str(cop_id) + '_' + str(i)
                                 + str(j) + '_' + str(turn_number))
                    for other_i in range(structure.height):
                        for other_j in range(structure.width):
                            if (i != other_i or j != other_j):
                                other_condi=('~P' + str(cop_id) + '_' + str(other_i)
                                 + str(other_j) + '_' + str(turn_number))
                                hau = str(to_cnf(condi_name + ' | ' +  other_condi))
                                hau = Convert_to_literal(hau, state_table)
                                for clasu in hau:
                                    wumpus.append(clasu)

    for turn_number in range(structure.number_of_turns):
        for medic_id in range(structure.medic_num):
            for i in range(structure.height):
                for j in range(structure.width):
                    condi_name = ('~M' + str(medic_id) + '_' + str(i)
                                 + str(j) + '_' + str(turn_number))
                    for other_i in range(structure.height):
                        for other_j in range(structure.width):
                            if (i != other_i or j != other_j):
                                other_condi=('~M' + str(medic_id) + '_' + str(other_i)
                                 + str(other_j) + '_' + str(turn_number))
                                hau = str(to_cnf(condi_name + ' | ' + other_condi))
                                hau = Convert_to_literal(hau, state_table)
                                for clasu in hau:
                                    wumpus.append(clasu)

    for i in range(structure.height):
        for j in range(structure.width):
            condi_name = ('~Q'+ str(i)
                          + str(j) + '_' + '0')
            wumpus.append([state_table[condi_name]])
            for clasu in hau:
                wumpus.append(clasu)
            condi_name = ('~I'+ str(i)
                          + str(j) + '_' + '0')
            wumpus.append([state_table[condi_name]])
    return





# sick- means he was either infected by one of his neighbours in the last 2 turns, or was sick himelf.
# healthy- means that no one adjacent was sick in the last turn, or was sick for the last 3 turns, or was quarantined 2 turns
# quarantined- means they were sick in the last turn or 2 turns back, and there was a free medic
# immune- was immunized  in a past turn, and was was healthy, and there was a free popo

# add variables for all states for each position on board, add in use state for each popo and medic
# add them of course for each turn
def create_main_table(structure):
    state_table = {}
    counter = 1
    number_of_turns = structure.number_of_turns
    possible_states = structure.possible_states
    cop_num = structure.cop_num
    medic_num = structure.medic_num
    width = structure.width  # len(input['observations'][0][0])
    height = structure.height  # len(input['observations'][0])
    for turn_id in range(number_of_turns):
        for row in range(height):
            for col in range(width):
                for state in possible_states:
                    loco = (state + str(row) + str(col) + '_' + str(turn_id))
                    state_table[loco] = counter
                    antilloco = '~' + loco
                    state_table[antilloco] = -counter
                    counter += 1
                for medic_id in range(medic_num):
                    hoho = ('M' + str(medic_id) + '_' + str(row) + str(col) + '_' + str(turn_id))
                    state_table[hoho] = counter
                    antihoho = '~' + hoho
                    state_table[antihoho] = -counter
                    counter += 1
                for cop_id in range(cop_num):
                    boho = ('P' + str(cop_id) + '_' + str(row) + str(col) + '_' + str(turn_id))
                    state_table[boho] = counter
                    antiboho = '~' + boho
                    state_table[antiboho] = -counter
                    counter += 1
    return state_table

# ----------------------------------------------------------------------------------------------------------------------------------
def is_symbol(s):
    """A string s is a symbol if it starts with an alphabetic char.
    >>> is_symbol('R2D2')
    True
    """
    return isinstance(s, str) and s[:1].isalpha()


def is_var_symbol(s):
    """A logic variable symbol is an initial-lowercase string.
    >>> is_var_symbol('EXE')
    False
    """
    return is_symbol(s) and s[0].islower()


def is_prop_symbol(s):
    """A proposition logic symbol is an initial-uppercase string.
    >>> is_prop_symbol('exe')
    False
    """
    return is_symbol(s) and s[0].isupper()


def variables(s):
    """Return a set of the variables in expression s.
    >>> variables(expr('F(x, x) & G(x, y) & H(y, z) & R(A, z, 2)')) == {x, y, z}
    True
    """
    return {x for x in subexpressions(s) if is_variable(x)}


def is_definite_clause(s):
    """Returns True for exprs s of the form A & B & ... & C ==> D,
    where all literals are positive. In clause form, this is
    ~A | ~B | ... | ~C | D, where exactly one clause is positive.
    >>> is_definite_clause(expr('Farmer(Mac)'))
    True
    """
    if is_symbol(s.op):
        return True
    elif s.op == '==>':
        antecedent, consequent = s.args
        return is_symbol(consequent.op) and all(is_symbol(arg.op) for arg in conjuncts(antecedent))
    else:
        return False


def parse_definite_clause(s):
    """Return the antecedents and the consequent of a definite clause."""
    assert is_definite_clause(s)
    if is_symbol(s.op):
        return [], s
    else:
        antecedent, consequent = s.args
        return conjuncts(antecedent), consequent


# ______________________________________________________________________________

def prop_symbols(x):
    """Return the set of all propositional symbols in x."""
    if not isinstance(x, Expr):
        return set()
    elif is_prop_symbol(x.op):
        return {x}
    else:
        return {symbol for arg in x.args for symbol in prop_symbols(arg)}


def constant_symbols(x):
    """Return the set of all constant symbols in x."""
    if not isinstance(x, Expr):
        return set()
    elif is_prop_symbol(x.op) and not x.args:
        return {x}
    else:
        return {symbol for arg in x.args for symbol in constant_symbols(arg)}


def predicate_symbols(x):
    """Return a set of (symbol_name, arity) in x.
    All symbols (even functional) with arity > 0 are considered."""
    if not isinstance(x, Expr) or not x.args:
        return set()
    pred_set = {(x.op, len(x.args))} if is_prop_symbol(x.op) else set()
    pred_set.update({symbol for arg in x.args for symbol in predicate_symbols(arg)})
    return pred_set


def tt_true(s):
    """Is a propositional sentence a tautology?
    >>> tt_true('P | ~P')
    True
    """
    s = expr(s)
    return tt_entails(True, s)


def pl_true(exp, model={}):
    """Return True if the propositional logic expression is true in the model,
    and False if it is false. If the model does not specify the value for
    every proposition, this may return None to indicate 'not obvious';
    this may happen even when the expression is tautological.
    >>> pl_true(P, {}) is None
    True
    """
    if exp in (True, False):
        return exp
    op, args = exp.op, exp.args
    if is_prop_symbol(op):
        return model.get(exp)
    elif op == '~':
        p = pl_true(args[0], model)
        if p is None:
            return None
        else:
            return not p
    elif op == '|':
        result = False
        for arg in args:
            p = pl_true(arg, model)
            if p is True:
                return True
            if p is None:
                result = None
        return result
    elif op == '&':
        result = True
        for arg in args:
            p = pl_true(arg, model)
            if p is False:
                return False
            if p is None:
                result = None
        return result
    p, q = args
    if op == '==>':
        return pl_true(~p | q, model)
    elif op == '<==':
        return pl_true(p | ~q, model)
    pt = pl_true(p, model)
    if pt is None:
        return None
    qt = pl_true(q, model)
    if qt is None:
        return None
    if op == '<=>':
        return pt == qt
    elif op == '^':  # xor or 'not equivalent'
        return pt != qt
    else:
        raise ValueError('Illegal operator in logic expression' + str(exp))


# ______________________________________________________________________________

# Convert to Conjunctive Normal Form (CNF)


def to_cnf(s):
    """
    [Page 253]
    Convert a propositional logical sentence to conjunctive normal form.
    That is, to the form ((A | ~B | ...) & (B | C | ...) & ...)
    >>> to_cnf('~(B | C)')
    (~B & ~C)
    """
    s = expr(s)
    if isinstance(s, str):
        s = expr(s)
    s = eliminate_implications(s)  # Steps 1, 2 from p. 253
    s = move_not_inwards(s)  # Step 3
    return distribute_and_over_or(s)  # Step 4


def eliminate_implications(s):
    """Change implications into equivalent form with only &, |, and ~ as logical operators."""
    s = expr(s)
    if not s.args or is_symbol(s.op):
        return s  # Atoms are unchanged.
    args = list(map(eliminate_implications, s.args))
    a, b = args[0], args[-1]
    if s.op == '==>':
        return b | ~a
    elif s.op == '<==':
        return a | ~b
    elif s.op == '<=>':
        return (a | ~b) & (b | ~a)
    elif s.op == '^':
        assert len(args) == 2  # TODO: relax this restriction
        return (a & ~b) | (~a & b)
    else:
        assert s.op in ('&', '|', '~')
        return Expr(s.op, *args)


def move_not_inwards(s):
    """Rewrite sentence s by moving negation sign inward.
    >>> move_not_inwards(~(A | B))
    (~A & ~B)
    """
    s = expr(s)
    if s.op == '~':
        def NOT(b):
            return move_not_inwards(~b)

        a = s.args[0]
        if a.op == '~':
            return move_not_inwards(a.args[0])  # ~~A ==> A
        if a.op == '&':
            return associate('|', list(map(NOT, a.args)))
        if a.op == '|':
            return associate('&', list(map(NOT, a.args)))
        return s
    elif is_symbol(s.op) or not s.args:
        return s
    else:
        return Expr(s.op, *list(map(move_not_inwards, s.args)))


def distribute_and_over_or(s):
    """Given a sentence s consisting of conjunctions and disjunctions
    of literals, return an equivalent sentence in CNF.
    >>> distribute_and_over_or((A & B) | C)
    ((A | C) & (B | C))
    """
    s = expr(s)
    if s.op == '|':
        s = associate('|', s.args)
        if s.op != '|':
            return distribute_and_over_or(s)
        if len(s.args) == 0:
            return False
        if len(s.args) == 1:
            return distribute_and_over_or(s.args[0])
        conj = first(arg for arg in s.args if arg.op == '&')
        if not conj:
            return s
        others = [a for a in s.args if a is not conj]
        rest = associate('|', others)
        return associate('&', [distribute_and_over_or(c | rest)
                               for c in conj.args])
    elif s.op == '&':
        return associate('&', list(map(distribute_and_over_or, s.args)))
    else:
        return s


def associate(op, args):
    """Given an associative op, return an expression with the same
    meaning as Expr(op, *args), but flattened -- that is, with nested
    instances of the same op promoted to the top level.
    >>> associate('&', [(A&B),(B|C),(B&C)])
    (A & B & (B | C) & B & C)
    >>> associate('|', [A|(B|(C|(A&B)))])
    (A | B | C | (A & B))
    """
    args = dissociate(op, args)
    if len(args) == 0:
        return _op_identity[op]
    elif len(args) == 1:
        return args[0]
    else:
        return Expr(op, *args)


_op_identity = {'&': True, '|': False, '+': 0, '*': 1}


def dissociate(op, args):
    """Given an associative op, return a flattened list result such
    that Expr(op, *result) means the same as Expr(op, *args).
    >>> dissociate('&', [A & B])
    [A, B]
    """
    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)

    collect(args)
    return result


def conjuncts(s):
    """Return a list of the conjuncts in the sentence s.
    >>> conjuncts(A & B)
    [A, B]
    >>> conjuncts(A | B)
    [(A | B)]
    """
    return dissociate('&', [s])


def disjuncts(s):
    """Return a list of the disjuncts in the sentence s.
    >>> disjuncts(A | B)
    [A, B]
    >>> disjuncts(A & B)
    [(A & B)]
    """
    return dissociate('|', [s])


# ______________________________________________________________________________


def pl_resolution(kb, alpha):
    """
    [Figure 7.12]
    Propositional-logic resolution: say if alpha follows from KB.
    >>> pl_resolution(horn_clauses_KB, A)
    True
    """
    clauses = kb.clauses + conjuncts(to_cnf(~alpha))
    new = set()
    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j])
                 for i in range(n) for j in range(i + 1, n)]
        for (ci, cj) in pairs:
            resolvents = pl_resolve(ci, cj)
            if False in resolvents:
                return True
            new = new.union(set(resolvents))
        if new.issubset(set(clauses)):
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)


def pl_resolve(ci, cj):
    """Return all clauses that can be obtained by resolving clauses ci and cj."""
    clauses = []
    for di in disjuncts(ci):
        for dj in disjuncts(cj):
            if di == ~dj or ~di == dj:
                clauses.append(associate('|', unique(remove_all(di, disjuncts(ci)) + remove_all(dj, disjuncts(cj)))))
    return clauses


# -------------------------- from utils.py ----------------------------------

def remove_all(item, seq):
    """Return a copy of seq (or string) with all occurrences of item removed."""
    if isinstance(seq, str):
        return seq.replace(item, '')
    elif isinstance(seq, set):
        rest = seq.copy()
        rest.remove(item)
        return rest
    else:
        return [x for x in seq if x != item]

class Expr(object):
    """A mathematical expression with an operator and 0 or more arguments.
    op is a str like '+' or 'sin'; args are Expressions.
    Expr('x') or Symbol('x') creates a symbol (a nullary Expr).
    Expr('-', x) creates a unary; Expr('+', x, 1) creates a binary."""

    def __init__(self, op, *args):
        self.op = str(op)
        self.args = args

    # Operator overloads
    def __neg__(self):
        return Expr('-', self)

    def __pos__(self):
        return Expr('+', self)

    def __invert__(self):
        return Expr('~', self)

    def __add__(self, rhs):
        return Expr('+', self, rhs)

    def __sub__(self, rhs):
        return Expr('-', self, rhs)

    def __mul__(self, rhs):
        return Expr('*', self, rhs)

    def __pow__(self, rhs):
        return Expr('**', self, rhs)

    def __mod__(self, rhs):
        return Expr('%', self, rhs)

    def __and__(self, rhs):
        return Expr('&', self, rhs)

    def __xor__(self, rhs):
        return Expr('^', self, rhs)

    def __rshift__(self, rhs):
        return Expr('>>', self, rhs)

    def __lshift__(self, rhs):
        return Expr('<<', self, rhs)

    def __truediv__(self, rhs):
        return Expr('/', self, rhs)

    def __floordiv__(self, rhs):
        return Expr('//', self, rhs)

    def __matmul__(self, rhs):
        return Expr('@', self, rhs)

    def __or__(self, rhs):
        """Allow both P | Q, and P |'==>'| Q."""
        if isinstance(rhs, Expression):
            return Expr('|', self, rhs)
        else:
            return PartialExpr(rhs, self)

    # Reverse operator overloads
    def __radd__(self, lhs):
        return Expr('+', lhs, self)

    def __rsub__(self, lhs):
        return Expr('-', lhs, self)

    def __rmul__(self, lhs):
        return Expr('*', lhs, self)

    def __rdiv__(self, lhs):
        return Expr('/', lhs, self)

    def __rpow__(self, lhs):
        return Expr('**', lhs, self)

    def __rmod__(self, lhs):
        return Expr('%', lhs, self)

    def __rand__(self, lhs):
        return Expr('&', lhs, self)

    def __rxor__(self, lhs):
        return Expr('^', lhs, self)

    def __ror__(self, lhs):
        return Expr('|', lhs, self)

    def __rrshift__(self, lhs):
        return Expr('>>', lhs, self)

    def __rlshift__(self, lhs):
        return Expr('<<', lhs, self)

    def __rtruediv__(self, lhs):
        return Expr('/', lhs, self)

    def __rfloordiv__(self, lhs):
        return Expr('//', lhs, self)

    def __rmatmul__(self, lhs):
        return Expr('@', lhs, self)

    def __call__(self, *args):
        "Call: if 'f' is a Symbol, then f(0) == Expr('f', 0)."
        if self.args:
            raise ValueError('can only do a call for a Symbol, not an Expr')
        else:
            return Expr(self.op, *args)

    # Equality and repr
    def __eq__(self, other):
        "'x == y' evaluates to True or False; does not build an Expr."
        return (isinstance(other, Expr)
                and self.op == other.op
                and self.args == other.args)

    def __hash__(self):
        return hash(self.op) ^ hash(self.args)

    def __repr__(self):
        op = self.op
        args = [str(arg) for arg in self.args]
        if op.isidentifier():  # f(x) or f(x, y)
            return '{}({})'.format(op, ', '.join(args)) if args else op
        elif len(args) == 1:  # -x or -(x + 1)
            return op + args[0]
        else:  # (x - y)
            opp = (' ' + op + ' ')
            return '(' + opp.join(args) + ')'


# An 'Expression' is either an Expr or a Number.
# Symbol is not an explicit type; it is any Expr with 0 args.


Number = (int, float, complex)
Expression = (Expr, Number)


def Symbol(name):
    """A Symbol is just an Expr with no args."""
    return Expr(name)


def symbols(names):
    """Return a tuple of Symbols; names is a comma/whitespace delimited str."""
    return tuple(Symbol(name) for name in names.replace(',', ' ').split())


def subexpressions(x):
    """Yield the subexpressions of an Expression (including x itself)."""
    yield x
    if isinstance(x, Expr):
        for arg in x.args:
            yield from subexpressions(arg)


def unique(seq):
    """Remove duplicate elements from seq. Assumes hashable elements."""
    return list(set(seq))


def is_variable(x):
    """A variable is an Expr with no args and a lowercase symbol as the op."""
    return isinstance(x, Expr) and not x.args and x.op[0].islower()


class PartialExpr:
    """Given 'P |'==>'| Q, first form PartialExpr('==>', P), then combine with Q."""

    def __init__(self, op, lhs):
        self.op, self.lhs = op, lhs

    def __or__(self, rhs):
        return Expr(self.op, self.lhs, rhs)

    def __repr__(self):
        return "PartialExpr('{}', {})".format(self.op, self.op, self.lhs)


def expr(x):
    """Shortcut to create an Expression. x is a str in which:
    - identifiers are automatically defined as Symbols.
    - ==> is treated as an infix |'==>'|, as are <== and <=>.
    If x is already an Expression, it is returned unchanged. Example:
    >>> expr('P & Q ==> Q')
    ((P & Q) ==> Q)
    """
    if isinstance(x, str):
        return eval(expr_handle_infix_ops(x), defaultkeydict(Symbol))
    else:
        return x


infix_ops = '==> <== <=>'.split()


def expr_handle_infix_ops(x):
    """Given a str, return a new str with ==> replaced by |'==>'|, etc.
    >>> expr_handle_infix_ops('P ==> Q')
    "P |'==>'| Q"
    """
    for op in infix_ops:
        x = x.replace(op, '|' + repr(op) + '|')
    return x


class defaultkeydict(collections.defaultdict):
    """Like defaultdict, but the default_factory is a function of the key.
    >>> d = defaultkeydict(len); d['four']
    4
    """

    def __missing__(self, key):
        self[key] = result = self.default_factory(key)
        return result


def first(iterable, default=None):
    """Return the first element of an iterable or the next element of a generator; or default."""
    try:
        return iterable[0]
    except IndexError:
        return default
    except TypeError:
        return next(iterable, default)
