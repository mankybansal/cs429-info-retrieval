# Assignment 4 - Page Rank
Mayank Bansal<br>
A20392482<br>
mbansal5@hawk.iit.edu

## Executing
Run
```
python3 pagerank.py > output.txt
```

Uncomment out the testcase you want to run.

```test1.txt``` & ```text2.txt``` are given test cases.

```test3.txt``` is from the sample in the slides.

```test4.txt``` is a random testcase

### Saving to File
Redirecting using,

```
python3 pagerank.py > outputs/output.txt
```

For the random testing,

```
python3 pagerank.py > outputs/output_random.txt
```

will save the output to output.txt

## Random Testing
To run random tests, uncomment the following piece of code

```
###################################################################################
#                                                                                 #
#  Uncomment this for Random Testing                                              #
#                                                                                 #
#  test_random(int max_n) where max_n is the maximum range for random page count  #
#  for quick tests, keep max_n < 100                                              #
#  this function has been tested for max_n = 1000 (2-3 minutes running time)      #
#                                                                                 #
###################################################################################

i.test_random()

```