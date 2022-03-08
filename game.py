# Author 1: Altay Acar - 2018400084
# Author 2: Engin Oguzhan Senol - 2020400324
# Compiling
# Working

import sys
from mpi4py import MPI
import numpy as np

# initialization of the mpi communication
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
p_num = size - 1	# number of workers

# fills the given cell of [r (parameter 3), c (parameter 4)) in the game board
# with the given tower type t (parameter 2) and the health of the tower is put
# in the game_board_h (parameter 0) array alongside the tower type in the game_board_t (parameter 1) array
def fill_board(game_board_h, game_board_t, t, r, c):
	# fills the cell if there is not any pre-existing tower (finds it by checking the corresponging health field)
	if game_board_h[r][c] <= 0:
		if t == 'o':
			game_board_t[r][c] = 'o'
			game_board_h[r][c] = 6
		else:
			game_board_t[r][c] = '+'
			game_board_h[r][c] = 8

output_file = open(sys.argv[2], 'a')	# output.txt file given in the second command line argument

input_file = open(sys.argv[1], 'r')	# input.txt file given in the first command line argument
# reads each line in the input.txt file and splits it into lines
lines = input_file.readlines()
lines = [line.rstrip() for line in lines]
input_file.close()

initials = lines[0].split()	# integers given in the first line

lines.pop(0)	# first line is removed from the line list after it is done with

board_size = int(initials[0])	# size (n) of the game board of n*n
num_of_waves = int(initials[1])	# total number of waves
num_of_towers = int(initials[2])	# total number of towers to be added in each wave

# convention: game_board_h[row][column] or game_board_t[row][column]
game_board_h = [[0 for x in range(board_size)] for y in range(board_size)]	# health values of each tower in the corresponging cell, initially all zero
game_board_t = [['.' for x in range(board_size)] for y in range(board_size)]	# types of each tower in the corresponging cell, initially all '.'

