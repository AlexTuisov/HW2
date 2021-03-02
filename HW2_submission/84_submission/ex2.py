ids = ['209063320', '204795090']
import math

def set_timers(observations):
  observations_timers = list(map(lambda x: list(map(lambda y: list(y) ,x)), observations))
  for row_num in range(2,len(observations[0])):
    for cell_num in range(len(observations[0][row_num])):
      if observations[0][row_num][cell_num] == 'S':
        observations_timers[0][row_num][cell_num] = 3.0
      elif observations[0][row_num][cell_num] == 'Q':
        observations_timers[0][row_num][cell_num] = 2.0
      else:
        observations_timers[0][row_num][cell_num] = math.inf

  for observation_num in range(len(observations)-1):
    for row_num in range(len(observations[observation_num])):
      for cell_num in range(len(observations[observation_num][row_num])):

        if observations[observation_num][row_num][cell_num] == observations[observation_num+1][row_num][cell_num] and isinstance(observations_timers[observation_num][row_num][cell_num], float):
          observations_timers[observation_num+1][row_num][cell_num] = float(observations_timers[observation_num][row_num][cell_num]) -1

        if observations[observation_num][row_num][cell_num] == 'S':
          if observations[observation_num+1][row_num][cell_num] == 'Q':
            observations_timers[observation_num+1][row_num][cell_num] = 2.0
          elif observations[observation_num+1][row_num][cell_num] == 'H':
            observations_timers[observation_num+1][row_num][cell_num] = math.inf

        elif observations[observation_num][row_num][cell_num] == 'H':
          observations_timers[observation_num][row_num][cell_num] = math.inf
          if observations[observation_num+1][row_num][cell_num] == 'I':
            observations_timers[observation_num+1][row_num][cell_num] = math.inf
          elif observations[observation_num+1][row_num][cell_num] == 'S':
            observations_timers[observation_num+1][row_num][cell_num] = 3.0

  return observations_timers


def deduce_unchenged_cells(observations,observations_timers):
  for observation_num in range(len(observations)):
    for row_num in range(len(observations[observation_num])):
      for cell_num in range(len(observations[observation_num][row_num])):

        if observations[observation_num][row_num][cell_num] == 'I':
          for observation_num2 in range(observation_num,len(observations)):
            observations[observation_num2][row_num][cell_num] = 'I'
            observations_timers[observation_num2][row_num][cell_num]  = math.inf

        elif observations[observation_num][row_num][cell_num] == 'U':
          for observation_num2 in range(len(observations)):
                observations[observation_num2][row_num][cell_num] = 'U'
                observations_timers[observation_num2][row_num][cell_num]  = math.inf

        if observations[observation_num][row_num][cell_num] =='?' and (observation_num != 0) and (observation_num < len(observations)-1):
          if observations[observation_num-1][row_num][cell_num] == 'S' and observations[observation_num+1][row_num][cell_num] == 'S' and observations_timers[observation_num-1][row_num][cell_num] == 3:          
            observations[observation_num][row_num][cell_num] = 'S'
            observations_timers[observation_num-1][row_num][cell_num]  = 3.0
            observations_timers[observation_num][row_num][cell_num]  = 2.0
            observations_timers[observation_num+1][row_num][cell_num]  = 1.0

          elif observations[observation_num-1][row_num][cell_num] == 'H' and observations[observation_num+1][row_num][cell_num] == 'H':
            observations[observation_num][row_num][cell_num] = 'H'
            observations_timers[observation_num][row_num][cell_num]  = math.inf
  return observations, observations_timers

def deduce_taken_actions(observations):
  actions =  [{'police_actions_taken' : 0,'medics_actions_taken' : 0} for i in range(len(observations)-1)]
  for observation_num in range(len(observations)-1):
    for row_num in range(len(observations[observation_num])):
      for cell_num in range(len(observations[observation_num][row_num])):
        if observations[observation_num][row_num][cell_num] == 'H' and observations[observation_num+1][row_num][cell_num] == 'I':
          actions[observation_num]['medics_actions_taken'] += 1
        elif observations[observation_num][row_num][cell_num] == 'S' and observations[observation_num+1][row_num][cell_num] == 'Q':
          actions[observation_num]['police_actions_taken'] += 1
  return actions


