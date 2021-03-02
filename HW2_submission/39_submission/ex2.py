from itertools import combinations, product
from pysat.solvers import Glucose4

ids = ['206014185', '316361641']


def pre_agent(action):
    if 'P' in action[2]:
        return (action[0], action[1], ('S', -1)), True
    return (action[0], action[1], ('H', -1)), True


def pre_infect(action, max_rows, max_cols):
    infect_literals = {'infect_to_pre': [], 'pre_to_infect': []}
    row_idx, col_idx = action[0]
    if row_idx - 1 >= 0:
        infect_literals['infect_to_pre'].append([(((row_idx - 1, col_idx), action[1], ('S', -1)), True),
                                                 (((row_idx - 1, col_idx), action[1] + 1, ('Q', 0)), False)])

        infect_literals['pre_to_infect'].append([(((row_idx - 1, col_idx), action[1], ('S', -1)), False),
                                                 (((row_idx - 1, col_idx), action[1] + 1, ('Q', 0)), True),
                                                 (((row_idx, col_idx), action[1], ('H', -1)), False),
                                                 (((row_idx, col_idx), action[1] + 1, ('I', -1)), True)])

    if row_idx + 1 < max_rows:
        infect_literals['infect_to_pre'].append([(((row_idx + 1, col_idx), action[1], ('S', -1)), True),
                                                 (((row_idx + 1, col_idx), action[1] + 1, ('Q', 0)), False)])

        infect_literals['pre_to_infect'].append([(((row_idx + 1, col_idx), action[1], ('S', -1)), False),
                                                 (((row_idx + 1, col_idx), action[1] + 1, ('Q', 0)), True),
                                                 (((row_idx, col_idx), action[1], ('H', -1)), False),
                                                 (((row_idx, col_idx), action[1] + 1, ('I', -1)), True)])

    if col_idx - 1 >= 0:
        infect_literals['infect_to_pre'].append([(((row_idx, col_idx - 1), action[1], ('S', -1)), True),
                                                 (((row_idx, col_idx - 1), action[1] + 1, ('Q', 0)), False)])

        infect_literals['pre_to_infect'].append([(((row_idx, col_idx - 1), action[1], ('S', -1)), False),
                                                 (((row_idx, col_idx - 1), action[1] + 1, ('Q', 0)), True),
                                                 (((row_idx, col_idx), action[1], ('H', -1)), False),
                                                 (((row_idx, col_idx), action[1] + 1, ('I', -1)), True)])

    if col_idx + 1 < max_cols:
        infect_literals['infect_to_pre'].append([(((row_idx, col_idx + 1), action[1], ('S', -1)), True),
                                                 (((row_idx, col_idx + 1), action[1] + 1, ('Q', 0)), False)])

        infect_literals['pre_to_infect'].append([(((row_idx, col_idx + 1), action[1], ('S', -1)), False),
                                                 (((row_idx, col_idx + 1), action[1] + 1, ('Q', 0)), True),
                                                 (((row_idx, col_idx), action[1], ('H', -1)), False),
                                                 (((row_idx, col_idx), action[1] + 1, ('I', -1)), True)])
    infect_literals['infect_to_pre'].append((((row_idx, col_idx), action[1], ('H', -1)), True))
    return infect_literals


def add_agent(action):
    if 'P' in action[2]:
        return (action[0], action[1] + 1, ('Q', 0)), True
    return (action[0], action[1] + 1, ('I', -1)), True


def add_infect(action):
    return (action[0], action[1] + 1, ('S', 0)), True


def delete_agent(action):
    if 'P' in action[2]:
        return [((action[0], action[1] + 1, ('S', time)), False) for time in range(3)]
    return [((action[0], action[1] + 1, ('H', -1)), False)]


def delete_infect(action):
    return (action[0], action[1] + 1, ('H', -1)), False


