'''Write a method called attendance that takes in a list of names in the class and a parallel list of string symbols 
('P' for present, 'X' for absent, 'T' for tardy) and returns a list of students who were in class that day, 
with a * added to the end of names of students who were tardy. You may assume that the lists are the same length 
and that the mark at index i is for the student also at index i.'''

def attendance(names: list, status:list) -> list:
    if len(names) == len(status):
        ret = [names[i] + '*' for i in range(len(status)) if status[i] != "X"]
    
    return ret


'''
Write a method called counts that takes in a (long) list of values between 1 and 10 and returns an array 
where index i contains the number of times i appeared in the parameter list. 
Note that you may NOT use the built-in count method for lists or anything similar.

What would you have to change in order to be able to handle ANY possible range of values with minimal wasted space?
It would be easier to write this code using the built-in count method. Why would I NOT want to do that?
'''
import array as arr

def counts(values:list) -> arr.array:
    ret = arr.array('i', [0 for _ in range(10)])

    for i in range(1, 11):
        for j in range(len(values)):
            if i == values[j]:
                ret[i] += 1

    return ret


#insight here: the number we're counting is the index where we store it's count

def counts_2(values:list) -> arr.array:
    ret = arr.array('i', [0 for _ in range(10)])
    for val in values:
        ret[val] += 1
    
    return ret

'''
Write a method that takes in a list of integers and returns the largest-sum subset of 3 consecutive values as its own list. 
Ie find the set of 3 consecutive values with the largest sum and return them in a new list. 
You may not use the sum method to accomplish this.

Now, write another version of this method that also takes in the size of the resulting list you want. 
So I could ask it to find the largest-sum set of 5 or 10 or 100 consecutive values.
'''

def largest_sum_consecutive_3(values:list) -> list:

    #[1,3,5,2,4,8,103,3,20,104]

    max_sum = values[0] + values[1] + values[2]

    pos = 0

    if len(values) >= 3:
        for i in range(len(values) - 2):
            sum = values[i] + values[i+1] + values[i+2]
            if sum > max_sum:
                max_sum=sum
                pos = i
        
    return values[pos:pos+3]

def largest_sum_part_two(values:list, size:int) -> list:

    initial = values[:size]
    max_sum = sum(initial)
    pos = 0

    if len(values) >= size:
        for i in range(len(values) - size + 1):
            current = values[i]
            for j in range(1, size):
                current += values[i+j]
            if current > max_sum:
                max_sum=sum
                pos = i
        
    return values[pos:pos+size]

    
