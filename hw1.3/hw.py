'''
For homework, finish the problem we started in class. We will then flip it around a bit on Wednesday.

Create a 100 x 100 2D list. Read from a file data in the following format:

5 12 93
73 15 8
...
where each line contains a row index, followed by a column index, followed by a value that should go in that position in the list. Put the values in the appropriate locations in the list. You may assume the indices are valid. Think through the following questions:

a) If I have n lines in my file that fit into an mxm grid, what is the time complexity of getting this grid set up?

O(m^2 + n)

b) How would this problem change if I didn't know in advance the size of the grid?

You would have to first find the maximum row and column indices from the file, and then create a grid from there. The time complexity
would be more than what we had. I'm interested in how we can find the max in the fastest way.
'''

def sort_2d_list(input_file) -> list:

    grid = [[0 for _ in range(100)] for _ in range(100)]

    with open(input_file, 'r') as file:
        for line in file:
            listy = line.strip().split()

            row, col, val = map(int, listy)
            grid[row][col] = val

    return grid

if __name__ == "__main__":
    grid = sort_2d_list("/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/hw1.3/test_data.txt")
    print(grid)


'''
Sparse Array: keeping a dictionary instead of a complete grid, when n is smaller in magnitude than m. 
'''
    

        