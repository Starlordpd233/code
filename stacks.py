'''
a stack of plates (data) from bottom to up; you only access the top plate and don't mess with the ones below
last in, first out: the
push: add a value to the top
pop: remove value from the top 
peek/top: peek at the top element and access it without removing it
empty: tells whether or not the stack is empty; bool
useful for nesting & branching: 

---
---
---
---
---


The call stack:

def a():
    do something
    b()

def b():
    do sth
    return val

def main():
    x = 5
    a()
    ret


A list object in python is perfect for a stack
push: O(1)
pop: O(1)
peak: O(1)
empty: O(1)

'''

def check(str): #only () and [] are counted
    stack = []

    for s in str:
        if s in ['(', '[']:
            stack.append(s)
        
        elif s == ')' and len(stack) > 0 and stack[-1] == '(':
            stack.pop()

        elif s == ']' and len(stack) > 0 and stack[-1] == '[':
            stack.pop()
    
    return True if len(stack) == 0 else False