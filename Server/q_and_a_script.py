"""
    run this file to create and implmenet a new question /
    answer pair. enter the following details to create a 
    complete pair:
        - question body
        - answer body (should be a function ideally)
        - question keywords (at least one) 
"""
import sys

import django
django.setup()

from model.file_processor import FileProcessor
from questions.models import Question
from answers.models import Answer

help_string = ("run this file to create and implmenet a new question" +
               "answer pair.\n enter the following details to create a" + 
               "complete pair:\n" +
               "    - question body\n" +
               "    - answer body (should be a function ideally)\n" +
               "     - question keywords (at least one)\n")

org_train_set = FileProcessor.read_file('machine_learning/data/value_set.jenk')
org_in_set = FileProcessor.read_file('machine_learning/data/output_set.jenk')
org_key_set = FileProcessor.read_file('./key_words/keywords.jenk')

def revert_data_to_reset():
    FileProcessor.write_file('key_words/keywords.jenk', org_key_set ,'w')
    FileProcessor.write_file('machine_learning/data/value_set.jenk', org_train_set ,'w')
    FileProcessor.write_file('machine_learning/data/output_set.jenk', org_in_set ,'w')

def write_keyword_data(q_keyword, q_address):
    keywords = org_key_set
    keywords[q_keyword] = q_address
    FileProcessor.write_file('key_words/keywords.jenk', str(keywords) ,'w')

def add_to_training_set(q_address, a_address):
    training_set = org_train_set
    input_set = org_in_set
    training_set.append(q_address)
    input_set.append(a_address)
    FileProcessor.write_file('machine_learning/data/value_set.jenk', str(keywords) ,'w')
    FileProcessor.write_file('machine_learning/data/output_set.jenk', str(keywords) ,'w')

def q_and_a_creation(q_body, a_body):
    q_new = Question(q_body, 0)
    a_new = Answer(a_body, 0)
    q_new.save()
    a_new.save()
    q_new = Question.objects.get(body = q_body)
    a_new = Answer.objects.get(address = a_body)
    q_new.address = q_new.id
    a_new.address = a_new.id
    q_new.save()
    a_new.save()
    return [q_new.address, a_new.address]



print("This is the runner for adding questions and answers to the application\n" +
      "Please read the included instructions for more infomation, this can be done"+
      "by entering HELP! at any time, press QQQ to close the script at any time\n"+
      "Enter a question to begin:")

while True:
    try:
        command = sys.stdin.readline().rstrip()
        if command == "QQQ":
            break
        elif command == "HELP!":
            print(help_string)
  
        q_body = command
        print("Now enter an answer please:")
        command = sys.stdin.readline().rstrip()
        a_body = command
        print("now enter your keywords:")
        command = sys.stdin.readline().rstrip()
        keywords = command

        if q_body == "" or a_body == "" or keywords == "":
            raise "you must enter all three fields to continue"
        
        address_pair = q_and_a_creation(q_body, a_body)
        write_keyword_data(address_pair[0], keywords)
        add_to_training_set(address_pair[0], address_pair[1])

        print("saved sucessfully")
        break

    except Exception, e:
        print("an error occured, resetting files..")
        revert_data_to_reset()
        print("your error message is:")
        print(str(e))
        print("\nplease try again")