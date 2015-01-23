#!/usr/bin/python

import os
import time
import csv
import MySQLdb as mdb
import numpy as np 
import random
import sys
import model_retraining_for_game as retrain
import object_learning_for_game as first
import extract_tags_per_game as extract

folder =  os.getcwd()
all_games = folder + '/Human_Games'
game_folders_idx = range(1,31) 

obj_id = []
objectlist = []

wins=0
losses=0

tags = []
tags_ids = folder + "/Answers/tagID"
with open(tags_ids) as f:
    for line in f:
        tags.append(line.strip())

#connect to databaseadd
con = mdb.connect('localhost', 'iSpy_team', 'password', 'iSpy_features')
with con:
    cur = con.cursor()

# get object names
cur.execute("SELECT DISTINCT(name) FROM NameInfo;")
obj = cur.fetchall()

OBJ = np.asarray(obj)
for OB in OBJ:
	objectlist.append(OB)

# clean out tags
cur.execute("DELETE FROM TagInfo;")
cur.execute("ALTER TABLE TagInfo AUTO_INCREMENT = 1;")

# get object ids
cur.execute("SELECT DISTINCT(observation_id) FROM NameInfo;")
objid = cur.fetchall()
obj_ID = np.asarray(objid)
for objID in obj_ID:
	obj_id.append(objID[0])

descriptions_file = folder + "/item_desc/descriptionsForTagging.txt"
f = open(descriptions_file)
descriptions_for_retraining = f.read().splitlines()

for gameID in game_folders_idx:
##########for OBJECT_WE_PLAY in obj_id:
#Play games in order

	start_time = time.time()	

	#if gameID == 1:
	#	for x in xrange(1,18):
	#		desc_index = 6 * (x - 1)
	#		os.system(" /usr/lib/jvm/java-7-oracle/bin/java -Djava.library.path=/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib -Dfile.encoding=UTF-8 -classpath /local2/awh0047/iSpy/ISPY/iSpy/ispy/bin:/local2/awh0047/iSpy/simplenlg-v4.4.2.jar:/local2/awh0047/iSpy/jaws-bin.jar:/local2/awh0047/iSpy/lucene-analyzers-common-4.6.0.jar:/local2/awh0047/iSpy/lucene-core-4.6.0.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1.jar:/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib/jnaoqi-1.14.5.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1-models.jar:/local2/awh0047/iSpy/mysql-connector-java-5.1.30-bin.jar ObjectDescription " + str(x) + " \"" + objectlist[x-1][0] + "\" \"" + descriptions_for_retraining[desc_index] + "\"") 
	#	first.Object_Learning(1, con)
	#	print "Initial learning complete"
	#	extract.Extract_Tags(1)
	#
	#elif gameID < 7:
	#	for x in xrange(1,18):
	#		desc_index = 6 * (x - 1) + gameID - 1
	#		os.system(" /usr/lib/jvm/java-7-oracle/bin/java -Djava.library.path=/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib -Dfile.encoding=UTF-8 -classpath /local2/awh0047/iSpy/ISPY/iSpy/ispy/bin:/local2/awh0047/iSpy/simplenlg-v4.4.2.jar:/local2/awh0047/iSpy/jaws-bin.jar:/local2/awh0047/iSpy/lucene-analyzers-common-4.6.0.jar:/local2/awh0047/iSpy/lucene-core-4.6.0.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1.jar:/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib/jnaoqi-1.14.5.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1-models.jar:/local2/awh0047/iSpy/mysql-connector-java-5.1.30-bin.jar ObjectDescription " + str(x) + " \"" + objectlist[x-1][0] + "\" \"" + descriptions_for_retraining[desc_index] + "\"")	
	#	retrain.Model_Retrain(gameID, con)
	#	print "Learning for game " + str(gameID) + " complete"
	#	extract.Extract_Tags(gameID)
	#	
	#else:
	#	csv_answers = np.genfromtxt(folder+'/Answers/Game'+str(gameID-1)+'.csv',dtype=str, delimiter='\t')
	#	for x in xrange(1,18):
	#		tag_built_description = ""
	#		for i in xrange(0, len(tags)):
	#			if csv_answers[x-1][i] == 'yes' or csv_answers[x-1][i] is 'yes':
	#				tag_built_description = tag_built_description + tags[i] + " "
	#		os.system(" /usr/lib/jvm/java-7-oracle/bin/java -Djava.library.path=/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib -Dfile.encoding=UTF-8 -classpath /local2/awh0047/iSpy/ISPY/iSpy/ispy/bin:/local2/awh0047/iSpy/simplenlg-v4.4.2.jar:/local2/awh0047/iSpy/jaws-bin.jar:/local2/awh0047/iSpy/lucene-analyzers-common-4.6.0.jar:/local2/awh0047/iSpy/lucene-core-4.6.0.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1.jar:/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib/jnaoqi-1.14.5.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1-models.jar:/local2/awh0047/iSpy/mysql-connector-java-5.1.30-bin.jar ObjectDescription " + str(x) + " \"" + objectlist[x-1][0] + "\" \"" + tag_built_description + "\"")
	#	retrain.Model_Retrain(gameID, con)
	#	print "Learning for game " + str(gameID) + " complete"
	#	extract.Extract_Tags(gameID)
		
	training_time = time.time() - start_time
	
        NoOfQuestions = 0
	# for each object we run all the games as it is the object that user has in mind
	# find the corresponding answer file
	
	round_wins = 0
	round_losses = 0
	for OBJECT_WE_PLAY in obj_id:
	#Play a game with each object in the round
	#for gameID in game_folders_idx:
                
                my_data = np.genfromtxt(folder+'/Answers/Game'+str(gameID)+'.csv',dtype=str, delimiter='\t')
		NoOfQuestions = 0
		belief_probs = []
		game_folder = all_games + '/Game' + str(gameID)
		
		print "+++++++++++++++" + game_folder + "+++++++++++++++"
		
		tags_file = game_folder + '/tags.txt'
		f = open(tags_file) 
		tags_to_ask = f.read().splitlines()
		#print tags_to_ask				
