

def find_freeBlocks(blocks, student_block_schedule: list): #for one student

    free_blocks = []

    if len(blocks) == len(student_block_schedule): #just double check to make sure index will match and that student schedule is valid
        for i in range(len(student_block_schedule)):
            if student_block_schedule[i] == '1':
                free_blocks.append(blocks[i])

    return free_blocks


class Student:
    def __init__(self, id, name, grade):
        self.id = id
        self.name = name
        self.grade = grade

        self.free_blocks = set() #fast lookup

        self.scheduled_sh = [] #iniaties for now as placeholder for future schedule study hall (sh)
    

    def get_freeBlocks(self, block_schedule, student_block_schedule):
        freeBlocks = find_freeBlocks(block_schedule, student_block_schedule)
        self.free_blocks.update(freeblock for freeblock in freeBlocks)

    
    def is_free(self, block):
        #block is a specific block, and I'm not sure if we're given directly the string in the form, ex. 'D5B2'
        return block in self.free_blocks

    def needs_sh(self):
        if self.grade == 'Grade 9':
            target = 2
        else:
            target = 1
        
        numberOF_current_sh = len(self.scheduled_sh)
        numberOF_remaining_free = len(self.free_blocks) - numberOF_current_sh

        return numberOF_current_sh < target and numberOF_remaining_free > 1


    def add_sh(self, sh_block): 
        #requires the sh_block to be in the exact format of 'DxBx'
        if self.needs_sh() and sh_block not in self.scheduled_sh:
            self.scheduled_sh.append(sh_block) 

    def __str__(self):
        return f"""Name: {self.name}
Grade: {self.grade[6:]}
Free Blocks: {self.free_blocks}
Scheduled Study Hall Sessions: {self.scheduled_sh}"""

