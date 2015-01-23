import csv


question_tag = "beans"
answer = "no"
belief_probs = [1,4,6,2,3,6,2,4,6]
with open("example.txt", "a") as myfile:
				myfile.write(question_tag + " -> " + answer + "\n")
				myfile.write(str(belief_probs))	
