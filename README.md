# two-towers-game-mpi

Bogazici University

Computer Engineering Department

Fall 2021

CMPE 300 - Analysis of Algorithms

Project 2

Altay Acar & Engin Oguzhan Senol

***

A simulation of a board game called Two Towers, in which two tower types are placed onto a game board and progress round by round by attacking each other using MPI for parallel programming.

Rules:

The game board, which is an N-dimensional orthogonal grid (map). We have a 2-dimensional orthogonal grid as a map (i.e. a matrix). Each cell on the map can either contain a certain type of tower (‘o’ or ‘+’) or be empty (‘.’). The 8 cells that are immediately around a cell are considered as its neighbors:
- The map’s state at time t = 0 is as initialized.
- To calculate the map’s state at time t = 1, we look at the state at time t = 0. For each cell on the map at time t = 1, we look at the same cell and its neighbors at time t = 0.
- We keep on simulating like this until time t = T .

The game will be played for W waves. And each wave consists of 8 rounds. So the total game time will be W × 8. At the start of each wave, new towers will be added to the map.

Towers are the main items of the game. Towers have health points and attack powers. Towers can be placed at any empty place on the map. Towers attack their neighbours in each round simultaneously. If a tower is attacked, its health points are reduced. If a tower’s health drops to 0 or below, then the tower gets destroyed. A tower can attack more than one tower in one round. A tower can be attacked by more than one tower in one round. Towers differentiate with each other by their attack patterns, health points and attack powers. A tower does not attack same type of towers. There are two types of towers:
– ‘o’ tower: Health Point: 6, Attack Power: 1, Attack pattern: Hits all its neighbors.
– ‘+’ tower: Health Point: 8, Attack Power: 2, Attack pattern: Hits up, down, left and right neighbors like a plus (‘+’) shaped attack.

The missing neighbors are taken as empty.

Initialize the map with empty cells and then iterate for W waves by putting new towers to the map and iterating for 8 rounds for each wave.

The job of the manager (rank = 0) process:
1. Reading input from input.txt.
2. Splitting the coordinates into completely separate (i.e. disjoint) parts and sending them to the
workers. A coordinate should not be sent to more than one processor.
3. Receiving the results from the workers, and their aggregation.
4. Writing the final map to output.txt.

The job of the worker (rank = 1, ..., P) processes:
1. Receiving the data from the manager.
2. Carrying out the simulation. In the mean time, communicating with the other workers when necessary.
  • Each worker process should keep track of the health and the location of its towers.
3. Sending the data back to manager after W waves.

Testing:
- The code will be run using the command below to the CLI:
  > mpiexec -n [P] python game.py input.txt output.txt
[P] is the number of processes to run game on. If you want to have P = 8 worker processes, then you need 9 processes in total, accounting for the manager. Hence, you should write -n 9 in the command line. Arguments input.txt and output.txt are passed onto game as command line arguments.

Input & Output:
- The input.txt will contain the size of the map (N), number of waves (W), the number of towers to be placed for each tower type per wave (T) and the coordinates of towers for each wave. Top left coordinate of the map is (0, 0) and bottom right coordinate of the map is (n − 1, n − 1). There will be T number of ‘o’ towers and T number of ‘+’ towers added to map per wave (if possible.)

A report about our project is provided via cmpe300-project2-report.pdf file.
