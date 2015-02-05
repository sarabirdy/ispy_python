import MySQLdb as mdb
import numpy as np
import gc

def prob_by_tag_frequency():
    #con = mdb.connect('localhost', 'iSpy_team', 'password', 'iSpy_features')
    #with con:
    #    cur = con.cursor()
    #
    #f = open('/local2/awh0047/iSpy/ISPY_PY/Answers/tagID')
    #tags = f.read().splitlines()
    #f.close()
    #
    #probabilityD = [0,0,0,0,0,0,0]
    #denominator = [0,0,0,0,0,0,0]
    #        
    #for objectID in range(1,18):
    #    print objectID
    #    for tag in range(0, 289):
    #        cur.execute("SELECT * FROM Descriptions WHERE description like '%" + tags[tag] + "%' AND objectID = " + str(objectID))
    #        T = len(cur.fetchall())
    #    
    #        cur.execute("SELECT * FROM Answers WHERE tag = '" + tags[tag] + "' AND objectID = " + str(objectID) + " AND answer = TRUE AND answerSet BETWEEN 1 AND 15")
    #        count = len(cur.fetchall())
    #        
    #        probabilityD[T] = probabilityD[T] + count
    #        denominator[T] = denominator[T] + 15
    #
    #for freq in range(0,7):
    #    probabilityD[freq] = probabilityD[freq]/(0.0 + denominator[freq])
    #    print probabilityD[freq]
    #return probabilityD
    
    
    con = mdb.connect('localhost', 'iSpy_team', 'password', 'iSpy_features')
    with con:
        cur = con.cursor()
    
    f = open('/local2/awh0047/iSpy/ISPY_PY/Answers/tagID')
    tags = f.read().splitlines()
    f.close()
    
    cur.execute("SELECT * FROM Questions")
    results = cur.fetchall()
    
    qid = 1
    for result in results:
        cur.execute("INSERT INTO questions (qid, question) VALUES (%s, %s)", (qid, result[0]))
        con.commit()
        qid = qid + 1
    
    
    #probabilityD = [0,0,0,0,0,0,0]
    #denominator = [0,0,0,0,0,0,0]
    #        
    #for objectID in range(1,18):
    #    print objectID
    #    for tag in range(0, 289):
    #        cur.execute("SELECT * FROM Descriptions WHERE description like '%" + tags[tag] + "%' AND objectID = " + str(objectID))
    #        T = len(cur.fetchall())
    #    
    #        cur.execute("SELECT * FROM QuestionAnswers WHERE tag = '" + tags[tag] + "' AND object = " + str(objectID) + " AND answer = TRUE")
    #        count = len(cur.fetchall())
    #        
    #        cur.execute("SELECT * FROM QuestionAnswers WHERE tag = '" + tags[tag] + "' AND object = " + str(objectID))
    #        D = len(cur.fetchall())            
    #        
    #        probabilityD[T] = probabilityD[T] + count
    #        denominator[T] = denominator[T] + D
    #
    #for freq in range(0,7):
    #    #probabilityD[freq] = probabilityD[freq]/(0.0 + denominator[freq])
    #    cur.execute("INSERT INTO Pqd (t_value, yes_answers, total_answers) VALUES (%s, %s, %s)", (freq, probabilityD[freq], denominator[freq]))
    #    con.commit()
    #    print probabilityD[freq]
    #return probabilityD
    
    return [0.22,0.509219858156,0.594202898551,0.584615384615,0.681481481481,0.663157894737,0.813333333333]

def decide_to_guess(pO):
    pO_sorted = np.sort(pO)
    
    if pO_sorted[pO_sorted.size - 1] - pO_sorted[pO_sorted.size - 2] >= 0.05:
        return True
    else:
        return False
    
def log_tag_answers(asked, answers, object_id):
    con = mdb.connect('localhost', 'iSpy_team', 'password', 'iSpy_features')
    with con:
        cur = con.cursor()
        
    for question in range(0, len(asked)):
        cur.execute("INSERT into QuestionAnswers (object, tag, answer) VALUES (" + str(object_id) + ", '" + asked[question] + "', " + str(answers[question]) + ")")
        
    con.commit()    
    con.close()

