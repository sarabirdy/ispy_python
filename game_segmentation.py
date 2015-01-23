#!/usr/bin/env python

import numpy as np 
import cv2
import object_retrain as obj
import image_loader as iml
import os

game_images = os.getcwd() + "/HumanGames" #path to images
game_segments = os.getcwd() + "/GAMES2"
if not os.path.exists(game_segments):
	os.makedirs(game_segments)

NoOfGames = os.listdir(game_images)

for game in NoOfGames:
	game_folder = game_segments +'/'+ game
	print game
	captures_per_game = os.listdir(game_images+'/'+game)
	for capture in captures_per_game:
		image = game_images + '/' + game +'/'+ capture
		segments,ID = obj.ObjSeperation(image)
		for segment,objID in zip(segments, ID):
			if not os.path.exists(game_folder):
    				os.makedirs(game_folder)
			if objID > 0:
				filename =  game_folder + '/obj' + objID + '.jpg' 
				cv2.imwrite(filename,segment)
		
