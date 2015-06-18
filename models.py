import os
import logging as log

import questions
import database as db

def build(_game, method, game_questions={}, game_answers={}, skip={}):
    """
    Build the model for all keywords using 1 of 3 different methods
    Currently only 1 and 3 work
    """

    log.info("Retraining model")

    #get all the different tags available
    db.cursor.execute("SELECT DISTINCT(tag) FROM TagInfoBk")
    results=db.cursor.fetchall()

    tags = []
    for result in results:
        tags.append(result[0])

    count = 0
    # Builds models by using images where the answer set has a yes for the paring as a positive example
    if method == 1:
        #for each tag we select all the observation_ids that are related to it
        for tag in tags:
            feature_matrix=[]#initialize feature matrix for each different tag
            feature_matrix_labels = [] # Labels to indicate if the example is positive or negative
            #cursor.execute("SELECT DISTINCT(observation_id) FROM TagInfoBk WHERE tag=%s",(tag))
            db.cursor.execute("SELECT DISTINCT(observation_id) FROM TagInfoBk")
            tag_obs_ids=db.cursor.fetchall()
            db.cursor.execute('SELECT id FROM Tags WHERE tag = %s', (tag,))
            qid = db.cursor.fetchone()[0]

            should_train = False
            #for every observation/object of this spesific tag
            for obs_id in tag_obs_ids:

                object_matrix = []
                T = questions.get_t(obs_id[0], qid)
                if _game.id == 0:
                    if T >= 3:
                        should_train = True
                        count = count + 1
                        db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], _game.id))
                        num_of_images_per_oservation=db.cursor.fetchall()

                        db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],_game.id))
                        feature_info=db.cursor.fetchall()

                        vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                        new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                        end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                        for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                            feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                            #print len(feature_vector)
                            new_fv=new_fv+vv_seperator #update starting index of the vector
                            end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                            feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                        feature_matrix_labels.append(1)
                else:
                #elif _game.id < 16:
                    model_folder = os.getcwd() + '/GMM_model_777'
                    listing = os.listdir(model_folder)
                    has_model = []
                    for mod in listing:
                        if mod.endswith('.pkl'):
                            model_clone = joblib.load(model_folder + '/' + mod)
                            T = mod.split('_', 1)[0]
                            T = T.lower()
                            has_model.append(T)
                    for game in range(0, _game.id+1):
                        if tag.lower() in has_model:
                            if game == 0:
                                should_train = True
                                count = count + 1
                                db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                num_of_images_per_oservation=db.cursor.fetchall()

                                db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                feature_info=db.cursor.fetchall()

                                vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                    feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                    #print len(feature_vector)
                                    new_fv=new_fv+vv_seperator #update starting index of the vector
                                    end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                    feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                feature_matrix_labels.append(1)
                            else:
                                answer_data = np.genfromtxt(os.getcwd()+'/Answers/Game'+str(game)+'.csv',dtype=str, delimiter='\t')
                                #cursor.execute("SELECT id FROM Tags where tag ='{0}'".format(tag))
                                #tag_id = cursor.fetchone()[0]
                                if answer_data[int(obs_id[0])-1][qid-1] == 'yes' or answer_data[int(obs_id[0])-1][qid-1] is 'yes':
                                    should_train = True
                                    count = count + 1
                                    db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                    num_of_images_per_oservation=db.cursor.fetchall()

                                    db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                    feature_info=db.cursor.fetchall()

                                    vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                    new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                    end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                    for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                        feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                        #print len(feature_vector)
                                        new_fv=new_fv+vv_seperator #update starting index of the vector
                                        end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                        feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                    feature_matrix_labels.append(1)

            if should_train:
                #print len(feature_matrix)
                feature_matrix=np.asarray(feature_matrix)
                model.ModelTraining(tag, feature_matrix, 777) #training the model
    elif method == 2:
        pass
    # Up to game 15, uses images that received a yes as positive and no as negative (All questions)
    # Beyond that, only uses keywords from the game (Much smaller subset)
    elif method == 3:
        #for each tag we select all the observation_ids that are related to it
        for tag in tags:
            if tag not in skip:
                feature_matrix=[]#initialize feature matrix for each different tag
                feature_matrix_labels = [] # Labels to indicate if the example is positive or negative
                #cursor.execute("SELECT DISTINCT(observation_id) FROM TagInfoBk WHERE tag=%s",(tag))
                db.cursor.execute("SELECT DISTINCT(observation_id) FROM TagInfoBk")
                tag_obs_ids=db.cursor.fetchall()
                db.cursor.execute('SELECT id FROM Tags WHERE tag = %s', (tag,))
                qid = db.cursor.fetchone()[0]

                should_train = False
                #for every observation/object of this spesific tag
                for obs_id in tag_obs_ids:

                    T = questions.get_t(obs_id[0], qid)
                    # For game 0, if a tag has been used 3 or more times in the object descriptions, that object is used as a positive example
                    if _game.id == 0:
                        if T >= 3:
                            should_train = True
                            count = count + 1
                            db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], _game.id))
                            num_of_images_per_oservation=db.cursor.fetchall()

                            db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],_game.id))
                            feature_info=db.cursor.fetchall()

                            vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                            new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                            end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                            for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                #print len(feature_vector)
                                new_fv=new_fv+vv_seperator #update starting index of the vector
                                end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                feature_matrix_labels.append(1)
                        # An object is only a negative example if it is used 0 times
                        elif T == 0:
                            count = count + 1
                            db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], _game.id))
                            num_of_images_per_oservation=db.cursor.fetchall()

                            db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],_game.id))
                            feature_info=db.cursor.fetchall()

                            vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                            new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                            end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                            for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                #print len(feature_vector)
                                new_fv=new_fv+vv_seperator #update starting index of the vector
                                end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                feature_matrix_labels.append(0)
                        #print len(feature_matrix_labels)
                    # games up to 15 trained using all available answer data
                    elif _game.id < 16:
                        answer_data = np.genfromtxt(os.getcwd()+'/Answers/Game'+str(_game.id)+'.csv',dtype=str, delimiter='\t')
                        model_folder = os.getcwd() + '/GMM_model_777'
                        listing = os.listdir(model_folder)
                        has_model = []
                        for mod in listing:
                            if mod.endswith('.pkl'):
                                model_clone = joblib.load(model_folder + '/' + mod)
                                K = mod.split('_', 1)[0]
                                K = K.lower()
                                has_model.append(K)
                        for game in range(0, _game.id+1):
                            if tag.lower() in has_model:
                                if game == 0:
                                    if T >= 3:
                                        should_train = True
                                        count = count + 1
                                        db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                        num_of_images_per_oservation=db.cursor.fetchall()

                                        db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                        feature_info=db.cursor.fetchall()

                                        vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                        new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                        end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                        for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                            feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                            #print len(feature_vector)
                                            new_fv=new_fv+vv_seperator #update starting index of the vector
                                            end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                            feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                            feature_matrix_labels.append(1)
                                    elif T == 0:
                                        should_train = True
                                        count = count + 1
                                        db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                        num_of_images_per_oservation=db.cursor.fetchall()

                                        db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                        feature_info=cursor.fetchall()

                                        vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                        new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                        end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                        for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                            feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                            #print len(feature_vector)
                                            new_fv=new_fv+vv_seperator #update starting index of the vector
                                            end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                            feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                            feature_matrix_labels.append(0)
                                else:
                                    answer_data = np.genfromtxt(os.getcwd()+'/Answers/Game'+str(game)+'.csv',dtype=str, delimiter='\t')
                                    #cursor.execute("SELECT id FROM Tags where tag ='{0}'".format(tag))
                                    #tag_id = cursor.fetchone()[0]
                                    if answer_data[int(obs_id[0])-1][qid-1] == 'yes' or answer_data[int(obs_id[0])-1][qid-1] is 'yes':
                                        should_train = True
                                        count = count + 1
                                        db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                        num_of_images_per_oservation=db.cursor.fetchall()

                                        db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                        feature_info=db.cursor.fetchall()

                                        vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                        new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                        end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                        for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                            feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                            #print len(feature_vector)
                                            new_fv=new_fv+vv_seperator #update starting index of the vector
                                            end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                            feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                            feature_matrix_labels.append(1)
                                    else:
                                        should_train = True
                                        count = count + 1
                                        db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                        num_of_images_per_oservation=db.cursor.fetchall()

                                        db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                        feature_info=db.cursor.fetchall()

                                        vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                        new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                        end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                        for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                            feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                            #print len(feature_vector)
                                            new_fv=new_fv+vv_seperator #update starting index of the vector
                                            end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                            feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                            feature_matrix_labels.append(0)
                    # Otherwise, use only questions from gameplay
                    else:
                        model_folder = os.getcwd() + '/GMM_model_777'
                        listing = os.listdir(model_folder)
                        has_model = []
                        for mod in listing:
                            if mod.endswith('.pkl'):
                                model_clone = joblib.load(model_folder + '/' + mod)
                                K = mod.split('_', 1)[0]
                                K = K.lower()
                                has_model.append(K)
                        for game in range(0, _game.id+1):
                            #print game
                            if tag.lower() in has_model:
                                if game == 0:
                                    if T >= 3:
                                        should_train = True
                                        count = count + 1
                                        db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                        num_of_images_per_oservation=db.cursor.fetchall()

                                        db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                        feature_info=db.cursor.fetchall()

                                        vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                        new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                        end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                        for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                            feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                            #print len(feature_vector)
                                            new_fv=new_fv+vv_seperator #update starting index of the vector
                                            end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                            feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag
                                            feature_matrix_labels.append(1)
                                    elif T == 0:
                                        should_train = True
                                        count = count + 1
                                        db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                        num_of_images_per_oservation=db.cursor.fetchall()

                                        db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                        feature_info=db.cursor.fetchall()

                                        vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                        new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                        end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                        for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                            feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                            #print len(feature_vector)
                                            new_fv=new_fv+vv_seperator #update starting index of the vector
                                            end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                            feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag
                                            feature_matrix_labels.append(0)
                                elif game < 16:
                                    answer_data = np.genfromtxt(os.getcwd()+'/Answers/Game'+str(game)+'.csv',dtype=str, delimiter='\t')
                                    #cursor.execute("SELECT id FROM Tags where tag ='{0}'".format(tag))
                                    #tag_id = cursor.fetchone()[0]
                                    if answer_data[int(obs_id[0])-1][qid-1] == 'yes' or answer_data[int(obs_id[0])-1][qid-1] is 'yes':
                                        should_train = True
                                        count = count + 1
                                        db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                        num_of_images_per_oservation=db.cursor.fetchall()

                                        db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                        feature_info=db.cursor.fetchall()

                                        vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                        new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                        end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                        for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                            feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                            #print len(feature_vector)
                                            new_fv=new_fv+vv_seperator #update starting index of the vector
                                            end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                            feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                            feature_matrix_labels.append(1)
                                    elif answer_data[int(obs_id[0])-1][qid-1] == 'no' or answer_data[int(obs_id[0])-1][qid-1] is 'no':
                                        should_train = True
                                        count = count + 1
                                        db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                        num_of_images_per_oservation=db.cursor.fetchall()

                                        db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                        feature_info=db.cursor.fetchall()

                                        vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                        new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                        end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                        for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                            feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                            #print len(feature_vector)
                                            new_fv=new_fv+vv_seperator #update starting index of the vector
                                            end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                            feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                            feature_matrix_labels.append(0)
                                else:
                                    db.cursor.execute("SELECT id FROM Tags WHERE tag = '{0}'".format(tag))
                                    tag_id = db.cursor.fetchone()[0]
                                    if tag_id in game_questions[game][int(obs_id[0])]:
                                        index = game_questions[game][int(obs_id[0])].index(tag_id)
                                        #cursor.execute("SELECT id FROM Tags where tag ='{0}'".format(tag))
                                        #tag_id = cursor.fetchone()[0]
                                        if game_answers[game][int(obs_id[0])][index] == 1:
                                            should_train = True
                                            count = count + 1
                                            db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                            num_of_images_per_oservation=db.cursor.fetchall()

                                            db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                            feature_info=db.cursor.fetchall()

                                            vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                            new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                            end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                            for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                                feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                                #print len(feature_vector)
                                                new_fv=new_fv+vv_seperator #update starting index of the vector
                                                end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                                feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                                feature_matrix_labels.append(1)
                                        elif game_answers[game][int(obs_id[0])][index] == 0:
                                            should_train = True
                                            count = count + 1
                                            db.cursor.execute("SELECT COUNT(*) FROM FeatureInfo WHERE feature_id='0' AND observation_id='{0}' AND game_id='{1}' ".format(obs_id[0], game))
                                            num_of_images_per_oservation=db.cursor.fetchall()

                                            db.cursor.execute("SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id='{0}' AND game_id='{1}'".format(obs_id[0],game))
                                            feature_info=db.cursor.fetchall()

                                            vv_seperator=len(feature_info)/num_of_images_per_oservation[0][0]

                                            new_fv=0 #flag to show when a feature vector given a capture starts (index in feature_info tuple)
                                            end_of_fv=vv_seperator#flag to show when a feature vector given a capture ends (index in feature_info tuple)

                                            for capture_id in xrange(0,num_of_images_per_oservation[0][0]):
                                                feature_vector=RetrieveFeatureVector(feature_info,new_fv,end_of_fv) #create a feature vector given a capture
                                                #print len(feature_vector)
                                                new_fv=new_fv+vv_seperator #update starting index of the vector
                                                end_of_fv=end_of_fv+vv_seperator #update ending index of the vector
                                                feature_matrix.append(feature_vector) #insert feature vectors into a matrix for each tag

                                                feature_matrix_labels.append(0)

                if should_train:
                    feature_matrix=np.asarray(feature_matrix)
                    #model.ModelTraining(tag, feature_matrix, 777) #training the model with GMM
                    model.ModelTrainingSVM(tag, feature_matrix, feature_matrix_labels, 777) #training the model with SVM
    #print count


