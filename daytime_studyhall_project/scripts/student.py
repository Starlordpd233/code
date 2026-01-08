from modules import find_freeBlocks #I don't need the other two methods in this script since I think I will import them in the main.py script

'''
Project Description:
Your first task in working toward a functional study hall project is to get the Free Period CSV read into your program. Because this project has an object-oriented focus, you should design and create a Student class. A student object should have at minimum the following functionality:

Create a student object from some form of entry data (a CSV line as a string, a list of values, etc)
A method that returns a boolean value of whether or not a student is free in a specific block
Once scheduled, a method that returns a list of their scheduled study halls. Pre-scheduling, it could be an empty list, a None, or a False -- up to you.
A method that indicates whether or not a given student should be scheduled for more study halls.
A __str__ method that prints the student information in a useful way.
Any helper methods necessary for you to accomplish this.
Remember to avoid data duplication (think: why?). This portion of the project should read in the CSV and create a collection (list, dictionary, etc) of Student objects. Output them in some way to be sure it has worked correctly.

Note that you should read the file as plain text to have practice parsing data -- packages that do it for you should not be used.
'''

class Student:
    def __init__(self, name, grade, free_blocks):
        self.name = name
        self.grade = grade

        self.free_blocks = set(free_blocks) #fast lookup

        self.scheduled_sh = [] #iniaties for now as placeholder for future schedule study hall (sh)
    
    def get_freeBlocks(self, student_block_schedule):
        freeBlocks = find_freeBlocks(student_block_schedule)
        self.free_blocks.update(freeblock for freeblock in freeBlocks)

    
    def is_free(self, block):
        #block is a specific block, and I'm not sure if we're given directly the string in the form, ex. 'D5B2'
        return block in self.free_blocks

    def needs_sh(self):
        if len(self.free_blocks) <= 1: #if anyone has only 1 free, they don't need sh
            return False
        else:
            if self.grade == 'Grade 9':
                if len(self.free_blocks) >= 3: 
                    return True
            else:
                if len(self.free_blocks) >= 2:
                    return True

    def add_sh(self, sh_block): 
        #requires the sh_block to be in the exact format of 'DxBx'
        if self.needs_sh() and sh_block not in self.scheduled_sh:
            self.scheduled_sh.append(sh_block) 

    def __str__(self):
        return f"""Name: {self.name}
        Grade: {self.grade}
        Free Blocks: {self.free_blocks}
        Scheduled Study Hall Sessions: {self.scheduled_sh}"""
