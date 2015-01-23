#!/usr/bin/env python
import os
import MySQLdb as mdb
import numpy as np 
import random


gameID  = raw_input('Give game ID: ')
game_folder = os.getcwd() + '/GAMES2/Game' + str(gameID)
tags_file = game_folder + '/tags.txt'


f = open(tags_file)
tags_to_ask = f.read().splitlines()


obj_id = []
belief_probs = []
NoOfQuestions = 0

#connect to database
con = mdb.connect('localhost', 'iSpy_team', 'password', 'iSpy_features')
with con:
    cur = con.cursor()

# get object names
cur.execute("SELECT DISTINCT(name) FROM NameInfo;")
obj = cur.fetchall()

# get object ids
cur.execute("SELECT DISTINCT(observation_id) FROM NameInfo;")
objid = cur.fetchall()
obj_ID = np.asarray(objid)
for objID in obj_ID:
	obj_id.append(objID[0])


# define threshold and initial belief probabilities
# the belief probabilities for each object at the beggining of the game are equal 
thresh2 = (1/float(len(obj))) + (float(len(obj)-1)/float(len(obj)*len(obj))) 
N = len(obj)
thresh = (float(2*N - 1))/(1.1*float(N*N)) 

print thresh2, thresh

initial_prob = 1/float(len(obj))  
for item in xrange(0, len(obj)):
	belief_probs.append(initial_prob)

    
belief_probs = np.asarray(belief_probs)

objects=((len(obj)),len(tags_to_ask))
objects=np.zeros(objects)
        
        
for i in xrange(0,len(obj)):            
	for j in xrange(0,len(tags_to_ask)):
               cur.execute("SELECT count(*) FROM TagInfo WHERE observation_id='{1}' and tag='{0}' ".format(str(tags_to_ask[j]),str(obj_id[i])))
               b = cur.fetchall()
               if b[0][0] == 0:
                   continue
               else:
                  objects[i][j]=1
		   

while all(belief_probs < thresh):

	NoOfQuestions = NoOfQuestions + 1;
             
        sums=objects.sum(axis=0)
        tag_ratio=abs(sums/len(obj)-0.5)
        minimum=np.min(tag_ratio)
        itemindexes =[i for i,x in enumerate(tag_ratio) if x==minimum]
        itemindex = random.choice(itemindexes)
  	question_tag=tags_to_ask[itemindex]
	
	print question_tag
        #### find Yes and No scores for all objects
        # first find number of times the tag occurs in the descriptions

        cur.execute("SELECT count(*) FROM TagInfo WHERE tag = '{0}'".format(question_tag))
	T = cur.fetchall()
	tag_counter = T[0][0]
	
	# then find the bigram counts of each object with this tag
	object_scores = []
	for object_name in obj:

		cur_object =  object_name[0][:]

		cur.execute("SELECT observation_id from NameInfo where name = '{0}';".format(str(cur_object)))
		O = cur.fetchall()
		Objid = int(O[0][0])

		bc = cur.execute("SELECT count(*) from TagInfo where observation_id = '{0}' AND tag = '{1}';".format(int(Objid), str(question_tag)))
		B = cur.fetchall()
		bc = int(B[0][0])
		# estimate the scores for each object --> score{object} = #{tag,object}/#{tag}
		object_scores.append(10*float(bc)/float(tag_counter))
	
	percentage_scores = []

        # Now, find the score on each probability 
	for prob, score in zip(belief_probs, object_scores):
		#print prob, score
		p = prob*score
		percentage_scores.append(p)
	
       
	"""
	os.chdir('../')
        NLG.QuestionGeneration(question_tag , '0')
	os.chdir('/home/tsiakas/workspace/ISPY/organised scripts')
	"""

        answer=raw_input('Y(yes) or N(no) & ENTER : ')

        if answer is'yes' or answer is 'y':
            for i in xrange(0,len(obj)):            
            	if objects[i][itemindex] == 0:
                	objects[i][itemindex] = 10
		   	belief_probs[i] = belief_probs[i] - (belief_probs[i]*percentage_scores[i])
	     	if objects[i][itemindex] == 1:
                   	belief_probs[i] = belief_probs[i] + (belief_probs[i]*percentage_scores[i])			
        else :
        	if  answer is'no' or answer is 'n':
             		for i in xrange(0,len(obj)):            
               			if objects[i][itemindex] == 1 :
                   			objects[i][itemindex] = 10
					belief_probs[i] = belief_probs[i] - (belief_probs[i]*percentage_scores[i])
				if objects[i][itemindex] == 0 :
					belief_probs[i] = belief_probs[i] + (belief_probs[i]*percentage_scores[i])


	# normalize the probabilities
	belief_probs = belief_probs / np.sum(belief_probs)
	print belief_probs
        

minimum=np.max(belief_probs)
itemindexes =[i for i,x in enumerate(belief_probs) if x==minimum]
A = np.asarray(obj)
guess = A[itemindexes]
guess2say =  guess[0][0]

print guess2say 

"""
    os.chdir('../')
    NLG.QuestionGeneration(str(guess2say), '1' )
    os.chdir('/home/tsiakas/workspace/ISPY/organised scripts')  
"""

answer=raw_input('Y(yes) or N(no) & ENTER : ')  

if answer is'no':
	result = 'lost'
else:
	result = 'won' 


	

with open("game.txt", "a") as myfile:
    myfile.write("Game No:" + str(gameID) + ". Number of Questions: " + str(NoOfQuestions) + " --" + result  +  "\n")

