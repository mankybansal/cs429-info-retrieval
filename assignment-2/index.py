# Python 3.6.4

import re
import os
import collections
import time
import math
import random


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

		self.champion_index = {}
		self.leaders = collections.defaultdict(list)

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

		init_dict = collections.defaultdict(dict)

		for key, value in self.doc_id.items():
			# read documents
			document = open(self.doc_path + "/" + value, "r")

			# clean text & split words
			file_text = document.read().lower()
			words = re.sub('[^A-Za-z\n ]+', '', file_text).split()
			words = [x for x in words if x not in self.stop_words]

			self.documents[key] = words
			# add each word to collection
			for i, word in enumerate(words):
				if key in list(init_dict[word]):
					init_dict[word][key].append(i)
				else:
					init_dict[word][key] = [i]

		for i in init_dict.keys():
			idf = math.log(len(self.doc_id) / len(init_dict[i].keys()), 10)
			self.collection[i].append(idf)
			for j in init_dict[i].keys():
				tf_idf = (1 + math.log(len(init_dict[i][j]))) * idf
				self.collection[i].append((j, tf_idf, init_dict[i][j]))

		end = time.time()
		print("TF-IDF Index built in", '{:.20f}'.format(end - start), "seconds")

		print("Generating document vectors")
		start = time.time()
		for doc in self.doc_id:
			document_vector = {}
			for k, v in self.collection.items():
				for i, v2 in enumerate(v):
					if i > 0 & doc == v2[0]:
						document_vector[k] = v2[1]
			self.document_vectors[doc] = document_vector
		end = time.time()
		print("Document vectors built in", '{:.20f}'.format(end - start), "seconds")

		print("Generating document magnitudes")
		start = time.time()
		for i, value in self.documents.items():
			doc_mag = 0
			for k, v in self.collection.items():
				for j in range(1, len(v)):
					if v[j][0] == i:
						doc_mag += v[j][1] ** 2
			self.document_magnitudes[i] = math.sqrt(doc_mag)
		end = time.time()
		print("Magnitudes calculated in", '{:.20f}'.format(end - start), "seconds")

		start = time.time()
		for t, v in self.collection.items():
			sorted_list = v[1:]
			sorted_list.sort(key=lambda x: x[1], reverse=True)
			self.champion_index[t] = [x[0] for x in sorted_list[:len(self.doc_id)]]

		end = time.time()
		print("Champions list built in", '{:.20f}'.format(end - start), "seconds")

		start = time.time()
		leader_index_size = math.floor(math.sqrt(len(self.doc_id)))
		leaders = set()
		while len(leaders) != leader_index_size:
			leaders.add(random.randint(1, len(self.doc_id)))

		for k in leaders:
			for doc in self.doc_id.keys():
				if self.cosine_similarity_docs(k, doc) > 0.05:
					self.leaders[k].append(doc)
		end = time.time()
		print('Cluster Pruning index built in', end - start, 'seconds')

	def clean_query(self, query):
		query = query.split(" ")
		query = [x for x in query if x not in self.stop_words]
		return self.query_tf_idf(query)

	def exact_query(self, query, k_docs):
		start = time.time()
		q_tf_idf = self.clean_query(query)

		scores = []
		for doc in self.doc_id.keys():
			scores.append((doc, self.cosine_similarity(q_tf_idf, doc)))
		scores.sort(key=lambda x: x[1], reverse=True)
		end = time.time()
		self.print_results(start, end, k_docs, query, scores, "exact retrieval")

	# function for exact top K retrieval using champion list (method 2)
	# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	def inexact_query_champion(self, query, k_docs):
		start = time.time()
		q_tf_idf = self.clean_query(query)

		final_list = []
		for k in q_tf_idf.keys():
			if k in self.champion_index.keys():
				final_list += self.champion_index[k]

		scores = []
		for doc in final_list:
			scores.append((doc, self.cosine_similarity(q_tf_idf, doc)))
		scores.sort(key=lambda x: x[1], reverse=True)
		end = time.time()
		self.print_results(start, end, k_docs, query, scores, "champion list")

	# function for exact top K retrieval using index elimination (method 3)
	# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	def inexact_query_index_elimination(self, query, k_docs):
		# create list of docs that contain at least half the query terms
		start = time.time()
		q_tf_idf = self.clean_query(query)

		# check how many terms of query the document has
		term_count = {}
		for t in q_tf_idf.keys():
			if t in self.collection.keys():
				v = self.collection[t]
				for i in range(1, len(v)):
					if v[i][0] in term_count.keys():
						term_count[v[i][0]] += 1
					else:
						term_count[v[i][0]] = 1

		# filter to documents with at least half
		final_list = []
		for k, v in term_count.items():
			if v >= len(q_tf_idf.keys()) / 2:
				final_list.append(k)

		scores = []
		for doc in final_list:
			scores.append((doc, self.cosine_similarity(q_tf_idf, doc)))
		scores.sort(key=lambda x: x[1], reverse=True)
		end = time.time()
		self.print_results(start, end, k_docs, query, scores, "index elimination")

	# function for exact top K retrieval using cluster pruning (method 4)
	# Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
	def inexact_query_cluster_pruning(self, query, k_docs):
		start = time.time()
		q_tf_idf = self.clean_query(query)

		scores = []
		for doc in self.leaders.keys():
			scores.append((doc, self.cosine_similarity(q_tf_idf, doc)))
		scores.sort(key=lambda x: x[1], reverse=True)

		final_list = []
		for x in range(len(scores)):
			for doc in self.leaders[scores[x][0]]:
				final_list.append((doc, scores[x][1]))
		end = time.time()
		self.print_results(start, end, k_docs, query, final_list, "cluster pruning")

	# function to print the terms and posting list in the index
	def print_dict(self):
		pass

	# function to print the documents and their document id
	def print_doc_list(self):
		pass

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

	def cosine_similarity_docs(self, doc_1, doc_2):
		scores = 0

		doc_v1 = self.document_vectors[doc_1]
		doc_v2 = self.document_vectors[doc_2]

		for k, v in doc_v1.items():
			if k in doc_v2.keys():
				scores += v * doc_v2[k]

		length = math.sqrt(self.document_magnitudes[doc_1] * self.document_magnitudes[doc_2])
		if length > 0:
			cosine_score = scores / length
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
				tf_idf = (1 + math.log(len(init_dict[i][j]))) * idf
				final_dict[i].append((j, tf_idf, init_dict[i][j]))

		return final_dict

	def print_results(self, start, end, k, query, scores, method):
		print("Top", k, "result(s) for the query '", query, "' using", method, "method are:")
		for i in range(k):
			print((i + 1), ".", self.doc_id[scores[i][0]], "with score", scores[i][1])
		print("Results found in", '{:.20f}'.format(end - start), "seconds")


obj = Index("./collection", "stop-list.txt")

print('\n>>> Build Index')

queries = [
	"with without yemen",
	"is germany a real country",
	"can germany win the war",
	"what do they speak in germany",
	"why do british people hate the germans"
]

obj.build_index()

for query in queries:
	obj.exact_query(query, 10)
	obj.inexact_query_champion(query, 10)
	obj.inexact_query_index_elimination(query, 10)
	obj.inexact_query_cluster_pruning(query, 10)
