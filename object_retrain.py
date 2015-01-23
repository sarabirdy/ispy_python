#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This function processes a capture and seperates the objects which appear in it. 
Afterwards it saves the images in a list .

20/6/2014
IRSS 2014 @ NCSR DEMOKRITOS
AUTHORS: Kostas Tsiakas/Papakostas Michalis

'''


import numpy as np
import cv2
from matplotlib import pyplot as plt

def  ObjSeperation(image_path):
 img = cv2.imread(image_path) #load image

 ######## SEGMENTATION ############
 gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
 ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
 fg = cv2.erode(thresh,None,iterations = 2)

 bgt = cv2.dilate(thresh,None,iterations = 3)
 ret,bg = cv2.threshold(bgt,1,128,1)

 marker = cv2.add(fg,bg)

 marker32 = np.int32(marker)

 cv2.watershed(img,marker32)
 m = cv2.convertScaleAbs(marker32)
 ret,thresh = cv2.threshold(m,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
 res = cv2.bitwise_and(img,img,mask = thresh)
 thresh2=thresh.copy()


 ######## CONTOURS ############
 contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)#find the contours




 #####################    SEPERATING OBJECTS FROM IMAGE & SAVING THEM TO NEW IMAGES #######################
 i=1
 captures=[]	#list to save the objects (crroped images) which appear in one capture
 IDs = []
 #print len(contours)
 for cnt in contours: #for each contour

 	#_________ RECTANGLE INCLUDING AN OBJECT ______
 
	x,y,w,h = cv2.boundingRect(cnt)#draw a rectangle around each object
   	crop_img = img[y: y + h, x: x + w] #new image containing only one object 


   	if len(crop_img)>200 or len(crop_img[0][:])>200 : # ignore trash images   (threshold of allowed pixel range deppends on the camera)
   		continue;
  


   	cv2.imshow("window title30", crop_img)
   	cv2.waitKey(1000)
   	cv2.destroyWindow("window title30")
   	ID = raw_input('Object ID (press 0 for trash):  ')

   	if ID is'0':
    		continue
   	else:
        	captures.append(crop_img)
		IDs.append(ID)

 return captures, IDs




