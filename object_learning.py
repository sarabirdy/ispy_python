#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import feature_update2 as feat
import os
import MySQLdb as mdb
import cv2
import db_data_retrieval as train

# access the DB

con = mdb.connect('localhost', 'iSpy_team', 'password', 'iSpy_features');#connect to database
with con:
    cur = con.cursor()


# for all segmented objects insert their feature vectors to the DB


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
	
train.CreateFeatureTable(cur)			
	
	
	


