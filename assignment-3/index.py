# Python 3.6.4

import re
import collections
import time
import math


class Index:
	def __init__(self, doc_path, stop_list_path):
		self.doc_path = doc_path
		self.stop_list_path = stop_list_path

		self.stop_words = {}
		self.all_tokens_set = {}

		self.doc_id = {}
		self.documents = {}

		self.collection = collections.defaultdict(list)

		self.document_magnitudes = {}
		self.document_vectors = {}

	# function to read documents from collection, tokenize and build the index with tokens
	# implement additional functionality to support relevance feedback
	# use unique document integer IDs
	def build_index(self):
		start = time.time()

		# read stop list
		stop_list = ""
		for line in open(self.stop_list_path):
			stop_list += line.lower()
		self.stop_words = re.sub('[^A-Za-z\n ]+', '', stop_list).split()

		# read and clean documents
		lines = [line.rstrip('\n') for line in open(self.doc_path)]
		doc_id = -1
		for i, line in enumerate(lines):
			if line[:5] == '*TEXT':
				doc_id += 1
				self.doc_id[doc_id] = "TEXT " + line[6:9] + ".txt"
				self.documents[doc_id] = []
			else:
				words = [x for x in re.sub('[^A-Za-z\n ]+', '', line.lower()).split() if x not in self.stop_words]
				self.documents[doc_id].extend(words)

		# insert into init dictionary
		init_dict = collections.defaultdict(dict)
		for key, value in self.doc_id.items():
			for i, word in enumerate(self.documents[key]):
				if key in list(init_dict[word]):
					init_dict[word][key].append(i)
				else:
					init_dict[word][key] = [i]

		# clean dictionary and generate weights
		for i in init_dict.keys():
			idf = math.log(len(self.doc_id) / len(init_dict[i].keys()), 10)
			self.collection[i].append(idf)
			for j in init_dict[i].keys():
				tf_idf = (1 + math.log(len(init_dict[i][j]), 10)) * idf
				self.collection[i].append((j, tf_idf, init_dict[i][j]))

		# init document vectors
		dictionary = list(self.collection.keys())
		for doc in self.doc_id:
			self.document_vectors[doc] = dict.fromkeys(dictionary, 0)
			self.document_magnitudes[doc] = 0

		# insert in vectors & calculate magnitude
		for k, v in self.collection.items():
			for i, v2 in enumerate(v):
				if i > 0:
					self.document_vectors[v2[0]][k] = v2[1]
					self.document_magnitudes[v2[0]] += v2[1]**2

		# recalculate magnitude
		for doc, mag in self.document_magnitudes.items():
			self.document_magnitudes[doc] = math.sqrt(mag)
		end = time.time()
		print("TF-IDF Index built in", '{:.20f}'.format(end - start), "seconds")

	# function to implement rocchio algorithm
	# pos_feedback - documents deemed to be relevant by the user
	# neg_feedback - documents deemed to be non-relevant by the user
	# Return the new query  terms and their weights
	def rocchio(self, query_terms, pos_feedback, neg_feedback, alpha, beta, gamma):
		start = time.time()

		print("Pos Vectors")
		for doc in pos_feedback.split(" "):
			print(doc)
			print(self.document_vectors[int(doc)])

		print("Neg Vectors")
		for doc in neg_feedback.split(" "):
			print(doc)
			print(self.document_vectors[int(doc)])

		end = time.time()
		print("New query computed in", '{:.20f}'.format(end - start), "seconds")
		print("New query terms with weights:")

	# function for exact top K retrieval using cosine similarity
	# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	def query(self, query, k_docs):
		start = time.time()
		q_tf_idf = self.clean_query(query)

		scores = []
		for doc in self.doc_id.keys():
			scores.append((doc, self.cosine_similarity(q_tf_idf, doc)))
		scores.sort(key=lambda x: x[1], reverse=True)
		end = time.time()
		self.print_results(start, end, k_docs, query, scores, "exact retrieval")

	def cosine_similarity(self, q_tf_idf, doc):
		# get product of query and documents
		score = 0
		for k in q_tf_idf.keys():
			if k in self.collection.keys():
				v = self.collection[k]
				for i in range(1, len(v)):
					if v[i][0] == doc:
						score += v[i][1]

		q_mag = 0
		for k, v in q_tf_idf.items():
			for i in range(1, len(v)):
				q_mag += v[i][1] ** 2

		length = self.document_magnitudes[doc] * math.sqrt(q_mag)

		if length != 0:
			cosine_score = score / length
		else:
			cosine_score = 0

		return cosine_score

	@staticmethod
	def query_tf_idf(query):
		init_dict = collections.defaultdict(dict)
		final_dict = collections.defaultdict(list)

		for key, value in enumerate(query):
			word = query[key]
			if key in init_dict[value].keys():
				init_dict[word][0].append(key)
			else:
				init_dict[word][0] = [key]

		for i in init_dict.keys():
			idf = math.log(len(query) / len(init_dict[i].keys()), 10)
			final_dict[i].append(idf)
			for j in init_dict[i].keys():
				tf_idf = (1 + math.log(len(init_dict[i][j]), 10)) * idf
				final_dict[i].append((j, tf_idf, init_dict[i][j]))

		return final_dict

	'''
	helper functions
	'''

	# function to print the terms and posting list in the index
	def print_dict(self):
		pass

	# function to print the document ids
	def print_doc_list(self):
		pass

	# function to clean a query
	def clean_query(self, query):
		query = re.sub('[^A-Za-z\n ]+', '', query.lower()).split()
		query = [x for x in query if x not in self.stop_words]
		return self.query_tf_idf(query)

	# function to print results
	def print_results(self, start, end, k, query, scores, method):
		print("\nTop", k, "result(s) for the query '", query, "' using", method, "method are:\n\nRANK | DOC_ID | DOC_NAME      | SCORE")
		for i in range(k):
			print('{num:02d}'.format(num=i+1), "  |", '{num:03d}'.format(num=scores[i][0]), "   |", self.doc_id[scores[i][0]], " |", scores[i][1])
		print("\nResults found in", '{:.20f}'.format(end - start), "seconds")


obj = Index("./time/TIME.ALL", "./time/TIME.STP")
print('\n>>> Build Index')
obj.build_index()

#query = input("Query to search: ")
# k_docs = int(input("Number of (top) results: "))
alpha = 1.0
beta = 0.75
gamma = 0.15

# todo: remove after debug
query = "BACKGROUND OF THE NEW CHANCELLOR OF WEST GERMANY, LUDWIG ERHARD ."
k_docs = 10
obj.query(query, k_docs)

iteration = -1
while 1:
	if iteration == -1:
		query_vector = obj.clean_query(query)

	iteration += 1
	print("\n=== Rocchio Algorithm ===\n")
	print("Iteration:", iteration)
	rel_docs = input("Enter relevant document ids separated by space: ")
	none_rel_docs = input("Enter non-relevant document ids separated by space: ")
	query_vector = obj.rocchio(query_vector, rel_docs, none_rel_docs, alpha, beta, gamma)

	again = input("\nContinue with new query (y/n): ")
	if again == "n":
		break

# todo: print query
