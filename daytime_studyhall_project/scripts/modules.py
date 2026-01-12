from student import Student
from block import Block

_block_schedule = []
_students = []
_sh_sections = {}


#Helper Functions
def read_csv_data(csv_path):

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        lines = f.read().strip().split('\n')
        
    #handles the header first
    header = lines[0].split(',')
    block_schedule = header[3:] #first result

    #now students
    lines_of_students = lines[1:]
    students_parsed = []

    for i, line in enumerate(lines_of_students):
        lines_of_students[i] = line.split('",')
        
        #lines_of_students[i][0] = lines_of_students[i][0].replace('"', '')
        lines_of_students[i][0] = lines_of_students[i][0].split(',"')
        person_id = lines_of_students[i][0][0]
        name = lines_of_students[i][0][1]

        lines_of_students[i][1] = lines_of_students[i][1].split(',', maxsplit=1) #finds the comma righ tafter the grade and split there
        
        grade = lines_of_students[i][1][0]
        free_blocks = lines_of_students[i][1][1]
        students_parsed.append([person_id,name,grade,free_blocks]) #second result
    
    return block_schedule, students_parsed




def parse_blocks(students:list): #returns a list of blocks of each student in one list containing '' (None) or '1'
    blocks_for_all_students = [student[3] for student in students]

    for i in range(len(blocks_for_all_students)):
        blocks_for_all_students[i] = blocks_for_all_students[i].split(',')

    return blocks_for_all_students

    #at this point, each element in the list of each student's block schedule matches in index with the 28 blocks



#Public Functions
def read_students(filename: str) -> str:
    global _block_schedule, _students

    try:
        _students = [] #clears the lists
        _block_schedule = []


        block_schedule, students_parsed = read_csv_data(filename)
        for block in block_schedule:
            b = Block(block)
            if isinstance(b, Block):
                _block_schedule.append(b) #ordered list

        all_students_blocks = parse_blocks(students_parsed) #gets all the students blocks in one single list

        for i, student_data in enumerate(students_parsed):
            id = student_data[0]
            name = student_data[1]
            grade = student_data[2]

            student = Student(id, name, grade)

            student.get_freeBlocks(_block_schedule, all_students_blocks[i])

            _students.append(student)

        return f"Successfully loaded {len(_students)} students."

    except FileNotFoundError:
        return f"Error: File '{filename}' not found"
    except Exception as e:
        return f"Error reading student data: {e}"


def read_sections(filename: str) -> str:
    global _sh_sections
    _sh_sections = []

    try: 
        with open(filename, 'r') as f:
            lines = f.read().strip().split('\n')

        sections = lines[1:]

        for i, line in enumerate(sections):
            sections[i] = line.split(',')

            internal_class_id = sections[i][0]
            class_id = sections[i][1]
            description = sections[i][2]
            grading_periods = sections[i][-1]
            block = class_id[-4:]

            _sh_sections[Block(block)] = {
                "block": block,
                "internal_class_id": internal_class_id,
                "class_id": class_id,
                "description": description,
                "grading_periods": grading_periods,
                "num_of_students_in_here": 0 #initializes the count here
            }

            #sections_parsed.append([internal_class_id, class_id, description, grading_periods])


        return f"Successfully loaded {len(_sh_sections)} study hall sessions"
    
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"Error reading section data: {e}"


def schedule():
    global _students, _sh_sections, _block_schedule
    max_per_sh_ppl = 35 #can change this later if needed

    if not _students:
        return "Error: No student data loaded"
    if not _sh_sections:
        return "Error: No study hall section loaded"
    
    
    


#for testing
if __name__ == "__main__":

    path_studentInfo = '/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/data/Study Hall Free Blocks Clean.csv'
    path_sh_sections = '/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/data/Spring Study Hall Sessions.csv'
    
    block_schedule, students_parsed = read_csv_data(path_studentInfo)
    read_students(path_studentInfo)
    read_sections(path_sh_sections)

    print(_students[0])
    #print(read_sections('/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/data/Spring Study Hall Sessions.csv'))
    #print(read_students(path))



    print(_block_schedule)
    print('---')
    #print(students_parsed[0])
    #print('---')
    #print(len(students_parsed))
    #print('---')
    print(_sh_sections)

    student0 = students_parsed[0]
    student_test = Student(student0[0], student0[1], student0[2])
    #student_test = student_test.get_freeBlocks(_block_schedule)


    










