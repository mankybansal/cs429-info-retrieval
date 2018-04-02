# Python 3.6.4

import re
import collections
import time
import math


class Index:
	def __init__(self, doc_path, stop_list_path, query_path, relevance_path):
		self.doc_path = doc_path
		self.stop_list_path = stop_list_path
		self.query_path = query_path
		self.relevance_path = relevance_path

		self.stop_words = {}
		self.all_tokens_set = {}
		self.queries = {}
		self.relevant_docs = {}

		self.doc_id = {}
		self.documents = {}

		self.old_maps = []
		self.new_maps = []

		self.collection = collections.defaultdict(list)

		self.document_magnitudes = {}
		self.document_vectors = {}

		# read queries list
		query_id = -1
		for line in open(self.query_path):
			if line[:5] == '*FIND':
				query_id += 1
				self.queries[query_id] = ""
			elif line[:5] == "*STOP":
				continue
			else:
				self.queries[query_id] += line.replace("\n", "") + " "

		# read relevance list
		query_id = -1
		lines = filter(lambda x: not re.match(r'^\s*$', x), open(self.relevance_path))
		for line in lines:
			query_id += 1
			line = list(map(int, line.split()))
			docs = []
			for doc in line[1:len(line)]:
				docs.append(doc)
			self.relevant_docs[query_id] = docs

		# read stop list
		stop_list = ""
		for line in open(self.stop_list_path):
			stop_list += line.lower()
		self.stop_words = re.sub('[^A-Za-z\n ]+', '', stop_list).split()

		# read and clean documents
		lines = [line.rstrip('\n') for line in open(self.doc_path)]
		doc_id = -1
		for line in lines:
			if line[:5] == '*TEXT':
				doc_id += 1
				self.doc_id[doc_id] = "TEXT " + line[6:9] + ".txt"
				self.documents[doc_id] = []
			else:
				words = [x for x in re.sub('[^A-Za-z0-9\n ]+', '', line.lower()).split() if x not in self.stop_words]
				self.documents[doc_id].extend(words)

	# function to read documents from collection, tokenize and build the index with tokens
	# implement additional functionality to support relevance feedback
	# use unique document integer IDs
	def build_index(self):
		print('\n>>> Build Index')

		start = time.time()

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
		self.all_tokens_set = list(self.collection.keys())
		for doc in self.doc_id:
			self.document_vectors[doc] = dict.fromkeys(self.all_tokens_set, 0)
			self.document_magnitudes[doc] = 0

		# insert in vectors & calculate magnitude
		for k, v in self.collection.items():
			for i, v2 in enumerate(v):
				if i > 0:
					self.document_vectors[v2[0]][k] = v2[1]
					self.document_magnitudes[v2[0]] += v2[1] ** 2

		# recalculate magnitude
		for doc, mag in self.document_magnitudes.items():
			self.document_magnitudes[doc] = math.sqrt(mag)
		end = time.time()
		print("TF-IDF Index built in", '{:.20f}'.format(end - start), "seconds")

	# function to implement rocchio algorithm
	# pos_feedback - documents deemed to be relevant by the user
	# neg_feedback - documents deemed to be non-relevant by the user
	# Return the new query  terms and their weights
	def rocchio(self, query_vector, pos_feedback, neg_feedback, alpha, beta, gamma):
		start = time.time()

		# add query weights
		for term, weight in query_vector.items():
			query_vector[term] = alpha * weight

		old_query = {}
		for term, weight in query_vector.items():
			if weight > 0:
				old_query[term] = weight

		# add positive feedback weights
		if len(pos_feedback) > 0:
			pos_feedback = list(map(int, pos_feedback.split(" ")))
			for doc in pos_feedback:
				for term, weight in self.document_vectors[doc - 1].items():
					query_vector[term] += beta * weight / len(pos_feedback)

		# subtract negative feedback weights
		if len(neg_feedback) > 0:
			neg_feedback = list(map(int, neg_feedback.split(" ")))
			for doc in neg_feedback:
				for term, weight in self.document_vectors[doc - 1].items():
					query_vector[term] -= gamma * weight / len(neg_feedback)

		# clean negative weights
		for term, weight in query_vector.items():
			if weight < 0:
				query_vector[term] = 0
		end = time.time()
		print("New query computed in", '{:.20f}'.format(end - start), "seconds")

		new_query = {}
		for term, weight in query_vector.items():
			if weight > 0:
				new_query[term] = weight

		print("New query terms with weights:")
		print(new_query)
		return query_vector

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
		return scores

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

	# function to clean a query
	def clean_query(self, query):
		query = re.sub('[^A-Za-z0-9\n ]+', '', query.lower()).split()
		query = [x for x in query if x not in self.stop_words]
		return self.query_tf_idf(query)

	# function to print results
	def print_results(self, start, end, k, query, scores, method):
		print("\nTop", k, "result(s) for the query '", query, "' using", method,
		      "method are:\n\nRANK | DOC_ID | DOC_NAME      | SCORE")
		for i in range(k):
			print('{num:02d}'.format(num=i + 1), "  |", '{num:03d}'.format(num=scores[i][0] + 1), "   |",
			      self.doc_id[scores[i][0]], " |", scores[i][1])
		print("\nResults found in", '{:.20f}'.format(end - start), "seconds")

	# function to initialize query vector
	def init_query_vector(self, query):
		query_init_dict = obj.clean_query(query)
		query_vector = dict.fromkeys(obj.all_tokens_set, 0)
		for k, v in query_init_dict.items():
			for i, v2 in enumerate(v):
				if i > 0:
					query_vector[k] = v2[1]
		return query_vector

	# function to run pseudo-relevance
	def run_pseudo_relevance(self, query_id, k_docs):
		query = self.queries[query_id]
		results = obj.query(query, k_docs)

		self.find_metrics(query_id, results, k_docs)
		self.old_maps.append(self.find_map(query_id, results))

		org_query_vector = obj.init_query_vector(query)

		for i in range(1, 4):
			print("\n=== Rocchio Algorithm ===\n\nIteration:", i)
			print("\nAssuming top 3 documents are relevant...")
			pos_feedback = str(results[0][0] + 1) + " " + str(results[1][0] + 1) + " " + str(results[2][0] + 1)
			query_vector = obj.rocchio(org_query_vector, pos_feedback, "", 1, 0.75, 0.15)

			query = ""
			for term, weight in query_vector.items():
				if weight > 0:
					query += term + " "
			results = obj.query(query, k_docs)
			self.find_metrics(query_id, results, k_docs)
			self.new_maps.append(self.find_map(query_id, results))

	# function to run rocchio program
	def run_rocchio(self, query, k_docs):
		again = "y"
		iteration = 0
		obj.query(query, k_docs)
		query_vector = self.init_query_vector(query)
		while again == "y":
			iteration += 1
			print("\n=== Rocchio Algorithm ===\n\n", "Iteration:", iteration)
			rel_docs = input("Enter relevant document ids separated by space: ")
			non_rel_docs = input("Enter non-relevant document ids separated by space: ")

			query_vector = obj.rocchio(query_vector, rel_docs, non_rel_docs, 1.0, 0.75, 0.15)

			query = ""
			for term, weight in query_vector.items():
				if weight > 0:
					query += term + " "

			obj.query(query, k_docs)
			again = input("\nContinue with new query (y/n): ")

	def find_metrics(self, query_id, results, k_docs):
		count = 0
		for i in range(0, k_docs):
			if (results[i][0] + 1) in self.relevant_docs[query_id]:
				count += 1
		print("PRECISION: ", count / k_docs)
		print("RECALL:    ", count / len(self.relevant_docs[query_id]))

	def find_map(self, query_id, results):
		count = 0
		recalls = []
		for i in range(0, len(self.relevant_docs[query_id]) + 1):
			if (results[i][0] + 1) in self.relevant_docs[query_id]:
				count += 1
				recalls.append(count / (i + 1))
		return recalls


obj = Index("./time/TIME.ALL", "./time/TIME.STP", "./time/TIME.QUE", "./time/TIME.REL")
obj.build_index()

query = input("Query to search: ")
k_docs = int(input("Number of (top) results: "))

obj.run_rocchio(query, k_docs)

#########################################
#                                       #
#  Uncomment this for Pseudo Relevance  #
#                                       #
#########################################

# query_ids = [5, 38, 39, 57, 79]
# query_ids = [46, 54, 27]
# for query_id in query_ids:
# 	obj.run_pseudo_relevance(query_id, 10)
#
# old_map = 0
# for map in obj.old_maps:
# 	add = 0
# 	for item in map:
# 		add += item
# 	add /= len(map)
# 	old_map += add
# old_map /= len(obj.old_maps)
#
# print("\nWithout Rocchio MAP:", old_map)
#
# new_map = 0
# for i in range(0, 3):
# 	new_map = 0
# 	for j in range(0, len(query_ids)):
# 		add = 0
# 		for map in obj.new_maps[j * 3 + i]:
# 			add += map
# 		add /= len(obj.new_maps[j * 3 + i])
# 		new_map += add
# 	new_map /= len(query_ids)
# 	print("With Rocchio MAP,", (i+1), "iteration(s):", new_map)
