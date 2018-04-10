# Python 3.0
import re
import collections
import operator
from random import *


class PageRank:
	def __init__(self):
		self.alpha = 0.15
		self.precision = 100

	# function to implement PageRank algorithm
	# input_file - input file that follows the format provided in the assignment description
	def page_rank(self, input_file):

		print("\nOutput for file", input_file)

		lines = open(input_file)

		page_count = int(lines.readline())
		edge_count = int(lines.readline())
		adjacency_matrix = [[0 for i in range(page_count)] for j in range(page_count)]
		transition_matrix = [[0 for i in range(page_count)] for j in range(page_count)]

		# for quick add
		link_counts = [0 for i in range(page_count)]

		for i in range(0, edge_count):
			pair = re.sub('[^0-9 ]+', '', lines.readline()).split(" ")
			src = int(pair[0])
			dst = int(pair[1])

			# for quick add
			if adjacency_matrix[src][dst] != 1:
				link_counts[src] += 1
			adjacency_matrix[src][dst] = 1

		print("\nAdjacency Matrix\n")

		for line in adjacency_matrix:
			print(line)

		for i in range(0, page_count):
			for j in range(0, page_count):
				if link_counts[i] != 0:
					transition_matrix[i][j] = adjacency_matrix[i][j] / link_counts[i]
				else:
					transition_matrix[i][j] = 1 / page_count

				transition_matrix[i][j] *= (1 - self.alpha)
				transition_matrix[i][j] += self.alpha / page_count
				transition_matrix[i][j] = round(transition_matrix[i][j], self.precision)

		x_old = [round(1 / page_count, self.precision) for i in range(page_count)]
		x_new = [0 for i in range(page_count)]

		print("\nTransition Matrix\n")

		for line in transition_matrix:
			print(line)

		print("\nInit State\n")
		print(x_old, "\n")

		while 1:
			for i in range(0, page_count):
				x_new[i] = 0
				for j in range(0, page_count):
					x_new[i] += x_old[j] * transition_matrix[j][i]

				x_new[i] = round(x_new[i], self.precision)

			print(x_new)

			if x_new == x_old:
				break
			else:
				x_old = list(x_new)

		print("\nFinal Page Ranks\n")
		print(x_new)

		ranking = collections.defaultdict(list)
		for i in range(0, page_count):
			ranking[x_new[i]].append(i)

		sorted_ranking = list(reversed(sorted(ranking.items(), key=operator.itemgetter(0))))
		print(sorted_ranking)

		print("\nRanking\n")
		for k, v in enumerate(sorted_ranking):
			print("#", k + 1, v)

	# function to run random tests
	def test_random(self, max_n):

		page_count = randint(1, max_n)
		edge_count = randint(0, page_count * page_count)

		edge_list = []

		for i in range(0, edge_count):
			src = randint(0, page_count - 1)
			dst = randint(0, page_count - 1)

			edge = [src, dst]

			if edge not in edge_list:
				edge_list.append(edge)

		edge_count = len(edge_list)

		test_file = open("tests/test_random.txt", "w")

		test_file.write("%d\n" % page_count)
		test_file.write("%d\n" % edge_count)
		for edge in edge_list:
			test_file.write("%d %d\n" % (edge[0], edge[1]))

		test_file.close()

		print("Page Count: ", page_count)
		print("Edge Count: ", edge_count)

		self.page_rank("tests/test_random.txt")


i = PageRank()

###################
#                 #
#  Sample Test 1  #
#                 #
###################

# i.page_rank("tests/test1.txt")

###################
#                 #
#  Sample Test 1  #
#                 #
###################

# i.page_rank("tests/test2.txt")

#################################
#                               #
#  Sample Test 3 - From Slides  #
#                               #
#################################

# i.page_rank("tests/test3.txt")

###############################
#                             #
#  Sample Test 3 - Arbitrary  #
#                             #
###############################

# i.page_rank("tests/test4.txt")

###################################################################################
#                                                                                 #
#  Uncomment this for Random Testing                                              #
#                                                                                 #
#  test_random(int max_n) where max_n is the maximum range for random page count  #
#  for quick tests, keep max_n < 100                                              #
#  this function has been tested for max_n = 1000 (2-3 minutes running time)      #
#                                                                                 #
###################################################################################

i.test_random(300)
