#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import feature_update2 as feat
import os
import MySQLdb as mdb
import cv2
import db_data_retrieval as train

# access the DB

def Object_Learning(game_num, con):

	with con:
	    cur = con.cursor()

	# for all segmented objects insert their feature vectors to the DB

	if game_num == 1:
		folder = os.getcwd()+"/cropped_ims"
		NoOfObjects = len(os.listdir(folder))

		for x in range(1,NoOfObjects+1):
			#print x
			objID = x
			# for each object folder, load all images
			current_folder = folder + "/obj" + str(objID)
			captures =  os.listdir(current_folder)
			for image in captures:
				image_path = current_folder + "/" + image
				img = cv2.imread(image_path)
				feat.FeatureUpdate(con,img,str(objID))
		con.commit()
	else:
		folder = os.getcwd()+"/GAMES/Game" + str(game_num-1)

		captures =  os.listdir(folder)
		for image in captures:
			if image.endswith('.jpg'):
				objID = image[3:5]
				img = cv2.imread(image)
				feat.FeatureUpdate(con,img,objID)
		con.commit()
		
	
	train.CreateFeatureTable(cur,game_num)			
	
