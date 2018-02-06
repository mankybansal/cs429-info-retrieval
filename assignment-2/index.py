# Python 3.0

import re
import os
import collections
import time


# import other modules as needed

class Index:
	def __init__(self, path):
		self.path = path

	# function to read documents from collection, tokenize and build the index with tokens
	# implement additional functionality to support methods 1 - 4
	# use unique document integer IDs
	def build_index(self):
		documents = os.listdir(self.path)

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
		pass

	# function to print the documents and their document id
	def print_doc_list(self):
		pass


obj = Index("./collection")
