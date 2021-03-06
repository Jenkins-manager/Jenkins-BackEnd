"""
    Question analysis class: breaks down user questions and
    selects appropriate database item
"""

import ast
import threading
import random
import re

from difflib import SequenceMatcher
from thesaurus import Word

from file_processor import FileProcessor

class QuestionAnalysis(threading.Thread):

    def __init__(self, question):
        threading.Thread.__init__(self)
        self.question = question
        self.address = None

    def run(self):
        print("starting single keywords question thread")

        # preparation stage
        split_question = QuestionAnalysis.question_destroy(self.question)
        processed_question = QuestionAnalysis.remove_non_keywords(split_question)
        # initial match
        match = QuestionAnalysis.match_keyword_to_address(processed_question)
        if match != None:
            print("finished question thread at stage 1")
            self.address = match
            return match

        # second stage
        match = QuestionAnalysis.compare_keyword_to_list(processed_question)
        if match != None:
            print("finished question thread at stage 2")
            self.address = match
            return match

        # third stage
        match = QuestionAnalysis.find_synonym(processed_question)
        if match != None:
            print("finished question thread at stage 3")
            self.address = match
            return match

        print("finished question thread with no result, picking random response...")
        return None

    @staticmethod
    def question_destroy(question):
        q_arr = question.split()
        return map(lambda w: w.lower(), list(filter(lambda w: len(w) > 2, q_arr)))

    @staticmethod
    def non_keywords_list():
        return FileProcessor.read_file('./key_words/non_keywords.jenk').split(" ")

    @staticmethod
    def remove_non_keywords(q_arr):
        non_keywords = QuestionAnalysis.non_keywords_list()
        return filter(lambda w: w not in non_keywords, q_arr)

    @staticmethod
    def match_keyword_to_address(q_arr):
        keyword_list = QuestionAnalysis.get_question_keywords()
        matched_word = list(filter(lambda w: w in keyword_list.keys(), q_arr))
        return None if matched_word == [] else keyword_list[matched_word[0]]

    @staticmethod
    def get_question_keywords():
        return ast.literal_eval(FileProcessor.read_file('./key_words/keywords.jenk'))

    @staticmethod
    def compare_keyword_to_list(q_arr):
        keyword_list = QuestionAnalysis.get_question_keywords()
        for word in q_arr:
            for key in keyword_list.keys():
                if SequenceMatcher(None, word, key).ratio() > 0.8:
                    return keyword_list[key]

    @staticmethod
    def add_word_to_keyword_list(word, address, keywords):
        keywords[word] = address
        FileProcessor.write_file('./key_words/keywords.jenk', str(keywords), 'w')
        return keywords

    @staticmethod
    def find_synonym(q_arr):
        keyword_list = QuestionAnalysis.get_question_keywords()
        for word in q_arr:
            words = Word(word).synonyms()
            matches = list(filter(lambda w: w in keyword_list.keys(), words))
            if matches != []:
                QuestionAnalysis.add_word_to_keyword_list(word, keyword_list[matches[0]], keyword_list)
                return keyword_list[matches[0]]
    @staticmethod
    def get_funny_response():
        return random.choice(FileProcessor.read_file('./key_words/responses.jenk').split('|'))

    @staticmethod
    def strip_question(question):
        return re.sub('[^a-z|A-Z|\s]', '', question)

    @staticmethod
    def process_user_question(question):
        question = QuestionAnalysis.strip_question(question)
        thread = QuestionAnalysis(question)
        scanning_thread = QuestionAnalysis.ScanningClass(question)
        scanning_thread.start()
        thread.start()
        scanning_thread.join()
        if scanning_thread.scanned_answer != None:
            print("scanning thread complete")
            return scanning_thread.scanned_answer
        thread.join()
        return thread.address

    class ScanningClass(threading.Thread):
        def __init__(self, question):
            threading.Thread.__init__(self)
            self.question = question
            self.scanned_answer = None

        def run(self):
            print("starting scanning thread")
            self.scanned_answer = QuestionAnalysis.ScanningClass.scan_for_keywords(self.question)

        @staticmethod
        def scan_for_keywords(question):
            question = question.lower()
            # prep stage: filter out non two work k/w
            keyword_list = QuestionAnalysis.get_question_keywords()

            # stage 1 match whole k/w vs q
            f_list = filter(lambda s: s in question, keyword_list)
            if len(f_list) > 0:
                return keyword_list[max(f_list, key=len)]