def add_padding(matrices, padding):
  for matrix_num in range(len(matrices)):
    matrices[matrix_num] = [[padding]*(len(matrices[matrix_num][0])+4)]*2 + [[padding]*2 + row + [padding]*2 for row in matrices[matrix_num]] + [[padding]*(len(matrices[matrix_num][0])+4)]*2
  return matrices

def remove_padding(matrices):
  unwrapped = []
  for matrix_num in range(len(matrices)):
    matrix = []
    for row_num in range(2,len(matrices[matrix_num])-2):
      matrix.append(matrices[matrix_num][row_num][2:-2])
    unwrapped.append(matrix)
  return unwrapped


def get_neighbors(matrix,row_num,cell_num):
  neighbors = []
  neighbors.append(matrix[row_num-1][cell_num])
  neighbors.append(matrix[row_num][cell_num+1])
  neighbors.append(matrix[row_num+1][cell_num])
  neighbors.append(matrix[row_num][cell_num-1])
  return neighbors

def forward_propagation(observations,observations_timers,actions,police_teams,medics_teams):

  for observation_num in range(len(observations)-1):
    police_actions_left = police_teams - actions[observation_num]['police_actions_taken']
    medics_actions_left = medics_teams - actions[observation_num]['medics_actions_taken']

    for row_num in range(2,len(observations[observation_num])-2):
      for cell_num in range(2,len(observations[observation_num][row_num])-2):

        if observations[observation_num+1][row_num][cell_num] == '?':

          if observations[observation_num][row_num][cell_num] == '?':
            current_neighbors = get_neighbors(observations[observation_num],row_num,cell_num)
            next_neighbors = get_neighbors(observations[observation_num+1],row_num,cell_num)
            neighbors_locations = get_neighbors_locations(row_num,cell_num)
            for neighbor_num in range(4):
              if current_neighbors[neighbor_num] == 'H' and next_neighbors[neighbor_num] == 'S':
                neighbors_of_H_neighbor = get_neighbors(observations[observation_num],neighbors_locations[neighbor_num][0],neighbors_locations[neighbor_num][1])
                if neighbors_of_H_neighbor.count('S') == 0 and neighbors_of_H_neighbor.count('?') == 1:
                  observations[observation_num][row_num][cell_num] = 'S'
                  observations_timers[observation_num][row_num][cell_num] = 3.0

          if observations[observation_num][row_num][cell_num] == 'S':
            if observations_timers[observation_num][row_num][cell_num] == 1 and police_actions_left == 0:
              observations[observation_num+1][row_num][cell_num] = 'H'
              observations_timers[observation_num+1][row_num][cell_num] = math.inf
            elif observations_timers[observation_num][row_num][cell_num] > 1 and police_actions_left == 0:
              observations[observation_num+1][row_num][cell_num] = 'S'
              observations_timers[observation_num+1][row_num][cell_num] = observations_timers[observation_num][row_num][cell_num] - 1
            elif police_actions_left > 0:
              current_neighbors = get_neighbors(observations[observation_num],row_num,cell_num)
              next_neighbors = get_neighbors(observations[observation_num+1],row_num,cell_num)
              for neighbor_num in range(4):
                if current_neighbors[neighbor_num] == 'H' and next_neighbors[neighbor_num] == 'H':
                  observations[observation_num+1][row_num][cell_num] = 'Q'
                  observations_timers[observation_num+1][row_num][cell_num] = 2.0
                  police_actions_left -= 1

          elif observations[observation_num][row_num][cell_num] == 'H':
            if medics_actions_left == 0:
              current_neighbors = get_neighbors(observations[observation_num],row_num,cell_num)
              if 'S' not in current_neighbors and '?' not in current_neighbors:
                observations[observation_num+1][row_num][cell_num] = 'H'
                observations_timers[observation_num+1][row_num][cell_num] = math.inf
              elif 'S' in current_neighbors :
                observations[observation_num+1][row_num][cell_num] = 'S'
                observations_timers[observation_num+1][row_num][cell_num] = 3.0
            if police_actions_left == 0:
              current_neighbors = get_neighbors(observations[observation_num],row_num,cell_num)
              next_neighbors = get_neighbors(observations[observation_num+1],row_num,cell_num)
              for neighbor_num in range(4):
                if current_neighbors[neighbor_num] == 'S' and next_neighbors[neighbor_num] == 'S':
                  observations[observation_num+1][row_num][cell_num] = 'S'
                  observations_timers[observation_num+1][row_num][cell_num] = 3.0
          
          elif observations[observation_num][row_num][cell_num] == 'Q':
            if observations_timers[observation_num][row_num][cell_num] == 1:
              observations[observation_num+1][row_num][cell_num] = 'H'
              observations_timers[observation_num+1][row_num][cell_num] = math.inf
            elif observations_timers[observation_num][row_num][cell_num] == 2:
              observations[observation_num+1][row_num][cell_num] = 'Q'
              observations_timers[observation_num+1][row_num][cell_num] = 1.0

      possible_unknown_action = 0
      possible_police_action = 0
      if police_actions_left > 0:
        for row_num in range(2,len(observations[observation_num])-2):
          for cell_num in range(2,len(observations[observation_num][row_num])-2):
            if observations[observation_num+1][row_num][cell_num] == '?'and observations[observation_num][row_num][cell_num] == 'S':
              possible_police_action += 1
            elif observations[observation_num+1][row_num][cell_num] == '?'and observations[observation_num][row_num][cell_num] == '?':
              possible_unknown_action += 1
        if police_actions_left >= possible_police_action + possible_unknown_action:
          for row_num in range(2,len(observations[observation_num])-2):
            for cell_num in range(2,len(observations[observation_num][row_num])-2):
              if observations[observation_num+1][row_num][cell_num] == '?'and observations[observation_num][row_num][cell_num] == 'S':
                observations[observation_num+1][row_num][cell_num] = 'Q'
                observations_timers[observation_num+1][row_num][cell_num] = 2.0

      possible_medics_action = 0
      if medics_actions_left > 0:
        for row_num in range(2,len(observations[observation_num])-2):
          for cell_num in range(2,len(observations[observation_num][row_num])-2):
            if observations[observation_num+1][row_num][cell_num] == '?' and observations[observation_num][row_num][cell_num] == 'H':
                possible_medics_action += 1
        if medics_actions_left >= possible_medics_action + possible_unknown_action:
          for row_num in range(2,len(observations[observation_num])-2):
            for cell_num in range(2,len(observations[observation_num][row_num])-2):
              if observations[observation_num+1][row_num][cell_num] == '?'and observations[observation_num][row_num][cell_num] == 'H':
                observations[observation_num+1][row_num][cell_num] = 'I'
                observations_timers[observation_num+1][row_num][cell_num] = math.inf


  return observations, observations_timers

