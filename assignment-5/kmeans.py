# Python 3.0
import re
import math
import collections
import time


# import other modules as needed
# implement other functions as needed
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

	# function to implement k means clustering algorithm
	# Print out:
	#   For each cluster, its RSS values and the document ID of the document closest to its centroid.
	#   Average RSS value
	#   Time taken for computation.
	def clustering(self, k_value):
		pass


i = Index("time/TIME.ALL", "time/TIME.STP")

i.build_index()
