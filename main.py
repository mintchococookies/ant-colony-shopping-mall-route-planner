import random
import matplotlib.pyplot as plt
from itertools import groupby
from operator import itemgetter
import itertools

#CLASS TO REPRESENT EACH LOCATION IN THE MALL
class Location:
  def __init__(self, name, cat):
    self.name = name
    self.roads = []
    self.coordinates = []
    self.cat = cat
    
  #Set the coordinates of the location  
  def set_coordinates(self, coordinates):
    self.coordinates = coordinates

  #Add roads to the location
  def add_road(self, road):
    if road not in self.roads:
      self.roads.append(road)
      
#CLASS TO REPRESENT THE ROADS CONNECTING ADJACENT LOCATIONS IN THE MALL
class Road:
  def __init__(self, connected_locations, cost, pheromone=0):
    self.connected_locations = connected_locations
    self.cost = cost
    self.pheromone = pheromone
    
  #Set pheromone to the road  
  def set_pheromone(self, pheromone):
    self.pheromone = pheromone
    
  #Evaporate pheromone from the road  
  def evaporate_pheromone(self, rho):
    self.pheromone = (1-rho) * self.pheromone
  
  #Deposit pheromone to the road  
  def deposit_pheromone(self, ants):
    deposited_pheromone = 0
    for ant in ants:
      if self in ant.path:
        if factor == 'Path Cost':
            deposited_pheromone += 5/ant.get_path_length()**1
        elif factor == 'Num Locations':
            deposited_pheromone += 5/ant.get_num_locations_passed()**1
    self.pheromone += deposited_pheromone
    
#CLASS TO REPRESENT THE ANTS USED IN THE ALGORITHM    
class Ant:
  def __init__(self):
    self.locations = []
    self.path = []
    
  #Get optimal path from origin to a list of destinations for an ant  
  def get_path(self, origin, destination, alpha):
    self.locations.append(origin)
    #While not every destination in the list of destinations has been visited, search for the next city
    while not (set(destination).issubset(set(self.locations))): 
      if len(self.path) > 0: 
        available_roads = [r for r in self.locations[-1].roads if r is not self.path[-1]] 
      else:
        available_roads = self.locations[-1].roads
      if len(available_roads) == 0:
        available_roads = [self.path[-1]]
        
      pheromones_alpha = [r.pheromone**alpha for r in available_roads]
      probabilities = [pa/sum(pheromones_alpha) for pa in pheromones_alpha]
      acc_probabilities = [sum(probabilities[:i+1]) for i,p in enumerate(probabilities)]
      chosen_value = random.random()
      
      for ai,ap in enumerate(acc_probabilities):
        if ap > chosen_value:
          break
      
      self.path.append(available_roads[ai])
      if self.path[-1].connected_locations[0] is self.locations[-1]:
        self.locations.append(self.path[-1].connected_locations[1])
      else:
        self.locations.append(self.path[-1].connected_locations[0])

      #Remove loops within the path by identifying repeated cities in the path and removing the roads between them
      while len(set(self.locations)) != len(self.locations):
        for i,location in enumerate(set(self.locations)):
          location_indices = [i for i, x in enumerate(self.locations) if x == location]
          if len(location_indices) > 1:
            self.locations = self.locations[:location_indices[0]] + self.locations[location_indices[-1]:]
            self.path = self.path[:location_indices[0]] + self.path[location_indices[-1]:]
            break

  #Get the length of the path
  def get_path_length(self):
    return sum([road.cost for road in self.path])

  #Get the number of locations passed by the ant
  def get_num_locations_passed(self):
      return len(self.path) + 1
  
  #Reset the path and location passed by the ant to zero 
  def reset(self):
    self.locations = []
    self.path = []