def get_neighbors_locations(row_num,cell_num):
  neighbors_locations = [[row_num-1,cell_num],[row_num, cell_num+1],[row_num+1, cell_num],[row_num,cell_num-1]]
  return neighbors_locations

def backward_propagation(observations,observations_timers,actions,police_teams,medics_teams):
  for observation_num in range(len(observations)-1):
    police_actions_left = police_teams - actions[observation_num]['police_actions_taken']
    #medics_actions_left = medics_teams - actions[observation_num]['medics_actions_taken']

    for row_num in range(2,len(observations[observation_num])-2):
      for cell_num in range(2,len(observations[observation_num][row_num])-2):

        if observations[observation_num][row_num][cell_num] == '?':

          if observations[observation_num+1][row_num][cell_num] == 'Q' and police_actions_left == 0:
            observations[observation_num][row_num][cell_num] = 'Q'
            observations_timers[observation_num][row_num][cell_num] = 2.0
            observations_timers[observation_num+1][row_num][cell_num] = 1.0

          elif observations[observation_num+1][row_num][cell_num] == 'S':
            current_neighbors = get_neighbors(observations[observation_num],row_num,cell_num)
            next_neighbors = get_neighbors(observations[observation_num+1],row_num,cell_num)
            for neighbor_num in range(4):
                if current_neighbors[neighbor_num] == 'H' and next_neighbors[neighbor_num] == 'H':
                  observations[observation_num][row_num][cell_num] = 'H'
                  observations_timers[observation_num][row_num][cell_num] = math.inf
                  observations_timers[observation_num+1][row_num][cell_num] = 2.0
                elif current_neighbors[neighbor_num] == 'H' and next_neighbors[neighbor_num] == 'S':
                  neighbors_locations = get_neighbors_locations(row_num,cell_num)
                  neighbors_of_S_neighbor = get_neighbors(observations[observation_num],neighbors_locations[neighbor_num][0],neighbors_locations[neighbor_num][1])
                  if neighbors_of_S_neighbor.count('S') == 0 and neighbors_of_S_neighbor.count('?') == 1:
                    observations[observation_num][row_num][cell_num] = 'S'

          elif observations[observation_num+1][row_num][cell_num] == 'H':
            current_neighbors = get_neighbors(observations[observation_num],row_num,cell_num)
            next_neighbors = get_neighbors(observations[observation_num+1],row_num,cell_num)
            not_S = False #check if its not S
            for neighbor_num in range(4):
              if current_neighbors[neighbor_num] == 'H' and next_neighbors[neighbor_num] == 'H':
                not_S = True
            has_S_neighbor = False  # check if it has S neighbor that hasnt been quarantined 
            for neighbor_num in range(4):
              if current_neighbors[neighbor_num] == 'S' and (next_neighbors[neighbor_num] != 'Q' or police_actions_left == 0) :
                has_S_neighbor = True
            if not_S and has_S_neighbor:
              observations[observation_num][row_num][cell_num] = 'Q'
              observations_timers[observation_num][row_num][cell_num] = 1.0
              observations_timers[observation_num+1][row_num][cell_num] = math.inf
            elif not_S and not has_S_neighbor and observation_num==0:
              observations[observation_num][row_num][cell_num] = 'H'
              observations_timers[observation_num][row_num][cell_num] = math.inf
              observations_timers[observation_num+1][row_num][cell_num] = math.inf
            else:
              neighbors_locations = get_neighbors_locations(row_num,cell_num)
              for neighbor_num in range(4):
                if current_neighbors[neighbor_num] == 'H' and next_neighbors[neighbor_num] == 'S':
                  neighbors_of_S_neighbor = get_neighbors(observations[observation_num],neighbors_locations[neighbor_num][0],neighbors_locations[neighbor_num][1])
                  if neighbors_of_S_neighbor.count('S') == 0 and neighbors_of_S_neighbor.count('?') == 1:
                     observations[observation_num][row_num][cell_num] = 'S'
                     observations_timers[observation_num][row_num][cell_num] = 1.0
                     observations_timers[observation_num+1][row_num][cell_num] = math.inf

  return observations, observations_timers




def solve_problem(state):
    police_teams = state['police']; medics_teams = state['medics'];
    observations =  list(map(lambda x: list(map(lambda y: list(y) ,x)), state['observations']))
    observations = add_padding(observations, 'U')

    last_observations = []
    while(observations not in [last_observations]):
      last_observations =  list(map(lambda x: list(map(lambda y: list(y) ,x)), observations))
      observations_timers = set_timers(observations)
      actions = deduce_taken_actions(observations)
      observations, observations_timers = deduce_unchenged_cells(observations,observations_timers)
      observations,observations_timers = forward_propagation(observations,observations_timers,actions,police_teams,medics_teams)
      observations,observations_timers = backward_propagation(observations,observations_timers,actions,police_teams,medics_teams)
      observations_timers = set_timers(observations)
      
    observations = remove_padding(observations)

    ans = {}
    for query in state['queries']:
        if observations[query[1]][query[0][0]][query[0][1]] == query[2]:
            ans.update({query:'T'})
        elif observations[query[1]][query[0][0]][query[0][1]] =='?':
             ans.update({query:'?'})
        else:
            ans.update({query:'F'})


    return ans