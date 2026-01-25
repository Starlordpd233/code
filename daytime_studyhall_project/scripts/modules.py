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


def compute_sh_section_demand(students, sh_sections) -> dict:
    
    for s in students:
        availabilities = list(b for b in s.free_blocks if b in sh_sections)
        
        for avail in availabilities:
            sh_sections[avail]["demand"] += 1



def sort_sh_sections(sh_sections: dict) -> dict:
    priority = {2:0, 4:0, 1:1}
    
    return sorted(sh_sections.keys(),
    key=lambda block: (
        sh_sections[block]["demand"],
        priority[block.which_block()],
        block.day,
        block.block
    ))



def get_valid_candidates(student, sh_sections, max_capacity):

    candidates = []

    for avail in student.availability:
        if sh_sections[avail]["num_of_students_in_here"] >= max_capacity:
            continue
        if not all(avail.get_distance(scheduled) > 1 for scheduled in student.scheduled_sh):
            continue

        candidates.append(avail)
    
    return candidates


def pick_best_section(candidates, sh_sections):
    if not candidates:
        return None

    priority = {2:0, 4:0, 1:1}

    return min(candidates, key=lambda block: (
        sh_sections[block]["demand"],
        priority[block.which_block()],
        sh_sections[block]["num_of_students_in_here"]
    ))

