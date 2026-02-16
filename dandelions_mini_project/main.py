"""
Lucas Seyboth loves to pick dandelions in the spring. The Meadows, which have many dandelions, can be modeled using a SIZE X SIZE 2D list of ints where the number in a given location is how many dandelions are in that patch of grass. Of course, some areas are not safe to walk (the pond, for example). Such locations would be marked with a -1. Assume Lucas wants to make his way from location (0,0) to the opposite side of the Meadows (SIZE-1, SIZE-1). Each step should take him in generally the right direction (so should be down or right), and he wants to know what the maximum number of dandelions he can pick would be.

Write a program which, given a 2-dimensional list of values, finds and prints the optimal number of dandelions Lucas can pick. Note that it will NOT need to report the path taken to achieve that number of dandelions. However, for the sake of practice, we will document the path (list of coordinates) here as well.

Hint: use a stack. If there is only one way to proceed from the current position, go there and update the total number of accumulated dandelions. If there are two ways to proceed, save one of them (and its total dandelions up to that point) onto the stack and proceed the other direction. If you have reached the lower-right corner, update the maximum. If there is nowhere possible to go, pop a saved point (if there is one), and continue onward.

Hint: you need to store a location and a value together in the stack -- you can do that using an object type you create or a tuple/list.

Starter code to create the field is available here: DandelionsStarter-1.py Download DandelionsStarter-1.py. You should use the first version of field (where the answer is known) to debug your code, then switch to the randomly generated field and see how it does.

Once you have your code working, submit it as well as answers to the following questions:

1) How would you have to redesign your code if the requirement was to provide both the pathway AND the maximum number of dandelions? Note that I'm not looking for code -- just a thoughtful description.

---------------------------------------------------
I didn't read this part before I wrote my code, so I actually already included the path in my tuple (each element in the stack) so that it records the coordinate each time we append a new element onto the call stack. To un-implement this, simply get rid of the path entry.

2) What is the worst-case time complexity of your code with n = SIZE? Support your answer.
For size = SIZE grid, we need R = (SIZE - 1) number of right moves, and D = (SIZE - 1) number of down moves. So the total number of moves needed, T = 2 * (Size - 1)

For the worst case, we have to choose at every single node and remember one and proceed to the other. I think the math here is that we're choosing which D (or R) moves to put out of all T moves, so it's a combination problem of T choose D (or T choose R, same thing here). The formula for that is T! / (R! * (D-R)!). To estimate the long term behavior for that, I used Stirling's approximation and graphed it on desmos and it looks like it's approximately 4^n, where n = SIZE. 

At each call in the stack, my code pops from the stack (O(1)), check goal O(1), get neighbords O(1), and copy path list O(n), but these don't seem to play a big role in the big O notation since the 4^n dominates. So I think the time complexity here is simply the total number of paths possible, which is O(4^n) or O(4^SIZE).

---------------------------------------------------

It's extremely slow compared to George's. Not sure why. Can be optimized somehow.

"""

import random
from turtle import down

SIZE = 10

def print_grid(f):
    for row in f:
        for val in row:
            print(f'{val}\t', end='')
        print()

#field for debugging purposes: answer is 37
field = [[5, 8, -1, 3, 20],
        [-1, 2, 5, 0, 15],
        [4, 9, -1, 2, 6],
        [2, 0, 3, 1, -1],
        [3, 4, 1, 2, 6]]

#code to randomly generate the field

random_field = [[int(random.randrange(0,400)**.5) for i in range(SIZE)] for j in range(SIZE)]

for r in range(SIZE):
    for c in range(SIZE):
        if r + c > 0 and r + c < 2*(SIZE-1) and random.random() < .1:
          random_field[r][c] = -1


print_grid(field)


def dfs_max_dandelions(field: list) -> tuple:
    #I'm thinking that the return should be both the path and the max dandelions picked, but I'm not sure if a tuple is the best choice here.

    def get_valid_neighbors(r, c) -> list:
        valid_neighbors = []

        if c+1 < SIZE:
            right_neighbor = (r, c+1)
            if field[right_neighbor[0]][right_neighbor[1]] != -1:
                valid_neighbors.append(right_neighbor)
        if r+1 < SIZE:
            down_neighbor = (r+1, c)
            if field[down_neighbor[0]][down_neighbor[1]] != -1:
                valid_neighbors.append(down_neighbor)
        
        if valid_neighbors:
            return valid_neighbors
        else:
            return None
        

    GOAL = (SIZE-1, SIZE-1)

    if field[0][0] == -1 or field[GOAL[0]][GOAL[1]] == -1:
        return "Starting position or goal position is not valid"
    
    else:

        max_total = -1
        best_path = None
        current_total = field[0][0]
        path_so_far = [(0,0)]

        stack = [(0, 0, current_total, path_so_far)]

        while stack:
            r, c, total, path = stack.pop()

            if (r, c) == GOAL:
                if total > max_total:
                    max_total = total
                    best_path = path
                continue


            neighbors = get_valid_neighbors(r, c)

            if not neighbors:
                continue #continue to next iteration and pop the latest stack element
            
            if len(neighbors) == 1:
                (nr, nc) = neighbors[0]
                stack.append((nr, nc, total + field[nr][nc], path + [(nr, nc)]))
            
            else:
                #core logic
                #push both to stack but push the first one first before the second one (so we always explore the second one first)
                first_r, first_c = neighbors[0]
                second_r, second_c = neighbors[1]

                stack.append((first_r, first_c, total + field[first_r][first_c], path + [(first_r, first_c)]))
                stack.append((second_r, second_c, total + field[second_r][second_c], path + [(second_r, second_c)]))
    
    return max_total, best_path

total, path = dfs_max_dandelions(random_field)

print(total, path)


                
















