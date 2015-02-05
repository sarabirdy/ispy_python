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


def get_t(object_id, question_id, cursor):

    tag = get_tag(question_id, cursor)

    cursor.execute('SELECT COUNT(*) \
                    FROM descriptions \
                    WHERE description like %s \
                    AND oid = %s', ('%{0}%'.format(tag), object_id))

    return cursor.fetchone()[0]


def get_tval(cursor):
    cursor.execute('SELECT yes_answers/total_answers FROM pqd')

    result = cursor.fetchall()

    tvals = []
    for r in result:
        tvals.append(float(r[0]))

    return tvals


def get_questions_answers(object_id, cursor):
    cursor.execute('SELECT qid, oid, answer from answers where oid = %s LIMIT 4200', (object_id))

    results = cursor.fetchall()

    questions_answers = {}
    for i in range(1, 289):
        questions_answers[i] = []

    for qid, oid, answer in results:
        for i in range(1, 289):
            if int(qid) == i:
                questions_answers[i].append(int(answer))

    return questions_answers


def get_tag(question_id, cursor):
    cursor.execute('SELECT tag from tags where qid = %s', (question_id))

    return cursor.fetchone()[0]


def get_t(object_id, question_id, cursor):
    tag = get_tag(question_id, cursor)

    cursor.execute('SELECT COUNT(*) \
                    FROM descriptions \
                    WHERE description like %s \
                    AND oid = %s', ('%{0}%'.format(tag), object_id))

    return cursor.fetchone()[0]


def gen_init_prob(cursor):
    objects = {}

    for i in range(1, 18):
        objects[i] = get_questions_answers(i, cursor)

    return objects


def get_best_question(objects, asked_questions, pO, cursor):
    tvals = get_tval(cursor)
    probabilities = []

    top = (17 - 0 - 1)/2 + 0 + 1
    bottom = 17 - top
    bestDifference = 0
    bestD = 0

    for i in range(0, 17):
        probabilities.append(0)

    for i in range(1, 18):
        for j in range(1, 289):
            if j not in asked_questions:
                T = get_t(i, j, cursor)
                num_yes = sum(objects[i][j])
                length = len(objects[i][j])

                probabilities[i-1] = pO[i-1] * (tvals[T] + (num_yes + 1.0)/(length + 2.0))
                probabilities.sort()
                probabilities.reverse()

                topProb = 0
                bottomProb = 0

                for x in range(0, top):
                    topProb = topProb + probabilities[x]

                for x in range(top, 17):
                    bottomProb = bottomProb + probabilities[x]

                topProb = topProb/(0.0 + top)
                bottomProb = bottomProb/(0.0 + bottom)

                if(abs(topProb - bottomProb) > bestDifference):
                    bestDifference = abs(topProb - bottomProb)
                    bestD = j

    return bestD


def get_subset_split():	    
    question_tag = tags[bestD]
    askedQuestions.append(tags[bestD])
    bestDifference = 0
    
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
    return bestDiff


def ask_question():			
    #tag_to_ask = 'Answer.Q' + str(idx + 1) + 'Obj'+str(OBJECT_WE_PLAY)+'Answer'
    #answer = question.get(tag_to_ask)
    answer = my_data[OBJECT_WE_PLAY-1][bestD]
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
		cursor.execute("SELECT COUNT(*) FROM Descriptions WHERE description like '%" + tags[bestD] + "%' AND objectID = " + str(objectID+1))
		T = cursor.fetchone()[0]
		
		cursor.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND answer=TRUE AND tag='" + tags[bestD] + "'")
		N = cursor.fetchone()[0]
		    
		cursor.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND tag='" + tags[bestD] + "'")
		D = cursor.fetchone()[0]
	    
		belief_probs[objectID] = belief_probs[objectID] * (probabilityD[T] + (N + 1)/(D + 2.0))

    else :
	    if  answer =='no' or answer is 'no':
		    #for i in xrange(0,len(obj)):
			print 'no'
			answers.append(False)
			for objectID in range(0,17):
			    pass
			    cursor.execute("SELECT COUNT(*) FROM Descriptions WHERE description like '%" + tags[bestD] + "%' AND objectID = " + str(objectID+1))
			    T = cursor.fetchone()[0]
					
			    cursor.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND answer=FALSE AND tag='" + tags[bestD] + "'")
			    N = cursor.fetchone()[0]
				
			    cursor.execute("SELECT COUNT(*) FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND tag='" + tags[bestD] + "'")
			    D = cursor.fetchone()[0]
			    
			    belief_probs[objectID] = belief_probs[objectID] * ((1 - probabilityD[T]) + (N + 1)/(D + 2.0))
				    
    # normalize the probabilities
    belief_probs = belief_probs / np.sum(belief_probs)
    
    with open("example.txt", "a") as myfile:
	    myfile.write(question_tag + " -> " + answer + "\n")
	    myfile.write(str(belief_probs) + "\n")
	
    split = bestDiff