def best_tag(askedQuestions, answers, pO, start, probabilityD, object_id):
    con = mdb.connect('localhost', 'iSpy_team', 'password', 'iSpy_features')
    with con:
        cur = con.cursor()
    
    f = open('/local2/awh0047/iSpy/ISPY_PY/Answers/tagID')
    tags = f.read().splitlines()
    f.close()
        
    Pd = 0.0
    bestD = 0
    
    probabilities = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    bestDifference = 0
    questionNum = 0
        
    top = (17 - start - 1)/2 + start + 1
    bottom = 17 - top
    
    zero = 0
    not_asked = 0
    
    for tag in range(0,len(tags)):
        print tag
        if tags[tag] not in askedQuestions:
            for objectID in range(1,18):
                
                #print str(objectID) + " " + tags[tag]
                cur.execute("SELECT COUNT(*) as count FROM Descriptions WHERE description like '%" + tags[tag] + "%' AND objectID = " + str(objectID))                
                T = cur.fetchone()[0]
                #print str(T) + " T"
                cur.execute("SELECT COUNT(*) as count FROM Answers WHERE objectID=%s AND tag=%s AND answer=1", (objectID, tags[tag]))
                N = cur.fetchone()[0]
                #print str(N) + " N"
                cur.execute("SELECT COUNT(*) as count FROM Answers WHERE objectID=%s AND tag=%s", (objectID, tags[tag]))
                D = cur.fetchone()[0]
                #print str(D) + " D"
                probabilities[objectID-1] = pO[objectID-1] * (probabilityD[T] + (N + 1)/(D + 2.0))
                
                probabilities.sort()
                probabilities.reverse()
            
                topProb = 0.0
                bottomProb = 0.0
                
                for x in range(start,top):
                    topProb = topProb + probabilities[x]
                    
                for x in range(top, 17):
                    bottomProb = bottomProb + probabilities[x]
                    
                topProb = topProb/(0.0 + top)
                bottomProb = bottomProb/(0.0 + bottom)
                
                if(abs(topProb - bottomProb) > bestDifference):
                    bestDifference = abs(topProb - bottomProb)
                    bestProbabilities = list(probabilities)
                    bestD = tag
                    
                    
                #cur.execute("SELECT COUNT(*) from ObjectTagAnswers WHERE objectID=%s AND tag=%s", (objectID, tags[tag]))
                #test = cur.fetchone()[0]
                #if(test > 0):
                #    cur.execute("SELECT yes_answers, no_answers FROM ObjectTagAnswers WHERE objectID=%s AND tag=%s", (objectID, tags[tag]))
                #    currentAnswers = cur.fetchall()
                #    yes = 
                #    no = currentAnswers[1]
                #    cur.execute("UPDATE ObjectTagAnswers SET yes_answers = %s, no_answers = %s")
                
                if N == 0:
                    zero = zero + 1
                if D == 0:
                    not_asked = not_asked + 1
        else:
            pass
            
    print str(bestDifference) + " -> " + tags[bestD]
    print str(zero) + " N empty. " + str(not_asked) + " D empty"
    
    #askedQuestions.append(tags[bestD])
    #bestDifference = 0
    #
    ##answer = raw_input('Is it ' + tags[bestD] + '? (yes/no) ')
    #print 'Is it ' + tags[bestD] + '? (yes/no) '
    #answer = answer_data[object_id][bestD]
    #print bestD
    #
    #if answer == 'yes':
    #    print 'yes'
    #    answers.append(True)
    #    for objectID in range(0,17):
    #        pass
    #        cur.execute("SELECT COUNT(*) as count FROM Descriptions WHERE description like '%" + tags[bestD] + "%' AND objectID = " + str(objectID+1))
    #        T = cur.fetchone()[0]
    #        
    #        cur.execute("SELECT COUNT(*) as count FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND answer=TRUE AND tag='" + tags[bestD] + "'")
    #        N = cur.fetchone()[0]
    #            
    #        cur.execute("SELECT COUNT(*) as count FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND tag='" + tags[bestD] + "'")
    #        D = cur.fetchone()[0]
    #    
    #        pO[objectID] = pO[objectID] * (probabilityD[T] + (N + 1)/(D + 2.0))
    #else:
    #    print 'no'
    #    answers.append(False)
    #    for objectID in range(0,17):
    #        pass
    #        cur.execute("SELECT COUNT(*) as count FROM Descriptions WHERE description like '%" + tags[bestD] + "%' AND objectID = " + str(objectID+1))
    #        T = cur.fetchone()[0]
    #                    
    #        cur.execute("SELECT COUNT(*) as count FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND answer=FALSE AND tag='" + tags[bestD] + "'")
    #        N = cur.fetchone()[0]
    #            
    #        cur.execute("SELECT COUNT(*) as count FROM QuestionAnswers WHERE object=" + str(objectID+1) + " AND tag='" + tags[bestD] + "'")
    #        D = cur.fetchone()[0]
    #        
    #        pO[objectID] = pO[objectID] * ((1 - probabilityD[T]) + (N + 1)/(D + 2.0))
    #    
    #pO = pO/sum(pO)
    #
    #pO_sorted = np.sort(pO)
    #pO_args_sorted = np.argsort(pO)
    #
    #for x in range(0,17):
    #    print str(pO_args_sorted[x]) + " -> " + str(pO_sorted[x])
    #    
    #diff = 0
    #bestDiff = 0
    #
    #for x in range(0, pO_sorted.size-1):
    #    if pO_sorted[x+1] - pO_sorted[x] > diff:
    #        diff = pO_sorted[x+1] - pO_sorted[x]
    #        bestDiff = x
    #print diff
    #print bestDiff
    #
    #con.close()
    #gc.collect()
    #
    #return bestDiff

prob_by_tag_frequency()

#for object_id in range(0,17):
#    pO = np.array([1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0,1/17.0])
#    asked = []
#    answers = []
#    split = 0
#    probabilityD = prob_by_tag_frequency()
#    answer_data = np.genfromtxt('/local2/awh0047/iSpy/ISPY_PY/Answers/Game1.csv',dtype=str, delimiter='\t')
#    while True:
#        split = best_tag(asked, answers, pO, split, probabilityD, object_id)
#        pO = pO/sum(pO)
#        if decide_to_guess(pO):
#            #final_answer = raw_input("Is it object " + str(np.argsort(pO)[pO.size-1] + 1) + "? (yes/no) ")
#            print "Is it object " + str(np.argsort(pO)[pO.size-1] + 1) + "? (yes/no) "
#            if np.argsort(pO)[pO.size-1] == object_id:
#                final_answer = 'yes'
#            else:
#                final_answer = 'no'
#            if final_answer == 'yes':
#                print 'Good game!'
#                log_tag_answers(asked, answers, np.argsort(pO)[pO.size-1] + 1)
#            else:
#                #object_id = raw_input("Which object number did you have in mind? ")
#                print "Which object number did you have in mind? "
#                print object_id + 1
#                log_tag_answers(asked, answers, object_id+1)            
#            break
#        else:
#            pass