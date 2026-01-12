

class Block:
    def __init__(self, block_str):
        self.day = int(block_str[1])
        self.block = int(block_str[-1])

    
    def which_block(self):
        #returns which block of the day (1st, 2nd, ... ) the block is
        #essentially we're just checking how much over the block is relative to the day, and so everytime we mod 7 that should increase the count
        if self.day <= self.block:
            return (self.block - self.day) + 1
        else:
            count = 0
            start = self.day
            while start%7 != self.block:
                start += 1
                count += 1

            return count + 1
            
    def get_distance(self, other) -> int: #returns 1, 2, 3, or 4
        seq = [1, 5, 2, 6, 3, 7, 4] #hardcoded sequence of the schedule

        self_index = seq.index(self.day)
        target_index = seq.index(other.day)
        
        return (target_index - self_index) % len(seq)
    
    def __eq__(self, other) -> bool: #needs this so that python knows how to compare different block objects and see if they're identifical
        if not isinstance(other, Block):
            return NotImplemented
        
        return self.day == other.day and self.block == other.block

    def __hash__(self) -> int: #for sets to work
        return hash((self.day, self.block))
    
    def __str__(self):
        return f"D{self.day}B{self.block}"

        
    