#
#	REPLACE BELOW
#		
		# define initial belief probabilities
		# the belief probabilities for each object at the beggining of the game are equal 

		initial_prob = 1/float(len(obj))  
		for item in xrange(0, len(obj)):
			belief_probs.append(initial_prob)			
			
		belief_probs = np.asarray(belief_probs)	
#
#	REPLACE ABOVE
#
	        probabilityD = [0,0,0,0,0,0,0]
		denominator = [0,0,0,0,0,0,0]
		        
		for objectID in range(1,18):
		    print objectID
		    for tag in range(0, 289):
		        cur.execute("SELECT * FROM Descriptions WHERE description like '%" + tags[tag] + "%' AND objectID = " + str(objectID))
		        T = len(cur.fetchall())
		    
		        cur.execute("SELECT * FROM QuestionAnswers WHERE tag = '" + tags[tag] + "' AND object = " + str(objectID) + " AND answer = TRUE")
		        count = len(cur.fetchall())
		        
		        probabilityD[T] = probabilityD[T] + count
		        denominator[T] = denominator[T] + 15
		
		for freq in range(0,7):
		    probabilityD[freq] = probabilityD[freq]/(0.0 + denominator[freq])
		    print probabilityD[freq]
		
		askedQuestions = []
		answers = []
		split = 0
		answer_data = np.genfromtxt('/local2/awh0047/iSpy/ISPY_PY/Answers/Game' + str(gameID) + '.csv',dtype=str, delimiter='\t')

		while np.sort(belief_probs)[belief_probs.size - 1] - np.sort(belief_probs)[belief_probs.size - 2] < 0.05:

			NoOfQuestions = NoOfQuestions + 1;            	     
