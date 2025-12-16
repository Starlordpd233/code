from CarSimTools import *

grid = Grid()
# test case from notes: start (2,1) goal (0,3)
start_row, start_col = 2, 1
goal_row, goal_col = 0, 3

dir_seq = grid.compute_direction_sequence(start_row, start_col, goal_row, goal_col)
print("Direction sequence:", dir_seq)
print("Length:", len(dir_seq))

# compute future path with start_tick=0
path = grid.compute_future_path(start_row, start_col, goal_row, goal_col, start_tick=0)
print("Future path (row, col, tick):", path)
print("Path length:", len(path))

# Check that each direction moves toward the next position
current_row, current_col = start_row, start_col
for i, (d, (r, c, t)) in enumerate(zip(dir_seq, path)):
    # compute expected next position based on direction
    if d == 0:  # up
        expected = (current_row - 1, current_col)
    elif d == 1:  # down
        expected = (current_row + 1, current_col)
    elif d == 2:  # left
        expected = (current_row, current_col - 1)
    elif d == 3:  # right
        expected = (current_row, current_col + 1)
    if (r, c) != expected:
        print(f"Mismatch at step {i}: direction {d} from ({current_row},{current_col}) expected {expected}, got ({r},{c})")
    current_row, current_col = r, c
print("Consistency check done.")