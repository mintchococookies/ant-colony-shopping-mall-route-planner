# Ant Colony Optimisation Shopping Mall Route Planner

## Description
The goal of this Python program is to identify the optimal route to shop in a mall containing 2 floors and 24
shops of varying sizes. The optimal route can be defined using either one of two different factors.
The first factor is the total walking distance in the calculated route from the entrance to the exit, and
the second factor is the total number of locations in the route from the entrance to the exit. The user
must be able to select the shops they would like to visit, and the algorithm must provide an optimal
path starting from a selected entrance to the nearest exit, containing all the shops to be visited. The
user can choose the shops by entering the names of 1 or more shops, or by entering a department
and choosing to visit either the nearest shop in that department or all the shops in that department.

## Mall layout
![Alt Text](https://github.com/mintchococookies/ant-colony-shopping-mall-route-planner/blob/main/mall-layout.PNG)

## Problem formulation
1. **State Space**: The map of the mall, which is the state space for the problem, is depicted in Figure 1.1.2.
2. **Initial State**: A user attempting to determine the shortest route to visit all the shops that he or she wishes to visit, beginning at a mall entrance and ending at the nearest door to exit.
3. **Final State (Goal)**: The user takes the shortest total walking distance or passes through the fewest number of locations to visit all of the shops that he or she desires to visit.
4. **States**: This is the arrangement of the locations in the mall which include shops, a lift, and an escalator. For example, Shop 1(100, 300, 1, 'Fashion') indicates that Shop 1 is a fashion shop located on the first floor at the x-coordinate of 100 and the y-coordinate of 300.
5. **Actions**: The user can move from one location to any location adjacent to it. For example, Shop 1, Shop 10, and the Lift are located adjacent to Door 1, therefore the applicable actions from Door 1 are `move(Door 1, Shop 1)`, `move(Door 1, Shop 10)`, and `move(Door 1, Lift)`.
6. **Transition Model**: Result (s, a) where 's' denotes the current state and 'a' denotes the action taken on the current state. For example, `Result(Arr(Door 1), Pair(Door 1, Shop 1)) = Arr(Door 1, Shop 1)` indicates that the user proceeds to Shop 1 from Door 1, making Shop 1 and Door 1 successive locations in the path.
7. **Goal Test**: The goal is to reach every desired shop using either the route with the least total walking distance or the route which passes the least number of locations.
8. **Path Cost**: The path cost between any two nodes is the distance between the two shops.

## Sample program output
![Alt Text](https://github.com/mintchococookies/ant-colony-shopping-mall-route-planner/blob/main/aco-output.PNG)

## Sample output on the mall layout depicted in a Matplotlib graph
![Alt Text](https://github.com/mintchococookies/ant-colony-shopping-mall-route-planner/blob/main/routeplanning.png)
The colour of the lines depict the concentration of the pheromones along the path. The darkest lines represent the final solution.