def train_initial_model(game_id):
    start_time = time.time()	

    if game_id == 1:
    	for x in xrange(1,18):
    		desc_index = 6 * (x - 1)
    		os.system(" /usr/lib/jvm/java-7-oracle/bin/java -Djava.library.path=/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib -Dfile.encoding=UTF-8 -classpath /local2/awh0047/iSpy/ISPY/iSpy/ispy/bin:/local2/awh0047/iSpy/simplenlg-v4.4.2.jar:/local2/awh0047/iSpy/jaws-bin.jar:/local2/awh0047/iSpy/lucene-analyzers-common-4.6.0.jar:/local2/awh0047/iSpy/lucene-core-4.6.0.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1.jar:/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib/jnaoqi-1.14.5.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1-models.jar:/local2/awh0047/iSpy/mysql-connector-java-5.1.30-bin.jar ObjectDescription " + str(x) + " \"" + objectlist[x-1][0] + "\" \"" + descriptions_for_retraining[desc_index] + "\"") 
    	first.Object_Learning(1, con)
    	print "Initial learning complete"
    	extract.Extract_Tags(1)
    
    elif game_id < 7:
    	for x in xrange(1,18):
    		desc_index = 6 * (x - 1) + game_id - 1
    		os.system(" /usr/lib/jvm/java-7-oracle/bin/java -Djava.library.path=/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib -Dfile.encoding=UTF-8 -classpath /local2/awh0047/iSpy/ISPY/iSpy/ispy/bin:/local2/awh0047/iSpy/simplenlg-v4.4.2.jar:/local2/awh0047/iSpy/jaws-bin.jar:/local2/awh0047/iSpy/lucene-analyzers-common-4.6.0.jar:/local2/awh0047/iSpy/lucene-core-4.6.0.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1.jar:/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib/jnaoqi-1.14.5.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1-models.jar:/local2/awh0047/iSpy/mysql-connector-java-5.1.30-bin.jar ObjectDescription " + str(x) + " \"" + objectlist[x-1][0] + "\" \"" + descriptions_for_retraining[desc_index] + "\"")	
    	retrain.Model_Retrain(game_id, con)
    	print "Learning for game " + str(game_id) + " complete"
    	extract.Extract_Tags(game_id)
    	
    else:
    	csv_answers = np.genfromtxt(folder+'/Answers/Game'+str(game_id-1)+'.csv',dtype=str, delimiter='\t')
    	for x in xrange(1,18):
    		tag_built_description = ""
    		for i in xrange(0, len(tags)):
    			if csv_answers[x-1][i] == 'yes' or csv_answers[x-1][i] is 'yes':
    				tag_built_description = tag_built_description + tags[i] + " "
    		os.system(" /usr/lib/jvm/java-7-oracle/bin/java -Djava.library.path=/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib -Dfile.encoding=UTF-8 -classpath /local2/awh0047/iSpy/ISPY/iSpy/ispy/bin:/local2/awh0047/iSpy/simplenlg-v4.4.2.jar:/local2/awh0047/iSpy/jaws-bin.jar:/local2/awh0047/iSpy/lucene-analyzers-common-4.6.0.jar:/local2/awh0047/iSpy/lucene-core-4.6.0.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1.jar:/local2/awh0047/iSpy/jnaoqi-1.14.5-linux64/lib/jnaoqi-1.14.5.jar:/local2/awh0047/iSpy/stanford-corenlp-full-2014-08-27/stanford-corenlp-3.4.1-models.jar:/local2/awh0047/iSpy/mysql-connector-java-5.1.30-bin.jar ObjectDescription " + str(x) + " \"" + objectlist[x-1][0] + "\" \"" + tag_built_description + "\"")
    	retrain.Model_Retrain(game_id, con)
    	print "Learning for game " + str(game_id) + " complete"
    	extract.Extract_Tags(game_id)
	    
    training_time = time.time() - start_time
    
    return training_time


