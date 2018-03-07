# Python 3.6.4

import re
import os
import collections
import time


class Index:
	def __init__(self, path):
		pass

	# function to read documents from collection, tokenize and build the index with tokens
	# implement additional functionality to support relevance feedback
	# use unique document integer IDs
	def build_index(self):
		pass

	# function to implement rocchio algorithm
	# pos_feedback - documents deemed to be relevant by the user
	# neg_feedback - documents deemed to be non-relevant by the user
	# Return the new query  terms and their weights
	def rocchio(self, query_terms, pos_feedback, neg_feedback, alpha, beta, gamma):
		pass

	# function for exact top K retrieval using cosine similarity
	# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	def query(self, query_terms, k):
		pass

	# function to print the terms and posting list in the index
	def print_dict(self):
		pass

	# function to print the documents and their document id
	def print_doc_list(self):
		pass
