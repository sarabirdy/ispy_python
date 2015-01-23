#!/usr/bin/python

import os
import csv
import numpy as np 

losses = [];
wins = [];
total= []
filename = os.getcwd() + '/game_average_questions.csv' 
with open(filename, 'rb') as csvfile:
    		reader = csv.reader(csvfile,delimiter = '\t')
    		for rows in reader:
			total.append(int(rows[0]))
			if rows[1] is 'lost' or rows[1] == 'lost':
				losses.append(int(rows[0]))
			if rows[1] is 'won' or rows[1] == 'won':
				wins.append(int(rows[0]))
			

	
W = np.asarray(wins)
print W.mean()		

L = np.asarray(losses)
print L.mean()	

T = np.asarray(total)
print T.mean()	