def gen_image_probabilities(game):
	# Collect all keyword classifiers and feature vectors of objects in the game space
	models, feature_vectors, labels = info(game)
	available_models = []
	probabilities = {}
	for i in range(0, 17):
		probability = []
		for j in range(1, 290):
			if j in models:
				# Score feature vector against keyword classifier and save the probability
				probability.append(models[j].score(feature_vectors[i], labels[i]))
				available_models.append(j-1)
				beans = models[j].score(feature_vectors[i], labels[i])
				if beans > 0:
					print j, beans
			else:
				# If no keyword classifier is available, score as -1 so we can skip later
				probability.append(-1)
		probabilities[i] = probability
	log.info("Image %d processed for game %d", i + 1, game.id)

	return probabilities


def evaluation_1(game):
	Pi = gen_image_probabilities_evaluation(game)
	with open("evaluation1.txt", "a") as myfile:
		myfile.write(str(game.id) + " game: \n")
		for obj in range(0, 17):
			for tag in range(0, 289):
				if Pi[obj][tag] >= 0:
					myfile.write(str(obj + 1) + " object: " + str(tag+1) + " -> " + get_tag(tag+1,cursor) + " tag: " + str(Pi[obj][tag]) + " score \n")
		myfile.write("\n")
	myfile.close() 


