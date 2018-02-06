# Assignment 1 - Boolean Retrieval
Mayank Bansal<br>
A20392482<br>
mbansal5@hawk.iit.edu

## Merge Algorithm

First we query each term from our collection and get all the keys for each term and add it to our initial unfiltered result. After the first list is added, we start merging the next list with the `merge_lists` function
```
# query each term and add to results
for i, term in enumerate(query):
    if i > 0:
        # merge next list with result
        result = self.merge_lists(result, self.collection[term].keys())
    else:
        # add first list to result
        result = self.collection[term].keys()
```

Here is the `merge_lists` function. This follows the basic intersecting of two post lists like the book.
```
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
```