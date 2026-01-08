'''
for some restricted dataset that you know the cap for, behaves like numbers, and smaller pieces and ordered significance 

ex. 5 digits max (like zip codes). Sorts the last digit, then the second digit, ..., then the most significant digit. Each layer maintains the relative order from the previous when there are same digit

O(mn), where m is the number of digits and n is the number of values in the list
'''