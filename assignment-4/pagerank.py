# Python 3.0
import re
import collections
import operator


class PageRank:
	def __init__(self):
		self.alpha = 0.15
		self.precision = 100

	# function to implement PageRank algorithm
	# input_file - input file that follows the format provided in the assignment description
	def page_rank(self, input_file):
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
					transition_matrix[i][j] = 1/page_count

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


i = PageRank()
i.page_rank("test1.txt")
i.page_rank("test2.txt")
i.page_rank("test3.txt")
i.page_rank("test4.txt")