#FUNCTION TO CALCULATE THE DISTANCE BETWEEN ADJACENT LOCATIONS AS THE STEP COST
def calculate_step_cost(location_list):
    step_cost = []
    
    #Sort the locations by rows (y) and columns (x) into groups. The locations in each group share either the same x or y coordinate
    x_groups = [list(c) for _, c in groupby(sorted(location_list, key = lambda x: int(x[0])), key=itemgetter(0))]
    y_groups = [list(c) for _, c in groupby(sorted(location_list, key = lambda x: int(x[1])), key=itemgetter(1))]
    groups = x_groups + y_groups
    
    #Get the costs between all possible pairs of locations that share the same x or y coordinate
    for group in groups:
        for i in range (0, len(group)):
            temp_costs = []
            for j in range (0, len(group)):
                if group[i][2] == group[j][2] or group[i][4] == 'Elevation' or group[j][4] == 'Elevation' : #on the same floor or is an escalator
                    temp_cost = abs(group[i][0] - group[j][0]) + abs(group[i][1] - group[j][1])
                    temp_step = [group[i][3], group[j][3], temp_cost]                        
                    if temp_cost != 0 and temp_step not in step_cost:
                        temp_costs.append(temp_step)
           
            #To limit the roads to be between only immediately adjacent locations
            temp_costs = sorted(temp_costs, key = lambda x: int(x[2]))
            y_limit = [min(y[1] for y in group), max(y[1] for y in group)] #The range of y coordinates to allow us to find locations that are at the edge of the map
            x_limit = [min(x[0] for x in group), max(x[0] for x in group)] #The range of x coordinates to allow us to find locations that are at the edge of the map
            #If its at the edge of the map, there can be only 1 location nearest to it, hence add the lowest step cost to the step costs
            #If its not at the edge, means it's between two locations, hence add the two lowest step costs to the step costs
            if group[i][0] not in x_limit or group[i][1] not in y_limit:
                step_cost += temp_costs[:2]
            else:
                step_cost += temp_costs[:1]
            
    return step_cost

#FUNCTION TO CREATE LOCATION AND ROAD OBJECTS FROM THE STATE SPACE
def initialize_roads(location_list):
    locations = {}
    for coord1, coord2, floor, name, cat in location_list:
        locations[name] = Location(name, cat)
        locations[name].set_coordinates([coord1, coord2, floor])
      
    step_cost = calculate_step_cost(location_list)
    roads = []
      
    for location1, location2, cost in step_cost:
        road = Road([locations[location1], locations[location2]], cost)
        locations[location1].add_road(road)
        locations[location2].add_road(road)
        roads.append(road)
        
    return locations, roads

#FUNCTION TO OBTAIN AND VALIDATE USER INPUT (1 STRING)
def get_option_input(options):
  choice = input("Selection: ")
  while choice not in options or choice == "":
      print("Please enter only the following options: " + str(options))
      choice = input("Selection: ")
  return choice

#FUNCTION TO OBTAIN AND VALIDATE ONE USER INPUT (LIST)
def get_list_input(options):
    choices = input("Selection: ")
    choices = choices.split(',')
    while not set(choices).issubset(set(options)) or choices == "":
        print("Please enter only the following options: " + str(options))
        choices = input("Selection: ")
        choices = choices.split(',')
    return choices

#FUNCTION TO GET THE INDIVIDUAL PATH DETAILS FOR ALL ANTS
def get_frequency_of_paths(ants):
  paths = []
  locations = []
  frequencies = []
  path_cost = []
  num_locations_passed = []
  for ant in ants:
    if len(ant.path) != 0:
      if ant.path in paths:
        frequencies[paths.index(ant.path)] += 1
      else:
        paths.append(ant.path)
        locations.append(ant.locations)
        frequencies.append(1)
        path_cost.append(ant.get_path_length())
        num_locations_passed.append(ant.get_num_locations_passed())
  return [frequencies, paths, locations, path_cost, num_locations_passed]

#FUNCTION TO GET THE PERCENTAGE OCCURENCE IN 20 INSTANCES FOR THE PATH WHICH OCCURS THE MOST FREQUENTLY
def get_percentage_of_dominant_path(ants):
  [frequencies, _, _, _, _] = get_frequency_of_paths(ants)
  if len(frequencies) == 0:
    percentage = 0
  else:
    percentage = max(frequencies)/sum(frequencies)
  return percentage

