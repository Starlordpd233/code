
def blurring_pixels(grid:list):

    new_grid = [None]

    for r in range(len(grid)):
        for c in range(len(grid[i][j])):
            loc = grid[r][c]

            up = r-1
            down = r+1
            left = c-1
            right = c+1

            sum = 0
            count = 0

            for i in range((max(0, r-1)), min(r+2, len(grid)):
                for c in range(max(0, c-1), min(c+2, len(grid[i]))):
                    #do the average here


