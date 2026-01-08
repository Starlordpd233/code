

def read_csv_data():

    csv_path = "/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/data/Study Hall Free Blocks Clean.csv"
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        lines = f.read().strip().split('\n')
        
        #handles the header first
        header = lines[0].split(',')
        block_schedule = header[2:] #first result

        #now students
        lines_of_students = lines[1:]
        students_parsed = []
        for i, line in enumerate(lines_of_students):
            lines_of_students[i] = line.split('",')
            
            lines_of_students[i][0] = lines_of_students[i][0].replace('"', '')
            lines_of_students[i][1] = lines_of_students[i][1].split(',', maxsplit=1) #finds the comma righ tafter the grade and split there
            
            name = lines_of_students[i][0]
            grade = lines_of_students[i][1][0]
            free_blocks = lines_of_students[i][1][1]
            students_parsed.append([name,grade,free_blocks]) #second result
    
    return block_schedule, students_parsed


def parse_blocks(students:list): #returns a list of free blocks of each student in one list
    blocks_for_all_students = [student[2] for student in students]

    for i in range(len(blocks_for_all_students)):
        blocks_for_all_students[i] = blocks_for_all_students[i].split(',')

    return blocks_for_all_students

    #at this point, each element in the list of each student's block schedule matches in index with the 28 blocks



def find_freeBlocks(blocks, student_block_schedule: list): #for one student

    free_blocks = []

    if len(blocks) == len(student_block_schedule): #just double check to make sure index will match and that student schedule is valid
        for i in range(len(student_block_schedule)):
            if student_block_schedule[i] == '1':
                free_blocks.append(blocks[i])

    return free_blocks




if __name__ == "__main__":
    #for testing
    block_schedule, students_parsed = read_csv_data()
    print(block_schedule)
    print('---')
    print(students_parsed[0])


    