#FUNCTION TO FIND THE OPTIMAL PATH BETWEEN TWO LOCATIONS
def find_path(origin, destination):
  for road in roads:
     road.set_pheromone(initial_pheromone)
  for ant in ants:
      ant.reset()
      
  iteration = 0
  while (iteration < max_iteration and get_percentage_of_dominant_path(ants) < percentage_of_dominant_path): # termination conditions
    for ant in ants: # loop through all the ants to identify the path of each ant
      ant.reset() # reset the path of the ant
      ant.get_path(origin, destination, alpha) # identify the path of the ant
    for road in roads: # loop through all roads
      road.evaporate_pheromone(rho) # evaporate the pheromone on the road
      road.deposit_pheromone(ants) # deposit the pheromone
    iteration += 1 # increase iteration count
    
  # after exiting the loop, return the most occurred path as the solution
  [freq, paths, locations_used, path_cost, num_locations_passed] = get_frequency_of_paths(ants)
  path = [c.name for c in locations_used[freq.index(max(freq))]]
  path_cost = path_cost[freq.index(max(freq))]  
  num_locations_passed = num_locations_passed[freq.index(max(freq))]
  
  return path, path_cost, num_locations_passed

#FUNCTION TO INITIATE THE find_path FUNCTION IF THE USER VISITS SHOPS BY CATEGORY
def search_by_category(option, cat_to_visit):
      paths = []
      shops_in_cat = [location.name for key, location in locations.items() if (location.cat == cat_to_visit)] #Filters the state space for the shops in that category
      
      #Find the path to the nearest shop in the category
      if option == "1": 
          for shop in shops_in_cat:
                paths.append(find_path(locations[entered_door], [locations[shop]])) #Find and save the optimal paths to all the shops in the category based on the global factor selected by the user
          if factor == 'Path Cost':
              shop_path_cost = min(paths, key=lambda x:x[1]) #Get the minimum of the path costs among all paths found
          elif factor == 'Num Locations':
              shop_path_cost = min(paths, key=lambda x:x[2]) #Get the minimum of the number of locations passed among all paths found
          shop_path = paths[paths.index(shop_path_cost)][0]
          num_locations_passed = paths[paths.index(shop_path_cost)][2]
          selected_shops = shops_in_cat[paths.index(shop_path_cost)]
          shop_path_cost = shop_path_cost[1]
    
     #Find the path to visit all the shops in the category
      elif option == "2":
          selected_shops = shops_in_cat
          shop_path, shop_path_cost, num_locations_passed = find_path(locations[entered_door], [locations[x] for x in shops_in_cat])
      
      return selected_shops, shop_path, shop_path_cost, num_locations_passed
  
#FUNCTION TO INITIATE THE find_path FUNCTION IF THE USER VISITS SHOPS BY NAME
def search_by_name(shops_to_visit):
    shops_to_visit = ['Shop ' + s for s in shops_to_visit]
    shop_path, shop_path_cost, num_locations_passed = find_path(locations[entered_door], [locations[x] for x in shops_to_visit])
    
    return shops_to_visit, shop_path, shop_path_cost, num_locations_passed

#FUNCTION TO FIND THE NEAREST DOOR AND THE COST BASED ON THE FACTOR
def get_path_to_nearest_exit():
  paths_to_door = []
  
  doors = [location.name for key, location in locations.items() if (location.cat == 'Door')] #Filter all the doors from the state space
  for door in doors:
        paths_to_door.append(find_path(locations[shop_path[-1]], [locations[door]])) #Find and save the optimal paths to all the doors from the last location in the path
  
  if factor == 'Path Cost':
      nearest_door = paths_to_door[paths_to_door.index(min(paths_to_door, key=lambda x:x[1]))] #Get the path to the door with the minimum path cost among all saved paths
  elif factor == 'Num Locations':
      nearest_door = paths_to_door[paths_to_door.index(min(paths_to_door, key=lambda x:x[2]))] #Get the path to the door with the minimum number of locations passed among all saved paths
  
  return nearest_door[0], nearest_door[1]
  
