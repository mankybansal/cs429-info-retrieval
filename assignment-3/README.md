# Assignment 3 - Relevance Feedback
Mayank Bansal<br>
A20392482<br>
mbansal5@hawk.iit.edu


### Running Program

The program by default runs user feedback with Rocchio. Comment the following lines to run pseudo-relevance

```
query = input("Query to search: ")
k_docs = int(input("Number of (top) results: "))

obj.run_rocchio(query, k_docs)
```

Uncomment the following lines to run pseudo-relevance:

```
#########################################
#                                       #
#  Uncomment this for Pseudo Relevance  #
#                                       #
#########################################

query_ids = [46, 54, 27]
for query_id in query_ids:
	obj.run_pseudo_relevance(query_id, 10)

old_map = 0
for map in obj.old_maps:
	add = 0
	for item in map:
		add += item
	add /= len(map)
	old_map += add
old_map /= len(obj.old_maps)

print("\nWithout Rocchio MAP:", old_map)

new_map = 0
for i in range(0, 3):
	new_map = 0
	for j in range(0, len(query_ids)):
		add = 0
		for map in obj.new_maps[j * 3 + i]:
			add += map
		add /= len(obj.new_maps[j * 3 + i])
		new_map += add
	new_map /= len(query_ids)
	print("With Rocchio MAP,", (i+1), "iteration(s):", new_map)


```

`NOTE:` THE PROGRAM USES THE QUERY ID's STARTING FROM 0. If the query you want to use is #60, then put in 59 in that array.

### Rocchio Algorithm

```
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

```

### Rocchio Input

```
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
```

### Pseudo-relevance

```
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
```