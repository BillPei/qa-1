# -*- coding: utf-8 -*-

import random
import nltk
import pickle
from MyConfig import MyConfig

from nltk.tree import Tree
from nltk.probability import FreqDist
from collections import Counter
from Answer import Answer
from qc import *

class AnswerExtractionAlgorithm(object):

	@classmethod
	def process_answer(self, passage, question):
		pass


class XXXAlgorithm(AnswerExtractionAlgorithm):

	@classmethod
	def process_answer(self, passage, question):
		# Do magic
		window = "window = " + passage.text
		exact = "exact"
		random.seed()
		score = random.randint(0, 1000)
		if passage.document.url.find("wikipedia") != -1:
			score = 0

		answer = Answer(passage, question, window, exact, score)

		return answer


class EntityRecognitionAlgorithm(AnswerExtractionAlgorithm):

	@classmethod
	def _question_classification(self, question):
		classifier= MyConfig.get("answer_extraction", "question_classifier")
		if (classifier == "bayes"):
			pkl_file= open('res/qc_bayes.pkl')
		else:
			pkl_file= open('res/qc_maxent.pkl')

		classifier= pickle.load(pkl_file)
		pkl_file.close()

		return classifier.classify(QuestionClassifier.get_features(question))

	@classmethod
	def _ne_recognition(self, text, searched_entities):
		# Entity Classification
		sentences = nltk.sent_tokenize(text)
		tokenized_sentences = [nltk.word_tokenize(s) for s in sentences]
		tagged_sentences = [nltk.pos_tag(s) for s in tokenized_sentences]
		ne_chunked_sentences = nltk.batch_ne_chunk(tagged_sentences)

		# Entity Extraction
		entities = []
		for tree in ne_chunked_sentences:
			for child in tree:
				if isinstance(child, Tree) and child.node in searched_entities:
					entity = " ".join([word for (word, pos) in child.leaves()])
					entities.append(entity)

		return entities

	@classmethod
	def _entity_ranking(self, question, entities):
		if len(entities) == 0:
			return "", "", int(0)

		# Obtain frequency of entities
		entities_freq = FreqDist(entities)

		# Our answer is the sample with the greatest number of outcomes
		exact = entities_freq.max()

		# Our window is ??? TODO
		window = "ventana de texto"

		# Our score is the entity frequency
		# To be improved...
		score = int(entities_freq.freq(exact) * 1000)

		return exact, window, score

	@classmethod
	def process_answer(self, passage, question):
		q = question.text
		p = passage.text

		searched_entities = self._question_classification(q)

		entities = self._ne_recognition(p, searched_entities)

		exact, window, score = self._entity_ranking(q, entities)

		answer = Answer(passage, question, window, exact, score)

		return answer