#FUNCTION TO DRAW THE GRAPH FOR ONE FLOOR FOR VISUALIZATION
def create_graph(locations, floor):
  ax = fig.add_subplot(1,2, floor)
  level = [shop for shop in location_list if (shop[2] == floor or shop[4] == 'Elevation')]
  locations_x = [location.coordinates[0] for key, location in locations.items() if (location.coordinates[2] == floor or location.cat == 'Elevation')]
  locations_y = [location.coordinates[1] for key, location in locations.items() if (location.coordinates[2] == floor or location.cat == 'Elevation')]
  ax.scatter(locations_x, locations_y)
  ax.set_aspect(aspect=1.0)
  ax.invert_yaxis()
  ax.title.set_text('Floor ' + str(floor))
  
  for i, name in enumerate(level):
      ax.annotate(name[3], (locations_x[i], locations_y[i]))
  return ax

#FUNCTION TO DRAW PHEROMONE ON THE GRAPH FOR VISUALIZATION
def draw_pheromone(ax, roads):
  lines = []
  for road in roads:
    from_coord = road.connected_locations[0].coordinates
    to_coord = road.connected_locations[1].coordinates
    coord_x = [from_coord[0], to_coord[0]]
    coord_y = [from_coord[1], to_coord[1]]
    lines.append(ax.plot(coord_x, coord_y, c='k', linewidth=road.pheromone**2)) #add a line between the two identified coordinates   
  
#FUNCTION TO DRAW THE PHEROMONE FOR LEVEL 1 ON THE LEVEL 1 GRAPH AND THE PHEROMONE FOR LEVEL 2 ON THE LEVEL 2 GRAPH
def draw_final_path(final_route):
      def pairwise(iterable): #function to get pairs of adjacent locations in the path
          a, b = itertools.tee(iterable)
          next(b, None)
          return zip(a, b)
      
      road_1 = []
      road_2 = []
      for x, y in pairwise(final_route):
          for road in roads:
              road.set_pheromone(0.5)
              if (road.connected_locations[0].coordinates[2] == 1) and (((road.connected_locations[0].name == x) and (road.connected_locations[1].name == y)) or ((road.connected_locations[0].name == y) and (road.connected_locations[1].name == x))): #the shop is on level 1
                  road_1.append(road)
              elif (road.connected_locations[0].coordinates[2] == 2) and (((road.connected_locations[0].name == x) and (road.connected_locations[1].name == y)) or ((road.connected_locations[0].name == y) and (road.connected_locations[1].name == x))): #the shop is on level 1
                  road_2.append(road)
                  
      draw_pheromone(ax1, road_1)
      draw_pheromone(ax2, road_2)
 
#STATE SPACE
location_list = [ # [x, y, floor, name, type]
  [100, 500, 1, 'Door 1', 'Door'],
  [100, 300, 1, 'Shop 1', 'Fashion'],
  [100, 100, 1, 'Shop 2', 'F&B'],
  [400, 100, 1, 'Shop 3', 'Jewellery'],
  [700, 100, 1, 'Shop 4', 'Children'],
  [1000, 300, 1, 'Door 2', 'Door'],
  [1000, 500, 1, 'Shop 5', 'Entertainment'],
  [1000, 750, 1, 'Shop 6', 'Digital'],
  [700, 750, 1, 'Shop 7', 'F&B'],
  [500, 750, 1, 'Shop 8', 'Jewellery'],
  [200, 750, 1, 'Shop 9', 'Digital'],
  [400, 500, 1, 'Shop 10', 'Children'],
  [700, 500, 1, 'Shop 11', 'Digital'],
  [700, 300, 1, 'Shop 12', 'Entertainment'],
  [100, 750, 1, 'Lift', 'Elevation'],
  [1000, 100, 1, 'Escalator', 'Elevation'],
  
  [100, 550, 2, 'Shop 13', 'Digital'],
  [100, 400, 2, 'Shop 14', 'Fashion'],
  [100, 300, 2, 'Shop 15', 'Children'],
  [100, 100, 2, 'Shop 16', 'Fashion'],
  [400, 550, 2, 'Shop 17', 'F&B'],
  [400, 300, 2, 'Shop 18', 'Jewellery'],
  [750, 550, 2, 'Shop 19', 'Entertainment'],
  [750, 400, 2, 'Shop 20', 'F&B'],
  [750, 300, 2, 'Shop 21', 'Entertainment'],
  [1000, 750, 2, 'Shop 22', 'Jewellery'],
  [1000, 550, 2, 'Shop 23', 'Fashion'],
  [1000, 300, 2, 'Shop 24', 'Children']
]
   
