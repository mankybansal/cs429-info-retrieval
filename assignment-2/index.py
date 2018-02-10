# Python 3.6.4

import sys
import re
import os
import collections
import time
import math


class Index:
	def __init__(self, doc_path, stop_list_path):
		self.doc_path = doc_path
		self.stop_list_path = stop_list_path
		self.stop_words = {}
		self.doc_id = {}
		self.collection = collections.defaultdict(dict)
		self.tfidf = {}

	# function to read documents from collection, tokenize and build the index with tokens
	# implement additional functionality to support methods 1 - 4
	# use unique document integer IDs
	def build_index(self):
		start = time.time()

		# generate document ids
		documents = os.listdir(self.doc_path)
		for i, doc_name in enumerate(documents):
			self.doc_id[i] = doc_name

		# get stop list
		stop_list = open(self.stop_list_path, "r").read()
		self.stop_words = re.sub('[^A-Za-z\n ]+', '', stop_list).split()

		# todo: fix indexing
		for key, value in self.doc_id.items():
			# read documents

			document = open(self.doc_path + "/" + value, "r")

			# clean text & split words
			file_text = document.read().lower()
			words = re.sub('[^A-Za-z\n ]+', '', file_text).split()
			words = [x for x in words if x not in self.stop_words]
			self.collection[key] = words

		self.tfidf = self.get_tfidf()

		end = time.time()
		print("Index built in", '{:.20f}'.format(end - start), "seconds")

	def get_tf(self, term, document):
		return document.count(term)

	def get_idf(self):
		idf = {}
		all_tokens_set = self.collection.keys()
		for tkn in all_tokens_set:
			contains_token = map(lambda doc: tkn in doc, self.collection.items())
			idf[tkn] = 1 + math.log(len(self.collection) / (sum(contains_token)))
		return idf

	def get_tfidf(self):
		idf = self.get_idf()
		tfidf = []

		for document in self.collection.items():
			doc_tfidf = []
			for term in idf.keys():
				tf = self.get_tf(term, document)
				doc_tfidf.append(tf * idf[term])
			tfidf.append(doc_tfidf)

		return tfidf

	def cosine_similarity(self, vector1, vector2):
		dot_product = sum(p * q for p, q in zip(vector1, vector2))
		magnitude = math.sqrt(sum([val ** 2 for val in vector1])) * math.sqrt(sum([val ** 2 for val in vector2]))
		if not magnitude:
			return 0
		return dot_product / magnitude

	# function for exact top K retrieval (method 1)
	# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	def exact_query(self, query_terms, k):
		pass

	# function for exact top K retrieval using champion list (method 2)
	# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	def inexact_query_champion(self, query_terms, k):
		pass

	# function for exact top K retrieval using index elimination (method 3)
	# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	def inexact_query_index_elimination(self, query_terms, k):
		pass

	# function for exact top K retrieval using cluster pruning (method 4)
	# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	def inexact_query_cluster_pruning(self, query_terms, k):
		pass

	# function to print the terms and posting list in the index
	def print_dict(self):
		for key, value in self.collection.items():
			sys.stdout.write(key + ": [")
			dict_item_count = len(value)
			dict_position = 1
			for doc_id, positions in value.items():
				sys.stdout.write("(" + str(doc_id) + ", " + "".join(str(positions)) + ")")
				if dict_position != dict_item_count:
					sys.stdout.write(", ")
				dict_position += 1
			sys.stdout.write("]\n")

	# function to print the documents and their document id
	def print_doc_list(self):
		pass


obj = Index("./collection", "stop-list.txt")

print('\n>>> Build Index')
obj.build_index()

print(obj.tfidf)
