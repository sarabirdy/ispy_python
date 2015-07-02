# iSpy_python

I worked on this project while at [UNT](http://unt.edu) working in the [HiLT Lab](http://hilt.cse.unt.edu) as part of the [I Spy Project](http://hilt.cse.unt.edu/ispy.html). I graduated in 2015 with my BS and am now at [Texas A&M](http://tamu.edu) working on my PhD in computer science, so I will no longer be contributing to this code. This code will be maintained by [Jacob](http://github.com/jacobbrunson) during his time in the HiLT Lab.

This code simulates a game of I Spy between two players, who in this case are both simulated. We currently play using a set of 17 objects and hopefully we will be able to add new objects to the playspace soon. Imagine that player 1 selects the object to be guessed, and player 2 tries to guess the object. Player 2 learns about objects based on collected descriptions, player 1's answers to questions, and features extracted from images of the objects. As the system simulates games, player 2 should get better at asking questions to determine which object player 1 has selected. This will simultaneously increase accuracy and decrease the number of questions asked to identify the object.

A (very) rough description of how the simulation works can be found [here](http://hilt.cse.unt.edu/static/images/projects/ispy/SUREPoster2014.pdf). Another description is [here](http://www.aaai.org/ocs/index.php/WS/AAAIW15/paper/viewFile/10074/10210) if you feel like reading a conference paper. The version from the paper is not automated like the version in this repository and the formulas are different, but the concept and goals are similar.

Setup:

1. Make sure the database settings in config.py match your local database
2. If running for the first time, make sure that 'setup = True' is set in config.py. This will clean the database and build the initial models
3. If not the first time, you can change setup to False, but that won't clean out the old answers/start fresh

Run: 
- Execute 'python main.py' from within the ispy_python directory

Dependencies:
- MySQL server
- mysql-python or pymysql
- opencv
- sklearn
- matplotlib
- numpy

Configuration ('config.py')
- db: Database credentials
- setup: Should the pre-simulation tasks be executed?