#MAIN
if __name__ == "__main__":
  locations, roads = initialize_roads(location_list)
  
  n_ant = 20
  alpha = 1
  rho = 0.5
  initial_pheromone = 0.001
  for road in roads:
    road.set_pheromone(initial_pheromone)
    
  ants = [Ant() for _ in range(n_ant)]
  
  #Termination threshold
  max_iteration = 200
  percentage_of_dominant_path = 0.9
  
  print("|| This program uses the Ant Colony Optimization Algorithm to find an optimal route to visit selected shops in a mall. ||\n")
 
  #USER INPUT TO CALL THE SEARCH FUNCTIONS
  #1. Select the factor to determine how optimal a path is
  print("===== Step 1: Select Factor for Optimal Route =====")
  print("Enter 1 for the route containing as few locations as possible")
  print("Enter 2 for the route with the shortest walking distance")
  choice = get_option_input([str(x) for x in range(1, 2 + 1)])
  if choice == '1':
      factor = 'Num Locations'
  elif choice == '2':
      factor = 'Path Cost'

  #2. Select the door used as the entrance
  print("\n===== Step 2: Select Entered Door =====")
  print("Enter 1 for Door 1")
  print("Enter 2 for Door 2")
  choice = get_option_input([str(x) for x in range(1, 2 + 1)])
  entered_door = 'Door ' + choice
    
  #3. Select the method to choose shops to visit
  print("\n===== Step 3: Select Shop Selection Method =====")
  print("Enter 1 to visit shops by category")
  print("Enter 2 to visit shops by name")
  choice = get_option_input([str(x) for x in range(1, 2 + 1)])
  
  if choice == "1":
     print("\n===== Step 4: Select Shop Category =====")
     print("1 - Children, 2 - Jewellery, 3 - Digital, 4 - F&B, 5 - Fashion, 6 - Entertainment")
     choice = get_option_input([str(x) for x in range(1, 6 + 1)])
     categories = ['Children', 'Jewellery', 'Digital', 'F&B', 'Fashion', 'Entertainment']
     cat_to_visit = categories[int(choice)-1]
     
     print("\n===== Step 5: Select Shops to Visit in Category =====")
     print("Enter 1 to visit the nearest shop in this category")
     print("Enter 2 to visit all shops in this category")
     choice = get_option_input([str(x) for x in range(1, 2 + 1)])
     selected_shops, shop_path, shop_path_cost, num_locations_passed = search_by_category(choice, cat_to_visit)
      
  elif choice == "2":
      print("\n===== Step 4: Select Shop Name(s) =====")
      print("Enter one or more shop names from 1-24 seperated by commas (e.g. 1,2,3,4,5)")
      shops_to_visit = get_list_input([str(x) for x in range(1, 24 + 1)])
      selected_shops, shop_path, shop_path_cost, num_locations_passed = search_by_name(shops_to_visit)
      
  #GET PATH TO NEAREST EXIT FROM THE LAST LOCATION IN THE IDENTIFIED PATH
  nearest_door, cost_to_door = get_path_to_nearest_exit()
  
  #GETTING THE FINAL ROUTE
  final_route = shop_path + nearest_door[1:] #Concatenate the path to shop with the path from the last shop to the nearest exit
  final_path_cost = shop_path_cost + cost_to_door
  num_locations_passed = len(final_route)
  
  #DISPLAY THE SOLUTION AND SOLUTION DETAILS
  print("")
  print("===== Solution - Optimal Route to Shop =====")
  print("Selected Shop(s): " + str(selected_shops))
  print("Selected Factor for Optimal Route: " + factor)
  print("Final Route: " + str(final_route))
  print("Total Path Cost: " + str(final_path_cost))
  print("Number of Locations Passed: " + str(num_locations_passed))
  
  #DRAW THE FINAL PATH USING A MATPLOTLIB GRAPH
  fig = plt.figure()
  ax1 = create_graph(locations, 1)
  ax2 = create_graph(locations, 2)
  draw_final_path(final_route)