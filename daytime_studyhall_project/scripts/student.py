from block import Block

def find_freeBlocks(block_schedule: list, student_block_schedule: list) -> list: #for one student

    free_blocks = []

    if len(block_schedule) == len(student_block_schedule): #just double check to make sure index will match and that student schedule is valid
        for i in range(len(student_block_schedule)):
            if student_block_schedule[i] == '1':
                free_blocks.append(block_schedule[i])

    return free_blocks


class Student:
    def __init__(self, id, name, grade):
        self.id = id
        self.name = name
        self.grade = int(grade[6:])

        self.free_blocks = set() #fast lookup

        self.availability = []
        self.scheduled_sh = [] #iniaties for now as placeholder for future schedule study hall (sh)
        self.notes = []
    

    def set_freeBlocks(self, block_schedule, student_block_schedule):
        freeBlocks = find_freeBlocks(block_schedule, student_block_schedule)
        self.free_blocks.update(freeblock for freeblock in freeBlocks)

    
    def is_free(self, block: Block): #i don't think I'm using this
        #block is a specific block, and I'm not sure if we're given directly the string in the form, ex. 'D5B2'
        return block in self.free_blocks

    def needs_sh(self):
        if self.grade == 9:
            target = 2
        else:
            target = 1
        
        numberOF_current_sh = len(self.scheduled_sh)
        numberOF_remaining_free = len(self.free_blocks) - numberOF_current_sh

        return numberOF_current_sh < target and numberOF_remaining_free > 1


    def set_availability(self, ordered_sh_sections: list):

        self.availability = [sh for sh in ordered_sh_sections if sh in self.free_blocks]

    def add_sh(self, sh_block): 
        if self.needs_sh() and sh_block not in self.scheduled_sh:
            self.scheduled_sh.append(sh_block) 
            return True
        else:
            return False
    
    def can_move_out(self, block_currently_in, sh_sections, max_ppl_per_sh):#determines whether this student can be moved out from the current scheduled sh block to some other available alternatives

        fallback = None

        if not block_currently_in in self.scheduled_sh: #confirms if the student is actually in this sh or not
            return (False, None)
        else:
            # does the student have any other availabilities?
            alternatives = [b for b in self.availability if b not in self.scheduled_sh]

            if alternatives:
                for alt in alternatives:
                    if sh_sections[alt]["num_of_students_in_here"] < max_ppl_per_sh and all(alt.get_distance(scheduled) > 1 for scheduled in self.scheduled_sh if scheduled != block_currently_in):
                        if alt.which_block() in [2,4]:
                            return True, alt #prefers blocks 2/4
                        
                        if fallback is None:
                            fallback = alt #if not, 1st block

                if fallback is not None:
                    return (True, fallback)
                
                return (False, None)

            else:
                return False, None #no alternatives


    def __str__(self):
        return f"""Name: {self.name}
Grade: {self.grade}
Free Blocks: {[str(b) for b in self.free_blocks]}
Potential SH Availability: {[str(b) for b in self.availability]}
Scheduled Study Hall Sessions: {[str(b) for b in self.scheduled_sh]}
Notes: {[str(b) for b in self.notes]}"""

