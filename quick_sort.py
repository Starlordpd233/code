'''
choose a pivot
separate 
recurse
worst case is O(n^2) (the pivot happens to be the smallest value or the biggest value) and typically O(nlogn)

basically finds a pivot, move it into its right space by imagining splitting the list into two sides with this pivot value sitting in the middle which is its correct space. Then, now there are two separate sublists on each side, and you will find a respective pivot value from those sublists, and move the pivot into their correct spaces, and goes on until you have used all the pivots (length of list -1 is the number of times you'd have to choose the pivot?)
'''

#needs an example of this to practice