def add_initial_obs_literals(state, row_idx, col_idx, state_set, literal_set, clause_list):
    time = 0
    initial_states = {('H', -1), ('S', 0), ('U', -1)}
    if state == '?':
        all_literals = []
        for other_state in initial_states:
            literal = ((row_idx, col_idx), time, other_state)
            literal_set.add(literal)
            all_literals.append((literal, True))
        clause_list.append(all_literals)
        for state1, state2 in combinations(initial_states, 2):
            literal1 = ((row_idx, col_idx), time, state1)
            literal2 = ((row_idx, col_idx), time, state2)
            clause_list.append([(literal1, False), (literal2, False)])
        not_state_set = initial_states
    elif state == 'S':
        literal = ((row_idx, col_idx), time, (state, 0))
        literal_set.add(literal)
        clause_list.append([(literal, True)])
        not_state_set = {('S', 0)}
    else:
        literal = ((row_idx, col_idx), time, (state, -1))
        literal_set.add(literal)
        clause_list.append([(literal, True)])
        not_state_set = {(state, -1)}
    for not_state in state_set - not_state_set:
        not_literal = ((row_idx, col_idx), time, not_state)
        literal_set.add(not_literal)
        clause_list.append([(not_literal, False)])
    return literal_set, clause_list


def add_advanced_obs_literals(state, row_idx, col_idx, time, state_set, literal_set, clause_list):
    if state == '?':
        all_literals = []
        for state in state_set:
            literal = ((row_idx, col_idx), time, state)
            literal_set.add(literal)
            all_literals.append((literal, True))
        clause_list.append(all_literals)
        for state1, state2 in combinations(state_set, 2):
            literal1 = ((row_idx, col_idx), time, state1)
            literal2 = ((row_idx, col_idx), time, state2)
            clause_list.append([(literal1, False), (literal2, False)])
        return literal_set, clause_list
    if state == 'S':
        clause = []
        not_clause = []
        for i in range(3):
            time_literal = ((row_idx, col_idx), time, (state, i))
            literal_set.add(time_literal)
            clause.append((time_literal, True))
            not_clause.append((time_literal, False))
        clause_list.append(clause)
        for time1, time2 in combinations(not_clause, 2):
            clause_list.append([time1, time2])
    elif state == 'Q':
        clause = []
        not_clause = []
        for i in range(2):
            time_literal = ((row_idx, col_idx), time, (state, i))
            literal_set.add(time_literal)
            clause.append((time_literal, True))
            not_clause.append((time_literal, False))
        clause_list.append(clause)
        for time1, time2 in combinations(not_clause, 2):
            clause_list.append([time1, time2])
    else:
        literal = ((row_idx, col_idx), time, (state, -1))
        literal_set.add(literal)
        clause_list.append([(literal, True)])
    for not_state in state_set - {other_state for other_state in state_set if other_state[0] == state}:
        not_literal = ((row_idx, col_idx), time, not_state)
        literal_set.add(not_literal)
        clause_list.append([(not_literal, False)])
    return literal_set, clause_list


def add_agent_actions(time, row_idx, col_idx, agent_actions, literal_set, clause_list):
    # add t-time action layer
    # agent_action = (position, time, action)
    agent_literals = {'P': [], 'M': []}
    for key_act in agent_actions.keys():
        for agent_act in agent_actions[key_act]:
            literal = ((row_idx, col_idx), time, agent_act)
            agent_literals[key_act].append(literal)
            literal_set.add(literal)
            # pre effects
            clause_list.append([(literal, False), pre_agent(literal)])
            # add effects
            clause_list.append([(literal, False), add_agent(literal)])
            # del effects
            for del_effect in delete_agent(literal):  # TODO
                clause_list.append([(literal, False), del_effect])

    return literal_set, clause_list, agent_literals


def add_infect_action(row_idx, col_idx, time, max_rows, max_cols, literal_set, clause_list):
    infect_literal = ((row_idx, col_idx), time, 'i')
    literal_set.add(infect_literal)
    pre_clauses = pre_infect(infect_literal, max_rows, max_cols)
    clause_list.append([(infect_literal, False), pre_clauses['infect_to_pre'][-1]])
    for infect_to_pre in product(*pre_clauses['infect_to_pre'][:-1]):
        clause_list.append([(infect_literal, False), *infect_to_pre])
    for pre_to_infect in pre_clauses['pre_to_infect']:
        clause_list.append(pre_to_infect + [(infect_literal, True)])
    clause_list.append([(infect_literal, False), add_infect(infect_literal)])
    clause_list.append([(infect_literal, False), delete_infect(infect_literal)])
    return literal_set, clause_list, infect_literal