def clear_tag_data():
    cursor.execute("DELETE FROM TagInfo;")
    cursor.execute("ALTER TABLE TagInfo AUTO_INCREMENT = 1;")


def build_object_list(cursor):
    objectlist = []
    
    cursor.execute("SELECT DISTINCT(name) FROM NameInfo;")
    obj = cursor.fetchall()
    
    OBJ = np.asarray(obj)
    for OB in OBJ:
	    objectlist.append(OB)
	    
    return objectlist


def get_object_ids(cursor):
    obj_id = []

    cursor.execute("SELECT DISTINCT(observation_id) \
		   FROM NameInfo;")
    objid = cursor.fetchall()
    
    obj_ID = np.asarray(objid)
    for objID in obj_ID:
	    obj_id.append(objID[0])

    return obj_id


def get_tags(cursor):
    cursor.execute("SELECT tag \
		   FROM Tags")
    tags = cursor.fetchall()
    
    return tags


def get_descriptions(oid, cursor):
    cursor.execute("SELECT description \
		   FROM Descriptions \
		   WHERE objectID = %s", (oid))
    descriptions = cursor.fetchall()
    
    return descriptions


def record_round_results(cursor):
    with open("game.txt", "a") as myfile:
      myfile.write(str(gameID)+','+ str(OBJECT_WE_PLAY) +','+ str(objectlist.index(guess2say))+"," + str(NoOfQuestions) + "," + result  +  "\n")
      
    for question in range(0, len(asked)):
	cursor.execute("INSERT into QuestionAnswers (object, tag, answer) VALUES (" + str(OBJECT_WE_PLAY) + ", '" + asked[question] + "', " + str(answers[question]) + ")")

    con.commit()
    
    with open("game.txt", "a") as myfile:
	myfile.write("Round " + str(gameID) + ": ")	  
	myfile.write("Wins=" + str(round_wins) + ', Losses='+str(round_losses))
	myfile.write(" Accuracy: " + str(round_wins/float(17)) + "\n")
	myfile.write("Training time: " + str(training_time) + " second\n")   


def guess_object():
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


def play_object():
    my_data = np.genfromtxt(folder+'/Answers/Game'+str(gameID)+'.csv',dtype=str, delimiter='\t')
    NoOfQuestions = 0
    belief_probs = []
    game_folder = all_games + '/Game' + str(gameID)
    
    print "+++++++++++++++" + game_folder + "+++++++++++++++"
    
    tags_file = game_folder + '/tags.txt'
    f = open(tags_file) 
    tags_to_ask = f.read().splitlines()

    initial_prob = 1/float(len(obj))  
    for item in xrange(0, len(obj)):
	    belief_probs.append(initial_prob)			
	    
    belief_probs = np.asarray(belief_probs)	
	    
    probabilityD = get_tval(cursor)

    askedQuestions = []
    answers = []
    split = 0
    answer_data = np.genfromtxt('/local2/awh0047/iSpy/ISPY_PY/Answers/Game' + str(gameID) + '.csv',dtype=str, delimiter='\t')

    while np.sort(belief_probs)[belief_probs.size - 1] - np.sort(belief_probs)[belief_probs.size - 2] < 0.1:
	pass

    print result 


def play_round():
    NoOfQuestions = 0
    
    round_wins = 0
    round_losses = 0
    for OBJECT_WE_PLAY in obj_id:
	pass
    

def play_game():
    wins=0
    losses=0

    for gameID in range(1,31):
	pass
    
    with open("game.txt", "a") as myfile:
	myfile.write("Wins=" + str(wins) + ', Losses='+str(losses))


def main():
    con = mdb.connect('localhost', 'iSpy_team', 'password', 'iSpy_features')
    with con:
	cursor = con.cursor()
    
    folder =  os.getcwd()
    all_games = folder + '/Human_Games'
    
    tags = get_tags(cursor)
  
		      
if __name__ == '__main__':
        sys.exit(main())
	