# runs the operation for each wave, after each wave the health values and tower types values are updated in the corresponding 2d array 
for wave in range(num_of_waves):
	if rank == 0:
		# manager process	
		o_towers = lines[(wave*2)].split(',')	# 'o' type towers to be added
		t_towers = lines[(wave*2)+1].split(',')	# '+' type towers to be added
		# adds each tower in the given cell of the board, if there is not any preexisting tower
		# initially all cells have '.' type and 0 health, meaning each cell is empty. So every tower in the initial iteration is added successfully
		for t in range(num_of_towers):
			o_row = int(o_towers[t].split()[0])
			o_column = int(o_towers[t].split()[1])
			t_row = int(t_towers[t].split()[0])
			t_column = int(t_towers[t].split()[1])
			fill_board(game_board_h, game_board_t, '+', t_row, t_column)
			fill_board(game_board_h, game_board_t, 'o', o_row, o_column)

		factor = board_size // p_num	# indicator of how many rows each worker process is responsible for

		# runs for each worker process
		for p in range(1, p_num+1):
			# creates a portion of the current game board containing each row a worker process is responsible for
			tower_data = [['.' for x in range(board_size)] for y in range(factor)]	# an empty 2d-array
			# empty 2-d array is filled with current values
			for row in range(factor):
				for column in range(board_size):
					tower_data[row][column] = game_board_t[row+(p-1)*factor][column]
			tower_data_np = np.array(tower_data, dtype='|S1')	# numpy array form of the 2d-array

			health_data = [[0 for x in range(board_size)] for y in range(factor)]	# an empty 2d-array
			# empty 2-d array is filled with current values
			for row in range(factor):
				for column in range(board_size):
					health_data[row][column] = game_board_h[row+(p-1)*factor][column]
			health_data_np = np.array(health_data, dtype=np.int8)	# numpy array form of the 2d-array
			# dimensions of the portion of the game board that the worker process is responsible for is sent to each worker process
			dimension = np.array([board_size, factor], dtype=np.int8)
			comm.Send(dimension, dest=p, tag=10)
			# numpy array of health data of the portion of the game board that the worker process is responsible for is sent to each worker process
			comm.Send(health_data_np, dest=p, tag=11)
			# numpy array of tower type data of the portion of the game board that the worker process is responsible for is sent to each worker process
			comm.Send(tower_data_np, dest=p, tag=12)
		# after each worker process executes their computation, master process receives the results from each worker process
		temp_h_data = np.array([])	# health data after one wave
		temp_t_data = np.array([])	# tower data after one wave
		# Concatenates the result of each worker process in the process order
		for p in range(1, p_num+1):
			# health and tower data from a worker process' computation
			current_t = np.empty((factor, board_size), dtype='|S1')
			current_h = np.empty((factor, board_size), dtype=np.int8)
			comm.Recv(current_t, source=p, tag=31)	# tower data from a worker process' computation received from the worker process
			comm.Recv(current_h, source=p, tag=32)	# health data from a worker process' computation received from the worker process
			if len(temp_h_data):
				temp_h_data = np.concatenate((temp_h_data, current_h))
				temp_t_data = np.concatenate((temp_t_data, current_t))
			else:
				# initial result is assigned, not concatenated
				temp_h_data = current_h
				temp_t_data = current_t
		# result of each wave is assigned to their respective arrays		
		game_board_h = temp_h_data
		game_board_t = temp_t_data
	else:
		# worker process
		dimension = np.empty(2, dtype=np.int8)	# dimensions of the portion of game board
		comm.Recv(dimension, source=0, tag=10)	# dimensions of the portion of game board is received from the manager process
		h_data = np.empty((int(dimension[1]), int(dimension[0])), dtype=np.int8)	# health data of the portion of game board
		comm.Recv(h_data, source=0, tag=11)	# health data of the portion of game board is received from the manager process
		t_data = np.empty((int(dimension[1]), int(dimension[0])), dtype='|S1')	# tower data of the portion of game board
		comm.Recv(t_data, source=0, tag=12)	# tower data of the portion of game board is received from the manager process
		# runs for 8 times for each wave
		for i in range(8):
			# directs the communication by splitting it between the odd numbered processes and even numbered processes	
			if rank % 2 == 0:
				# Even process
				# top row of the even process
				top_row_t = np.empty(int(dimension[0]), dtype='|S1')
				top_row_h = np.empty(int(dimension[0]), dtype=np.int8)
				# receives above process' last row from its above process
				comm.Recv(top_row_t, source=rank-1, tag=20)
				comm.Recv(top_row_h, source=rank-1, tag=21)
				if rank != p_num:
					# sends its last row to the below process if it is not the last process
					comm.Send(t_data[-1], dest=rank+1, tag=20)
					comm.Send(h_data[-1], dest=rank+1, tag=21)
				# bottom row of the even process
				bottom_row_t = np.empty(int(dimension[0]), dtype='|S1')
				bottom_row_h = np.empty(int(dimension[0]), dtype=np.int8)
				if rank != p_num:
					# recevies below process' first row from its below process if it is not the last process
					comm.Recv(bottom_row_t, source=rank+1, tag=22)
					comm.Recv(bottom_row_h, source=rank+1, tag=23)
				# sends its first row to the above process
				comm.Send(t_data[0], dest=rank-1, tag=22)
				comm.Send(h_data[0], dest=rank-1, tag=23)
			else:
				# Odd process
				# top row of the odd process
				top_row_t = np.empty(int(dimension[0]), dtype='|S1')
				top_row_h = np.empty(int(dimension[0]), dtype=np.int8)
				# sends its last row to the below process
				comm.Send(t_data[-1], dest=rank+1, tag=20)
				comm.Send(h_data[-1], dest=rank+1, tag=21)
				if rank != 1:
					# recevies above process' last row from its above process if it is not the first process
					comm.Recv(top_row_t, source=rank-1, tag=20)
					comm.Recv(top_row_h, source=rank-1, tag=21)
				# bottom row of the even process
				bottom_row_t = np.empty(int(dimension[0]), dtype='|S1')
				bottom_row_h = np.empty(int(dimension[0]), dtype=np.int8)
				if rank != 1:
					# sends its first row to the above process if it is not the first process
					comm.Send(t_data[0], dest=rank-1, tag=22)
					comm.Send(h_data[0], dest=rank-1, tag=23)
				# receives below process' first row from its below process
				comm.Recv(bottom_row_t, source=rank+1, tag=22)
				comm.Recv(bottom_row_h, source=rank+1, tag=23)
			# does the computation of health for each turn in a wave
			if rank == 1:
				# First process
				t_data = np.concatenate((t_data, [bottom_row_t]))
				h_data = np.concatenate((h_data, [bottom_row_h]))
				for row in range(0, dimension[1]):
					for column in range(0, dimension[0]):
						if t_data[row][column] != b'.':
							for i in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
								if row+i[0] >= 0 and column+i[1] >= 0 and column+i[1] < dimension[0]:
									if t_data[row+i[0]][column+i[1]] == b'+' and t_data[row][column] != b'+':
										h_data[row][column] = h_data[row][column] - 2
									elif t_data[row+i[0]][column+i[1]] == b'o' and t_data[row][column] != b'o':
										h_data[row][column] = h_data[row][column] - 1

							for i in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
								if row+i[0] >= 0 and column+i[1] >= 0 and column+i[1] < dimension[0]:
									if t_data[row+i[0]][column+i[1]] == b'o' and t_data[row][column] != b'o':
										h_data[row][column] = h_data[row][column] - 1
				t_data = t_data[:-1]
				h_data = h_data[:-1]

			elif rank != p_num:
				# Process in between
				t_data = np.concatenate(([top_row_t], t_data, [bottom_row_t]))
				h_data = np.concatenate(([top_row_h], h_data, [bottom_row_h]))
				for row in range(1, dimension[1]+1):
					for column in range(0, dimension[0]):
						if t_data[row][column] != b'.':
							for i in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
								if column+i[1] >= 0 and column+i[1] < dimension[0]:
									if t_data[row+i[0]][column+i[1]] == b'+' and t_data[row][column] != b'+':
										h_data[row][column] = h_data[row][column] - 2
									elif t_data[row+i[0]][column+i[1]] == b'o' and t_data[row][column] != b'o':
										h_data[row][column] = h_data[row][column] - 1

							for i in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
								if column+i[1] >= 0 and column+i[1] < dimension[0]:
									if t_data[row+i[0]][column+i[1]] == b'o' and t_data[row][column] != b'o':
										h_data[row][column] = h_data[row][column] - 1
				t_data = t_data[1:-1]
				h_data = h_data[1:-1]						

			else:
				# Las process
				t_data = np.concatenate(([top_row_t], t_data))
				h_data = np.concatenate(([top_row_h], h_data))
				for row in range(1, dimension[1]+1):
					for column in range(0, dimension[0]):
						if t_data[row][column] != b'.':
							for i in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
								if row+i[0] < dimension[1]+1 and column+i[1] >= 0 and column+i[1] < dimension[0]:
									if t_data[row+i[0]][column+i[1]] == b'+' and t_data[row][column] != b'+':
										h_data[row][column] = h_data[row][column] - 2
									elif t_data[row+i[0]][column+i[1]] == b'o' and t_data[row][column] != b'o':
										h_data[row][column] = h_data[row][column] - 1

							for i in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
								if row+i[0] < dimension[1]+1 and column+i[1] >= 0 and column+i[1] < dimension[0]:
									if t_data[row+i[0]][column+i[1]] == b'o' and t_data[row][column] != b'o':
										h_data[row][column] = h_data[row][column] - 1
				t_data = t_data[1:]
				h_data = h_data[1:]	

			for r in range(len(h_data)):
				for c in range(len(h_data[0])):
					if h_data[r][c] <= 0:
						h_data[r][c] = 0
						t_data[r][c] = '.'

		comm.Send(t_data, dest=0, tag=31)
		comm.Send(h_data, dest=0, tag=32)

if rank == 0:
	for i in range(board_size):
		res_line = ""
		for j in range(board_size):
			res_line = res_line + game_board_t[i][j].decode()
			if (j!=board_size-1):
				res_line += " "
		if (i!=board_size-1):
			output_file.write(res_line + "\n")
		else:
			output_file.write(res_line)
		res_line = ""

output_file.close()