def gen_image_probabilities_evaluation(game):
	models, feature_vectors, feature_vector_labels = info(game)
	available_models = []
	probabilities = {}
	for i in range(0, 17):
		probability = []
		for j in range(1, 290):
			if j in models:
				probability.append(score_tag(feature_vectors[i], models[j]))
				available_models.append(j-1)
			else:
				probability.append(-1)
		probabilities[i] = probability
	log.info("Image " + str(i + 1) + " processed")

	return probabilities


def score_tag(feature_vector, model):
    prob = model.score([feature_vector])
    return math.e ** (prob[0] / 100000.0)


def info(game):
    """
    Gets model info
    """

    log.info("Getting model info for Game %d", game.id)

    # Get all of the model vectors from the database
    feature_matrix = []
    feature_matrix_labels = []
    for i in range(1, 18):
        db.cursor.execute('SELECT COUNT(*) FROM FeatureInfo WHERE feature_id="0" AND observation_id="{0}" AND game_id < "{1}"'.format(i, game.id))
        num_of_images_per_observation = db.cursor.fetchall()

        db.cursor.execute('SELECT feature_id,feature_value FROM FeatureInfo WHERE observation_id="{0}" AND game_id < "{1}"'.format(i, game.id))
        feature_info = db.cursor.fetchall()

        vv_seperator = len(feature_info)/num_of_images_per_observation[0][0]

        new_fv = 0 # flag to show when a feature vector given a capture starts (index in feature_info tuple)
        end_of_fv = vv_seperator # flag to show when a feature vector given a capture ends (index in feature_info tuple)
        matrix_labels = []
        matrix = []

        for capture_id in xrange(0, num_of_images_per_observation[0][0]):
            feature_vector = RetrieveFeatureVector(feature_info, new_fv, end_of_fv) # create a feature vector given a capture
            #print len(feature_vector)
            new_fv = new_fv + vv_seperator # update starting index of the vector
            end_of_fv = end_of_fv + vv_seperator # update ending index of the vector
            matrix.append(feature_vector) # insert feature vectors into a matrix for each tag
            matrix_labels.append(1)
        feature_matrix.append(matrix)
        feature_matrix_labels.append(matrix_labels)
        #image_path = os.getcwd() + "/GAMES/Game" + str(game_id) + '/obj' + str(i) + '.jpg'
        #image = cv2.imread(image_path)
        #feature_vectors.append(test_ft.FeatureExtraction(image))

    models = {}
    model_folder = os.getcwd() + '/SVM_model_777'
    listing = os.listdir(model_folder)

    for model in listing:
        if model.endswith('.pkl'):

            model_clone = joblib.load(model_folder + '/' + model)
            T = model.split('_', 1)[0]
            T = T.lower()
            db.cursor.execute('SELECT id FROM Tags WHERE tag = %s', (T))
            qid = db.cursor.fetchone()[0]
            models[qid] = model_clone

    return models, feature_matrix, feature_matrix_labels


def RetrieveFeatureVector(feature_info, start, end):
    feature_vector=[]
   
    for index in xrange(start,end):  
	feature_vector.append(feature_info[index][1])
    return feature_vector