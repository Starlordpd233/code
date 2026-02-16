from collections import deque 
"""
First in, first out

     ---------------------
x -> xxxx................x ->
     ---------------------

All O(n):
add (to one end)
remove (from the other end)
empty? 
peek

Don't care about the middle people.

Buffer

Data type: deque
`from collections import deque`

`d = deque()`
works for both stack or queue

"""

#practice problems from handout
def reverse_front(q: deque, n:int) -> deque:
     stack = deque()
     ret = deque()

     if n > len(q):
          for i in range(len(q)):
               stack.append(q[i])
     else:
          for i in range(n):
               stack.append(q[i])

     while stack:
          ret.append(stack.pop())
     
     #to append the rest of the unchanged deque into ret
     if n < len(q):
          for i in range(n, len(q)):
               ret.append(q[i])

     return ret


d = deque([1,2,3,4,5,6,7])

print(reverse_front(d, 10))



def frequency(q: deque, s: str) -> int:
     #takes in a populated queue and a string s and returns the number of times string s appears in q. q should remain unchanged, and I cannot use auxiliary data structures, but I can use len(q) at any time.
     count = 0

     for _ in range(len(q)):
          pop = q.popleft()
          if pop == s:
               count += 1
          q.append(pop)
     return count


"""

"""

class Task:
     def __init__(self, description: str, days: int):
          self.description = description
          self.days = days
     
     def nextDay(self):
          if self.days > 0:
               self.days -= 1
     
     def dueToday(self):
          return self.days == 0
     
     def __str__(self):
          return f"Description: {self.description}   |   Due in: {self.days} days"
     
class ToDoList:
     def __init__(self):
          self.tasks = deque()
     
     def addTask(self, description, days):
          self.tasks.append(Task(description, days))
     
     def update_and_get_today(self):
          due_today = deque()
          original_lenth = len(self.tasks)
          count = 0 #to check whether or not we have checked every task in the original self.task deque

          while count < original_lenth: #the reason I'm not using directly len(self.tasks) is because it's changing when we're inside the loop
               pop = self.tasks.popleft()

               if pop.dueToday():
                    due_today.append(pop) 
                    count += 1
               else:
                    self.tasks.append(pop) #just append it to the right again.
                    count += 1

          return due_today
     
     def __str__(self):
          return f"To-Do List: {self.tasks}"




def next_greater(l:list) -> list:
     stack = deque([])
     ans = [-1] * len(l)

     for i, num in enumerate(l):

          while stack and num > l[stack[-1]]:
               j = stack.pop() #get the index from the stack
               ans[j] = num
          
          stack.append(i)
     return ans

def first_unique_char(s:str):

     candidates= deque([])
     count = {}

     for i, string in enumerate(s):
          count[string] += 1

          if count[string] == 1: 
               candidates.append(i)
          
          while candidates and count[s[candidates[0]]] > 1:
               candidates.popleft()
     
     return candidates[0] if candidates else -1


          