#
#	REPLACE BELOW
#
			Pd = 0.0
			bestD = 0
			
			probabilities = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			bestDifference = 0
			questionNum = 0
			
		        top = (17 - split - 1)/2 + split + 1
			bottom = 17 - top
			
			for tag in range(0,len(tags)):
			    if tags[tag] not in askedQuestions:
				for objectID in range(1,18):
				    
				    #print str(objectID) + " " + tags[tag]
				    cur.execute("SELECT COUNT(*) as count FROM Descriptions WHERE description like '%" + tags[tag] + "%' AND objectID = " + str(objectID))                
				    T = cur.fetchone()[0]
				    #print str(T) + " T"
				    cur.execute("SELECT COUNT(*) as count FROM QuestionAnswers WHERE object=%s AND tag=%s AND answer=1", (objectID, tags[tag]))
				    N = cur.fetchone()[0]
				    #print str(N) + " N"
				    cur.execute("SELECT COUNT(*) as count FROM QuestionAnswers WHERE object=%s AND tag=%s", (objectID, tags[tag]))
				    D = cur.fetchone()[0]
				    #print str(D) + " D"
				    probabilities[objectID-1] = belief_probs[objectID-1] * (probabilityD[T] + (N + 1)/(D + 2.0))
				    
				    probabilities.sort()
				    probabilities.reverse()
				
				    topProb = 0.0
				    bottomProb = 0.0
				    
				    for x in range(split,top):
					topProb = topProb + probabilities[x]
					
				    for x in range(top, 17):
					bottomProb = bottomProb + probabilities[x]
					
				    topProb = topProb/(0.0 + top)
				    bottomProb = bottomProb/(0.0 + bottom)
				    
				    if(abs(topProb - bottomProb) > bestDifference):
					bestDifference = abs(topProb - bottomProb)
					bestProbabilities = list(probabilities)
					bestD = tag
			    else:
				pass
				
			print str(bestDifference) + " -> " + tags[bestD]
			question_tag = tags[bestD]
			askedQuestions.append(tags[bestD])
			bestDifference = 0
			
			print 'Is it ' + tags[bestD] + '? (yes/no) '
			answer = answer_data[OBJECT_WE_PLAY][bestD]
			print bestD
			
			#if answer == 'yes':
			#    print 'yes'
			#    answers.append(True)
			#    for objectID in range(0,17):
			#	pass
			#	cur.execute("SELECT COUNT(*) FROM Descriptions WHERE description like '%" + tags[bestD] + "%' AND objectID = " + str(objectID+1))
			#	T = cur.fetchone()[0]
			#	
			#	cur.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND answer=TRUE AND tag='" + tags[bestD] + "'")
			#	N = cur.fetchone()[0]
			#	    
			#	cur.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND tag='" + tags[bestD] + "'")
			#	D = cur.fetchone()[0]
			#    
			#	belief_probs[objectID] = belief_probs[objectID] * (probabilityD[T] + (N + 1)/(D + 2.0))
			#else:
			#    print 'no'
			#    answers.append(False)
			#    for objectID in range(0,17):
			#	pass
			#	cur.execute("SELECT COUNT(*) FROM Descriptions WHERE description like '%" + tags[bestD] + "%' AND objectID = " + str(objectID+1))
			#	T = cur.fetchone()[0]
			#		    
			#	cur.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND answer=FALSE AND tag='" + tags[bestD] + "'")
			#	N = cur.fetchone()[0]
			#	    
			#	cur.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND tag='" + tags[bestD] + "'")
			#	D = cur.fetchone()[0]
			#	
			#	belief_probs[objectID] = belief_probs[objectID] * ((1 - probabilityD[T]) + (N + 1)/(D + 2.0))
			#    
			#belief_probs = belief_probs/sum(belief_probs)
			
			belief_probs_sorted = np.sort(belief_probs)
			belief_probs_args_sorted = np.argsort(belief_probs)
			
			for x in range(0,17):
			    print str(belief_probs_args_sorted[x]) + " -> " + str(belief_probs_sorted[x])
			    
			diff = 0
			bestDiff = 0
			
			for x in range(0, belief_probs_sorted.size-1):
			    if belief_probs_sorted[x+1] - belief_probs_sorted[x] > diff:
				diff = belief_probs_sorted[x+1] - belief_probs_sorted[x]
				bestDiff = x
			print diff
			print bestDiff
