"""
BFS: breathf-first search gives you the optimal (shortest path)
DFS: depth-first search will determine for you whether there is a path (solution) or not at all

visited: set()
frontier: deque()


# Dandelions Maze — BFS Practice Problem (Queues/Deques)

## Why we’re tweaking your original goal

Your original assignment (right/down only, maximize total dandelions) is naturally **DFS/backtracking** or **dynamic programming** because the grid is a directed acyclic graph. If you instead allow maze-like movement (4 directions), “maximize total dandelions” becomes tricky: you’d need extra rules (no revisiting, or a step limit), and it stops being what BFS is best at.

So this practice problem is designed so **BFS is the right tool**, while still caring about “most dandelions.”

---

## Problem statement

Write a function:

* `def search(grid):`

where `grid` is a 2D list of ints.

* `grid[r][c] == -1` means the cell is blocked.
* Otherwise `grid[r][c]` is the number of dandelions you collect when you step on that cell.

You start at `(0,0)` and want to reach `(rows-1, cols-1)`.

### Movement

From `(r,c)` you may move **one step** to any of the four neighbors:

* up `(r-1,c)`
* down `(r+1,c)`
* left `(r,c-1)`
* right `(r,c+1)`

(Only in-bounds, and not blocked.)

### Goal

Return the **maximum total dandelions you can collect among all *shortest* paths** from start to goal.

* “Shortest” means **fewest steps** (edges), not biggest sum.
* If the goal is unreachable, return `None`.

> This is a classic BFS-friendly twist: BFS finds shortest distances, and then we optimize dandelions *within that distance layer*.

---

## What you must use

* `frontier`: a `collections.deque`
* `visited`: a `set()` **(plus** one extra structure to handle the “max dandelions among shortest paths” tie-break)

---

## Example

Given:

```text
grid = [
  [5, 1, -1, 4],
  [2, 0, 10, 1],
  [1, -1, 2, 2],
  [0, 3, 1, 7]
]
```

* The shortest path length is 6 steps.
* Among those shortest paths, the maximum dandelions is **28**.

So `search(grid)` returns:

```text
28
```

---

## State representation (what goes in the frontier)

Each frontier element should store enough to continue the search.

Minimum recommended state:

* `(r, c, steps, total)`

(You *can* store a path too, but it makes things slower. For this practice, don’t store the path unless you do the “extension.”)

---

## Visited: why a plain set is not enough

If you use `visited = {(r,c)}` like normal BFS, you might throw away a later-arriving path that reaches the same cell in the **same number of steps** but with **more dandelions**.

So you need an extra bookkeeping idea.

### Suggested approach

Use:

* `visited` as a set of `(r,c,steps)` states you’ve already enqueued/processed, **and**
* `best_total[(r,c,steps)] = maximum total dandelions seen for that exact (cell,step-count)`

That lets you revisit the same cell **only** when it’s still within the shortest-path layer you care about.

---

## BFS stopping rule (important)

In ordinary BFS, you can stop when you first reach the goal.

Here you **cannot** stop immediately, because another path might reach the goal in the **same number of steps** but with more dandelions.

So:

1. Record the step-count `goal_steps` the first time you reach the goal.
2. Keep processing frontier states with `steps == goal_steps`.
3. Track the maximum `total` among those goal hits.
4. Stop when you are about to process states with `steps > goal_steps`.

---

## What your teacher’s code snippet is about

If your `frontier` is a `deque`:

* `popleft()` makes it behave like a **queue** (FIFO) → **BFS**
* `pop()` makes it behave like a **stack** (LIFO) → **DFS**

So the snippet:

```python
if self.mode == 'bfs':
    self.current = self.frontier.popleft()
else:
    self.current = self.frontier.pop()
```

is showing that **one container type (`deque`) can run either algorithm** depending on which end you remove from.

---

## Extension challenges (optional)

1. **Return both values:** return `(min_steps, max_dandelions_on_shortest_paths)`.
2. **Return a path:** also return one path that achieves the max (store parents, don’t store full paths in every state).
3. **DFS mode:** add a parameter `mode` in `search(grid, mode='bfs')` and allow DFS by switching pop direction.
4. **Deque practice:** implement “two-ended frontier” behavior (e.g., prioritize some moves by appendleft vs append) and observe how it changes exploration order.


from collections import deque

def bfs_shortest_steps(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if rows == 0 or cols == 0:
        return None

    # start/end blocked?
    if grid[0][0] == -1 or grid[rows - 1][cols - 1] == -1:
        return None

    start = (0, 0)
    goal = (rows - 1, cols - 1)

    frontier = deque([(0, 0, 0)])  # (r, c, dist)
    visited = {start}

    while frontier:
        r, c, dist = frontier.popleft()  # FIFO => BFS

        if (r, c) == goal:
            return dist  # first time reaching goal is shortest

        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc

            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] != -1 and (nr, nc) not in visited:
                    visited.add((nr, nc))          # mark when enqueuing
                    frontier.append((nr, nc, dist + 1))

    return None  # unreachable


"""

def search(grid: list):
    pass