def add_action_conflicts(agent_literals, infect_literal, clause_list):
    for act1, act2 in combinations([literal for actions in agent_literals.values() for literal in actions] +
                                   [infect_literal], 2):
        clause_list.append([(act1, False), (act2, False)])
    return clause_list


def add_frame_effects(row_idx, col_idx, time, infect_literal, agent_literals, state_set, clause_list):
    position_agent_action = [(literal, True) for actions in agent_literals.values() for literal in actions]
    time_states = {('S', 0), ('S', 1), ('Q', 0)}
    to_health_states = {('S', 2), ('Q', 1)}
    rest = (state_set - time_states) - to_health_states
    for time_state in time_states:
        cur_state, state_time = time_state
        clause_list.append([(((row_idx, col_idx), time, time_state), False), (infect_literal, True),
                            *position_agent_action,
                            (((row_idx, col_idx), time + 1, (cur_state, state_time + 1)), True)])
    for to_health_state in to_health_states:
        clause_list.append([(((row_idx, col_idx), time, to_health_state), False), (infect_literal, True),
                            *position_agent_action, (((row_idx, col_idx), time + 1, ('H', -1)), True)])
    for rest_state in rest:
        cur_state_and_time = rest_state
        clause_list.append([(((row_idx, col_idx), time, rest_state), False), (infect_literal, True),
                            *position_agent_action, (((row_idx, col_idx), time + 1, cur_state_and_time), True)])
    return clause_list


def add_agent_dependencies(row_idx, col_idx, time, prev_agent_literals, agent_actions, clause_list):
    # police dependencies
    curr_sick1_literal = ((row_idx, col_idx), time, ('S', 1))
    curr_sick2_literal = ((row_idx, col_idx), time, ('S', 2))
    for p_act in agent_actions['P']:
        clause_list.append([(curr_sick1_literal, False)] + [(act, True) for act in prev_agent_literals['P']
                                                            if act[2] == p_act])
        clause_list.append([(curr_sick2_literal, False)] + [(act, True) for act in prev_agent_literals['P']
                                                            if act[2] == p_act])
    # medics dependencies
    curr_healthy_literal = ((row_idx, col_idx), time, ('H', -1))
    previous_last_sick = ((row_idx, col_idx), time - 1, ('S', 2))
    previous_last_quarantine = ((row_idx, col_idx), time - 1, ('Q', 1))
    for m_act in agent_actions['M']:
        clause_list.append([(curr_healthy_literal, False), (previous_last_sick, True),
                            (previous_last_quarantine, True)] + [(act, True) for act in prev_agent_literals['M']
                                                                 if act[2] == m_act])
    return clause_list


def add_general_sick(row_idx, col_idx, time, literal_set, clause_list):
    general_sick_literal = ((row_idx, col_idx), time, ('S', -1))
    literal_set.add(general_sick_literal)
    sick_timer_list = [((row_idx, col_idx), time, ('S', timer)) for timer in range(3)]
    for sick_literal in sick_timer_list:
        clause_list.append([(sick_literal, False), (general_sick_literal, True)])
    clause_list.append([(general_sick_literal, False)] + [(sick_literal, True) for sick_literal in sick_timer_list])
    return literal_set, clause_list


def add_agent_conflicts(agent_actions, curr_agent_literals, clause_list):
    for key_act in agent_actions.keys():
        for agent_act_counter in agent_actions[key_act]:
            for act1, act2 in combinations([act for act in curr_agent_literals[key_act]
                                            if act[2] == agent_act_counter], 2):
                clause_list.append([(act1, False), (act2, False)])
    return clause_list