#
#	REPLACE ABOVE
#				
			idx = tags.index(question_tag)
			#tag_to_ask = 'Answer.Q' + str(idx + 1) + 'Obj'+str(OBJECT_WE_PLAY)+'Answer'
			#answer = question.get(tag_to_ask)
			answer = my_data[OBJECT_WE_PLAY-1][idx]
			print game_folder, OBJECT_WE_PLAY,objectlist[OBJECT_WE_PLAY-1][0],'qt->'+question_tag+' ' ,'ans->'+answer 
			if not (answer):
				#answer = 'yes'
			
				#objects[OBJECT_WE_PLAY-1][itemindex] = 10
			        #NoOfQuestions = NoOfQuestions - 1;
				print game_folder, OBJECT_WE_PLAY,'qt->'+question_tag+' ' ,'sd'+answer+'<-', objectlist[OBJECT_WE_PLAY-1][0]
				continue		
				
				sys.exit()
				
			#print question_tag , answer , tag_to_ask
        		if answer == 'yes' or answer is 'yes':
            			#for i in xrange(0,len(obj)):
				print 'yes'
				answers.append(True)
				for objectID in range(0,17):
				    pass
				    cur.execute("SELECT COUNT(*) FROM Descriptions WHERE description like '%" + tags[bestD] + "%' AND objectID = " + str(objectID+1))
				    T = cur.fetchone()[0]
				    
				    cur.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND answer=TRUE AND tag='" + tags[bestD] + "'")
				    N = cur.fetchone()[0]
					
				    cur.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND tag='" + tags[bestD] + "'")
				    D = cur.fetchone()[0]
				
				    belief_probs[objectID] = belief_probs[objectID] * (probabilityD[T] + (N + 1)/(D + 2.0))
		
        		else :
        			if  answer =='no' or answer is 'no':
             				#for i in xrange(0,len(obj)):
					    print 'no'
					    answers.append(False)
					    for objectID in range(0,17):
						pass
						cur.execute("SELECT COUNT(*) FROM Descriptions WHERE description like '%" + tags[bestD] + "%' AND objectID = " + str(objectID+1))
						T = cur.fetchone()[0]
							    
						cur.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND answer=FALSE AND tag='" + tags[bestD] + "'")
						N = cur.fetchone()[0]
						    
						cur.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND tag='" + tags[bestD] + "'")
						D = cur.fetchone()[0]
						
						belief_probs[objectID] = belief_probs[objectID] * ((1 - probabilityD[T]) + (N + 1)/(D + 2.0))
							
			# normalize the probabilities
			belief_probs = belief_probs / np.sum(belief_probs)
			#print belief_probs
			
			with open("example.txt", "a") as myfile:
				myfile.write(question_tag + " -> " + answer + "\n")
				myfile.write(str(belief_probs) + "\n")
							
			split = bestDiff
	  			
		minimum=np.max(belief_probs)
		itemindexes =[i for i,x in enumerate(belief_probs) if x==minimum]
		A = np.asarray(obj)
		guess = A[itemindexes]
		guess2say =  guess[0][0]

		print guess2say
		print objectlist[OBJECT_WE_PLAY-1][0]
		if objectlist[OBJECT_WE_PLAY-1][0] == guess2say:
			result = 'won'
                        wins=wins+1
			round_wins=round_wins + 1
		else:
			result = 'lost'
			losses=losses+1
			round_losses=round_losses + 1
		
		print result 

		with open("game.txt", "a") as myfile:
		  myfile.write(str(gameID)+','+ str(OBJECT_WE_PLAY) +','+ str(objectlist.index(guess2say))+"," + str(NoOfQuestions) + "," + result  +  "\n")
		  
		for question in range(0, len(asked)):
		    cur.execute("INSERT into QuestionAnswers (object, tag, answer) VALUES (" + str(OBJECT_WE_PLAY) + ", '" + asked[question] + "', " + str(answers[question]) + ")")
        
		con.commit() 

	with open("game.txt", "a") as myfile:
		myfile.write("Round " + str(gameID) + ": ")	  
	  	myfile.write("Wins=" + str(round_wins) + ', Losses='+str(round_losses))
		myfile.write(" Accuracy: " + str(round_wins/float(17)) + "\n")
		myfile.write("Training time: " + str(training_time) + " second\n")

with open("game.txt", "a") as myfile:
  		  myfile.write("Wins=" + str(wins) + ', Losses='+str(losses))