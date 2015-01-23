#!/usr/bin/python
import os
import test_model 
import cv2
import test_features_extraction as test_ft
import numpy as np

filename = os.getcwd() + '/model_evaluation.txt' 
f = open(filename, "w")


pepper = os.getcwd() + "/GAMES/Game1/obj14.jpg"
apple  = os.getcwd() + "/GAMES/Game1/obj9.jpg"
analog = os.getcwd() + "/GAMES/Game1/obj2.jpg"

model1 =  "GMM_model_1"
model2 =  "GMM_model_7"
model3 =  "GMM_model_14"

###############  PEPPER ########################
img = cv2.imread(pepper)
feature_vector = test_ft.FeatureExtraction(img)
tags_pepper1 = test_model.test(feature_vector, model1)
print 'pepper'
f.write('pepper\n_______\n')
f.write('MODEL_1\n')
for tag in tags_pepper1:
	T = tag.split('_', 1)[0]
	#tags_per_game.append(T)
	f.write(T + '\n')

tags_pepper2 = test_model.test(feature_vector, model2)
f.write('MODEL_7\n')
for tag in tags_pepper2:
	T = tag.split('_', 1)[0]
	#tags_per_game.append(T)
	f.write(T + '\n')

tags_pepper3 = test_model.test(feature_vector, model3)
f.write('MODEL_14\n')
for tag in tags_pepper3:
	T = tag.split('_', 1)[0]
	#tags_per_game.append(T)
	f.write(T + '\n')

###############  APPLE ########################
print 'apple'
f.write('apple\n_______\n')
img = cv2.imread(apple)
feature_vector = test_ft.FeatureExtraction(img)
tags_apple1 = test_model.test(feature_vector, model1)
f.write('MODEL_1\n')
for tag in tags_apple1:
	T = tag.split('_', 1)[0]
	#tags_per_game.append(T)
	f.write(T + '\n')

tags_apple2 = test_model.test(feature_vector, model2)
f.write('MODEL_7\n')
for tag in tags_apple2:
	T = tag.split('_', 1)[0]
	#tags_per_game.append(T)
	f.write(T + '\n')

tags_apple3 = test_model.test(feature_vector, model3)
f.write('MODEL_14\n')
for tag in tags_apple3:
	T = tag.split('_', 1)[0]
	#tags_per_game.append(T)
	f.write(T + '\n')

###############  ANALOG CLOCK ########################

print 'analog clock'
f.write('analog clock\n__________\n')
img = cv2.imread(analog)
feature_vector = test_ft.FeatureExtraction(img)
tags_analog1 = test_model.test(feature_vector, model1)
f.write('MODEL_1\n')
for tag in tags_analog1:
	T = tag.split('_', 1)[0]
	#tags_per_game.append(T)
	f.write(T + '\n')

tags_analog2 = test_model.test(feature_vector, model2)
f.write('MODEL_7\n')
for tag in tags_analog2:
	T = tag.split('_', 1)[0]
	#tags_per_game.append(T)
	f.write(T + '\n')

tags_analog3 = test_model.test(feature_vector, model3)
f.write('MODEL_14\n')
for tag in tags_analog3:
	T = tag.split('_', 1)[0]
	#tags_per_game.append(T)
	f.write(T + '\n')


f.close()


