from student import Student

_block_schedule = []
_students = []
_sh_sessions = []


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
        _block_schedule, students_parsed = read_csv_data(filename)

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
        return f"Error: File '{filename} not found"
    except Exception as e:
        return f"Error reading student data: {e}"




def read_sections(filename: str) -> str:
    global _sh_sessions

    try: 
        with open(filename, 'r') as f:
            lines = f.read().strip().split('\n')

        sessions = lines[1:]
        sections_parsed = []

        for i, line in enumerate(sessions):
            sessions[i] = line.split(',')

            internal_class_id = sessions[i][0]
            class_id = sessions[i][1]
            description = sessions[i][2]
            grading_periods = sessions[i][-1]

            sections_parsed.append([internal_class_id, class_id, description, grading_periods])

        sh_sessions = []

        for section in sections_parsed:
            class_ID = section[1]
            blocks = class_ID[-4:] #prints the last 4 characters
            sh_sessions.append(blocks)

        _sh_sessions = sh_sessions

        return f"Successfully loaded {len(_sh_sessions)} study hall sessions"
    
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"Error reading section data: {e}"



#for testing
if __name__ == "__main__":

    path = '/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/data/Study Hall Free Blocks Clean.csv'
    block_schedule, students_parsed = read_csv_data(path)
    print(read_sections('/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/data/Spring Study Hall Sessions.csv'))
    print(read_students(path))



    print(block_schedule)
    print('---')
    print(students_parsed[0])
    print('---')
    print(len(students_parsed))
    print('---')
    print(_sh_sessions)


    










