class min_heap:
    def __init__(self):
        self.heap = []

    def parent(index: int):
        return (index-1) // 2

    def children(index: int):
        return 2*index + 1, 2*index + 2


    #Implement the missing portions of the push and pop methods to maintain the structure of the heap.
    def push(self, value):
        self.heap.append(value)

        #bubbling up to be implemented
        current_index = len(self.heap) - 1
        parent_index = min_heap.parent(current_index)

        while self.heap[current_index] < self.heap[parent_index]:
            self.heap[current_index], self.heap[parent_index] = self.heap[parent_index], self.heap[current_index]
            current_index = parent_index
            parent_index = min_heap.parent(current_index)


    def pop(self):

        def get_smaller_children(c1_index: int, c2_index: int):
            which = None
            if self.heap[c1_index] < self.heap[c2_index]:
                which = c1_index
            else:
                which = c2_index
                
            return which


        ret = self.heap[0]
        self.heap[0] = self.heap.pop()  #move last leaf to root
        #bubbling down to be implemented

        #we should change the below and write a dedicated bubble down method
        current_index = 0
        c1_index, c2_index = min_heap.children(current_index)


        which = get_smaller_children(c1_index,c2_index)
        while self.heap[current_index] > self.heap[which]:
            if which == c1_index:
                self.heap[current_index], self.heap[c1_index] = self.heap[c1_index], self.heap[current_index]
                current_index = c1_index
                c1_index, c2_index = min_heap.children(current_index)
                which = get_smaller_children(c1_index, c2_index)
            
            else:
                self.heap[current_index], self.heap[c2_index] = self.heap[c2_index], self.heap[current_index]
                current_index = c2_index
                c1_index, c2_index = min_heap.children(current_index)
                which = get_smaller_children(c1_index, c2_index)

        return ret

    def pushPop(self, val): #this effectively is necessary because when you push a new value it might be popped
        if val < self.heap[0]:
            pop = self.heap.pop(0)

            self.heap[0] = val
            min_heap.bubble_down() #needs to write the bubble down
            return pop


