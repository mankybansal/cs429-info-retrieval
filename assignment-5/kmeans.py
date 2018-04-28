# Python 3.0
import re
import math
import collections
import time
import random

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
		self.avg_rss = []

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
		for token in self.all_tokens_set:
			for i, v in enumerate(self.collection[token]):
				if i != 0:
					self.document_vectors[v[0]][token] = v[1]
					self.document_magnitudes[v[0]] += v[1] ** 2

		# recalculate magnitude
		for doc, mag in self.document_magnitudes.items():
			self.document_magnitudes[doc] = math.sqrt(mag)
		end = time.time()
		print("TF-IDF Index built in", '{:.20f}'.format(end - start), "seconds")

	def cosine_similarity_docs(self, doc_1, doc_2):
		scores = 0

		doc_v1 = self.document_vectors[doc_1]
		doc_v2 = self.document_vectors[doc_2]

		for k, v in doc_v1.items():
			if k in doc_v2.keys():
				scores += v * doc_v2[k]

		length = self.document_magnitudes[doc_1] * self.document_magnitudes[doc_2]
		if length > 0:
			cosine_score = scores / length
		else:
			cosine_score = 0

		return cosine_score

	# function to implement k means clustering algorithm
	# Print out:
	#   For each cluster, its RSS values and the document ID of the document closest to its centroid.
	#   Average RSS value
	#   Time taken for computation.

	def cosine_score(self, centroids, k_value):
		cosine_scores = collections.defaultdict(list)
		for centroid in centroids:
			cosine_scores[centroid] = [-1] * len(self.doc_id)

		for centroid in centroids:
			# print(centroids[i], i, len(centroids))
			for j in range(0, len(self.doc_id)):
				cosine_scores[centroid][j] = self.cosine_similarity_docs(centroid, j)

		#print(cosine_scores)
		return cosine_scores

	def assign_cluster(self, centroids, cosine_scores, k_value):

		clusters = collections.defaultdict(list)
		for centroid in centroids:
			clusters[centroid] = []

		#print(clusters)

		for i in self.doc_id:
			values = []
			for centroid in centroids:
				values.append(cosine_scores[centroid][i])
			# print("assign_cluster, values size:", len(values), "values:", values)
			clusters[centroids[values.index(max(values))]].append(i)
		#print("assign_cluster, clusters:", clusters.keys())
		#print("assign_cluster, clusters size:", len(clusters))
		#print(clusters)
		return clusters

	def new_centroids(self, clusters, cosine_scores, k_value):

		centroids = []
		avg_rss = 0
		#print("new_centroids, cluster size:", len(clusters.keys()))
		for k, v in clusters.items():
			avg = 0
			for v2 in v:
				avg += cosine_scores[k][v2]
			avg /= len(clusters[k])

			rss = 0
			min = 9999
			min_index = -1
			for k2, v2 in enumerate(clusters[k]):
				rss += (cosine_scores[k][v2] - avg) ** 2
				diff = cosine_scores[k][v2] - avg
				if diff < min:
					min = diff
					min_index = v2
			avg_rss += rss
			centroids.append(min_index)
		self.avg_rss.append(avg_rss / len(clusters.keys()))
		#print("new_centroids, centroid size:", len(centroids))
		return centroids

	def clustering(self, k_value):
		self.avg_rss = []

		centroids = []
		while k_value > 0:
			centroid_id = random.randint(0, len(self.doc_id) - 1)
			if centroid_id not in centroids:
				centroids.append(centroid_id)
				k_value -= 1
		#print("Init Centroids:", centroids)

		k_value = len(centroids)

		for times in range(0, 3):
			cosine_scores = self.cosine_score(centroids, k_value)
			clusters = self.assign_cluster(centroids, cosine_scores, k_value)
			# for i in range(0, len(clusters.keys())):
			# 	print("   Cluster", i + 1, " (count):", len(clusters[i]))
			centroids = self.new_centroids(clusters, cosine_scores, k_value)

			#print("\nNew Centroids:", centroids)


i = Index("time/TIME.ALL", "time/TIME.STP")

i.build_index()


for k in range(2, 30):
	start = time.time()
	i.clustering(k)
	end = time.time()
	print("Avg RSS ( k =", k, "):", sum(i.avg_rss) / len(i.avg_rss), "\ttime:", '{:.20f}'.format(end - start), "seconds")
