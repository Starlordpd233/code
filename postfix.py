from collections import deque

postfix = [2,3,'+',4,'*',6,'+']
stack = deque()

for i, object in enumerate(postfix):
    
    if type(object) == int:
        stack.append(object)

    elif object == '+':
        o1 = stack.pop()
        o2=stack.pop()

        stack.append(o1+o2)
    elif object == '*':
        o1 = stack.pop()
        o2=stack.pop()

        stack.append(o1*o2)
    
print(stack[-1])

