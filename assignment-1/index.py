# Python 2.7.3

from __future__ import print_function
import sys
import re
import os
import collections
import time


class Index:
	def __init__(self, path):
		self.path = path
		self.doc_id = {}
		self.collection = collections.defaultdict(dict)

	# function to read documents from collection, tokenize and build the index with tokens
	def build_index(self):
		start = time.time()

		# generate document ids
		documents = os.listdir(self.path)
		for i, doc_name in enumerate(documents):
			self.doc_id[i] = doc_name

		for key, value in self.doc_id.items():
			# read documents
			document = open(self.path + "/" + value, "r")

			# clean text & split words
			file_text = document.read().lower()
			words = re.sub('[^A-Za-z\n ]+', '', file_text).split()

			# add each word to collection
			for i, word in enumerate(words):
				if key in self.collection[word].keys():
					self.collection[word][key].append(i)
				else:
					self.collection[word][key] = [i]

		end = time.time()
		print("Index built in", '{:.20f}'.format(end - start), "seconds")

	# function for identifying relevant docs using the index
	def and_query(self, query):
		print("\nResults for the Query:", " AND ".join(query))

		start = time.time()

		# query each term and add to results
		for i, term in enumerate(query):
			if i > 0:
				# merge next list with result
				result = self.merge_lists(result, self.collection[term].keys())
			else:
				# add first list to result
				result = self.collection[term].keys()

		end = time.time()

		# print document names
		print("Total Docs retrieved:", len(result))
		for doc_id in list(result):
			print(self.doc_id[doc_id])
		print("Retrieved in", '{:.20f}'.format(end - start), "seconds")

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
		for key, value in self.doc_id.items():
			print("Doc ID:", key, "==>", value)

	@staticmethod
	def merge_lists(list1, list2):
		list1.sort()
		list2.sort()
		i, j = 0, 0
		merged = []
		while i < len(list1) and j < len(list2):
			if list1[i] == list2[j]:
				merged.append(list1[i])
				i += 1
				j += 1
			elif list1[i] > list2[j]:
				j += 1
			else:
				i += 1
		return merged


obj = Index("./collection")

print('\n>>> Build Index')
obj.build_index()

print('\n>>> Print Document List')
obj.print_doc_list()

print('\n>>> Print Dictionary')
obj.print_dict()

print('\n>>> AND Query')

# sample queries
obj.and_query(["army"])
obj.and_query(["army", "germany"])
obj.and_query(["army", "germany", "britain"])
obj.and_query(["army", "germany", "britain", "nuclear"])
obj.and_query(["army", "germany", "britain", "nuclear", "leader"])