def solve_problem(input):
    state_set = {('H', -1), ('S', 0), ('S', 1), ('S', 2), ('Q', 0), ('Q', 1), ('I', -1), ('U', -1)}
    agent_actions = {'P': {'P' + str(j) for j in range(input["police"])},
                     'M': {'M' + str(i) for i in range(input["medics"])}}
    literal_set = set()
    clause_list = []
    prev_agent_literals = {'P': [], 'M': []}
    for time, obs in enumerate(input["observations"]):
        curr_agent_literals = {'P': [], 'M': []}
        for row_idx in range(len(obs)):
            for col_idx in range(len(obs[row_idx])):
                state = obs[row_idx][col_idx]
                if time == 0:
                    literal_set, clause_list = add_initial_obs_literals(state, row_idx, col_idx, state_set,
                                                                        literal_set, clause_list)
                    if time == len(input["observations"]) - 1:
                        continue
                    literal_set, clause_list, agent_literals = add_agent_actions(time, row_idx, col_idx, agent_actions,
                                                                                 literal_set, clause_list)
                    for key_act in agent_literals.keys():
                        curr_agent_literals[key_act] = curr_agent_literals[key_act] + agent_literals[key_act]
                    literal_set, clause_list, infect_literal = add_infect_action(row_idx, col_idx, time, len(obs),
                                                                                 len(obs[row_idx]),
                                                                                 literal_set, clause_list)
                    clause_list = add_action_conflicts(agent_literals, infect_literal, clause_list)
                    clause_list = add_frame_effects(row_idx, col_idx, time, infect_literal, agent_literals, state_set,
                                                    clause_list)
                elif time < len(input["observations"]) - 1:
                    literal_set, clause_list = add_advanced_obs_literals(state, row_idx, col_idx, time, state_set,
                                                                         literal_set, clause_list)
                    clause_list = add_agent_dependencies(row_idx, col_idx, time, prev_agent_literals, agent_actions,
                                                         clause_list)
                    literal_set, clause_list, agent_literals = add_agent_actions(time, row_idx, col_idx, agent_actions,
                                                                                 literal_set, clause_list)
                    for key_act in agent_literals.keys():
                        curr_agent_literals[key_act] = curr_agent_literals[key_act] + agent_literals[key_act]
                    literal_set, clause_list, infect_literal = add_infect_action(row_idx, col_idx, time, len(obs),
                                                                                 len(obs[row_idx]),
                                                                                 literal_set, clause_list)
                    clause_list = add_action_conflicts(agent_literals, infect_literal, clause_list)
                    clause_list = add_frame_effects(row_idx, col_idx, time, infect_literal, agent_literals, state_set,
                                                    clause_list)
                else:
                    literal_set, clause_list = add_advanced_obs_literals(state, row_idx, col_idx, time, state_set,
                                                                         literal_set, clause_list)
                    clause_list = add_agent_dependencies(row_idx, col_idx, time, prev_agent_literals, agent_actions,
                                                         clause_list)
                literal_set, clause_list = add_general_sick(row_idx, col_idx, time, literal_set, clause_list)

        clause_list = add_agent_conflicts(agent_actions, curr_agent_literals, clause_list)
        prev_agent_literals = curr_agent_literals

    literal_dict = {}
    for num, literal in enumerate(literal_set):
        literal_dict[literal] = num + 1

    coded_clause_list = []
    for clause in clause_list:
        coded_clause = []
        for literal, sign in clause:
            if sign:
                coded_clause.append(literal_dict[literal])
            else:
                coded_clause.append(-literal_dict[literal])
        coded_clause_list.append(coded_clause)

    results = {}
    for query in input["queries"]:
        new_clause_false = coded_clause_list.copy()
        true_clause = []
        if query[2] == 'S':
            for i in range(3):
                time_literal = (query[0], query[1], ('S', i))
                true_clause.append(literal_dict[time_literal])
                new_clause_false.append([-literal_dict[time_literal]])
            new_clause_true = coded_clause_list + [true_clause]
        elif query[2] == 'Q':
            for i in range(2):
                time_literal = (query[0], query[1], ('Q', i))
                true_clause.append(literal_dict[time_literal])
                new_clause_false.append([-literal_dict[time_literal]])
            new_clause_true = coded_clause_list + [true_clause]
        else:
            literal = (query[0], query[1], (query[2], -1))
            new_clause_true = coded_clause_list + [[literal_dict[literal]]]
            new_clause_false = coded_clause_list + [[-literal_dict[literal]]]
        glucose4_true = Glucose4(bootstrap_with=new_clause_true)
        glucose4_false = Glucose4(bootstrap_with=new_clause_false)
        result_true = glucose4_true.solve()
        result_false = glucose4_false.solve()
        if result_true and result_false:
            results[query] = '?'
        elif not result_true and result_false:
            results[query] = 'F'
        elif result_true and not result_false:
            results[query] = 'T'
        else:
            print(query, 'Knowledge base is wrong - return empty results')
            return results
    return results
