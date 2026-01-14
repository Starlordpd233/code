from student import Student
from block import Block
from modules import read_csv_data, parse_blocks, sort_sh_sections

_block_schedule = []
_students = []
_sh_sections = {}

#helpers
def update_sh_section(action, stu, block, sh_sections):
    if block not in sh_sections:
        return "invalid study hall block"
    section = sh_sections[block]

    if action == "add":
        if stu in section["list_of_students"]:
            return "student already in section"
        
        section["list_of_students"].append(stu)
        section["num_of_students_in_here"] += 1

        if block not in stu.scheduled_sh:
            stu.scheduled_sh.append(block)
        
        return "added"
    
    elif action == "remove":
        if stu not in section["list_of_students"]:
            return "student is not in the section"
            
        section["list_of_students"].remove(stu)
        section["num_of_students_in_here"] -= 1

        if block in stu.scheduled_sh:
            stu.scheduled_sh.remove(block)
        
        return "removed"
    
    return "failed"

def swap_and_move(stu_in, stu_out, block_of_swapping, destination_block_for_stu_out, _sh_sections):
    print(f"[SWAP] Moving {stu_out.name} from {block_of_swapping} to {destination_block_for_stu_out} to make room for {stu_in.name}")


    #move the student out first
    msg1 = update_sh_section("remove", stu_out, block_of_swapping, _sh_sections)
    msg2 = update_sh_section("add", stu_out, destination_block_for_stu_out, _sh_sections)

    #moves the waiting student in
    msg3 = update_sh_section("add", stu_in, block_of_swapping, _sh_sections)

    #add notes:
    stu_out.notes.append(f"Moved from {block_of_swapping} to {destination_block_for_stu_out} to make room for {stu_in.name}")
    stu_in.notes.append(f"Placed in {block_of_swapping} after bumping {stu_out.name}")

    return msg1, msg2, msg3


#Public Functions for UI
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

            student.set_freeBlocks(_block_schedule, all_students_blocks[i])

            _students.append(student)

        return f"Successfully loaded {len(_students)} students."

    except FileNotFoundError:
        return f"Error: File '{filename}' not found"
    except Exception as e:
        return f"Error reading student data: {e}"


def read_sections(filename: str) -> str:
    global _sh_sections
    _sh_sections = {}

    try: 
        with open(filename, 'r') as f:
            lines = f.read().strip().split('\n')

        sections = lines[1:]

        for i, line in enumerate(sections):
            sections[i] = line.split(',')


            #todo: this depends on order and might be suboptimal
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
                "list_of_students": [],
                "num_of_students_in_here": 0 #initializes the count here
            }


        return f"Successfully loaded {len(_sh_sections)} study hall sessions"
    
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"Error reading section data: {e}"


def schedule():
    global _students, _sh_sections, _block_schedule
    max_ppl_per_sh = 35 #can change this later if needed
    min_ppl_per_sh = 5
    
    #sanity checks
    if not _students:
        return "Error: No student data loaded"
    if not _sh_sections:
        return "Error: No study hall section loaded"
    
    avg_ppl_per_sh = len(_students)//len(_sh_sections)

    _sh_sections = sort_sh_sections(_sh_sections) #but when I sort later (i forgot which sort it is), wouldn't that just override this one?

    #finds availability of each students
    for s in _students: 
        s.set_availability(_sh_sections)    


    #sort the things
    ninth_grader = [s for s in _students if s.grade == 9] # 161人
    ninth_grader = sorted(ninth_grader, key=lambda stu: len(stu.availability))
    tenth_grader = [s for s in _students if s.grade == 10] # 32人
    tenth_grader = sorted(tenth_grader, key=lambda stu: len(stu.availability))



    #in this case since 9th graders are the majority, we'll assign them first
    #first round
    for student in ninth_grader:
        if student.needs_sh():

            candidates = []
            for i in range(len(student.availability)): #to be able to use i to check if we're at the end of a student's avail list and still hasn't assigned them their first sh due to skipping
                avail = student.availability[i] #the block
                if _sh_sections[avail]["num_of_students_in_here"] >= max_ppl_per_sh:
                    continue
                if not all(avail.get_distance(scheduled) > 1 for scheduled in student.scheduled_sh):
                    continue
                candidates.append(avail)
                
                
            if candidates:
                #defines "best" as the section (only 2nd or 4th) with the least num of people; if no 2nd or 4th availability, go to the 1st block
                candidates = sorted(candidates, key=lambda block: _sh_sections[block]["num_of_students_in_here"])
                best = None
                for candidate in candidates:
                    if candidate.which_block() in [2,4]:
                        best = candidate
                        break
                    elif best is None:
                        best = candidate
                
                #now assigns the student
                if student.add_sh(best):
                    msg = update_sh_section("add", student, best, _sh_sections)

                    if msg != "added":
                        return msg


    #second round to assign second sh section for nineth graders
    for student in ninth_grader:
        if student.needs_sh():
            placed = False
            relaxed_rule_used = False

            candidates = []
            for avail in student.availability:
                if _sh_sections[avail]["num_of_students_in_here"] >= max_ppl_per_sh:
                    continue
                if not all(avail.get_distance(scheduled) > 1 for scheduled in student.scheduled_sh):
                    continue
                candidates.append(avail)
            
            if not candidates: #if there isn't any candidate selected due to: 1. section full, 2. distance is all <= 1, or student has no availability left (this case shouldn't be the reason since we prechecked the data) -> so the only reason would be the distance issue, so we'll relax it here
                for avail in student.availability:
                    if _sh_sections[avail]["num_of_students_in_here"] >= max_ppl_per_sh:
                        continue
                    candidates.append(avail) #get rid of the distance check

                    if candidates:
                        relaxed_rule_used = True      

            if candidates:
                candidates = sorted(candidates, key=lambda block: _sh_sections[block]["num_of_students_in_here"])
                best = None
                for candidate in candidates:
                    if candidate.which_block() in [2,4]:
                        best = candidate
                        break
                    elif best is None:
                        best = candidate
                
                if student.add_sh(best):
                    _sh_sections[best]["num_of_students_in_here"] += 1
                    _sh_sections[best]["list_of_students"].append(student)

                    placed = True

                    if relaxed_rule_used:
                        student.notes.append("This student's second block could be placed only after relaxing the distance rule of 1 day apart. So now the students have consecutive study halls.")
            
            if not placed:
                if len(student.availability) == 0:
                    student.notes.append("Could not place the second study hall: no other availability was found")
                else:
                    student.notes.append("Could not place the second study hall: the student's all other available alternatives sections are full") #so if this is appended to the student's message, do we know that this is talking about all the student's availabilities are full, or the right next one we are looking at in the second round is full? Is it referring to all the blocks inside the student's availabilities?

    
    #Next we'll tackle the situation where certain 9th graders only got 1 study hall because during Round 2, every section in their availability list was at max_ppl_per_sh (35)
    ninth_w_only_1sh = [s for s in ninth_grader if len(s.scheduled_sh) == 1]
    print(f"\n[DEBUG 1] Students with only 1 SH: {len(ninth_w_only_1sh)}")

    for s in ninth_w_only_1sh:
        alternative = [b for b in s.availability if b not in s.scheduled_sh]
        placed = False
        any_passed_spacing = False

        print(f"\n[DEBUG 2] {s.name}: has {len(alternative)} alternatives: {[str(b) for b in alternative]}")
        print(f"[DEBUG 2b] {s.name}: currently scheduled in: {[str(b) for b in s.scheduled_sh]}")

        if alternative:

            for a in alternative:
                spacing_ok = all(a.get_distance(scheduled) > 1 for scheduled in s.scheduled_sh)
                print(f"[DEBUG 3] Trying section {a}: spacing_ok = {spacing_ok}")

                if not spacing_ok:
                    continue

                any_passed_spacing = True

                students_in_section = _sh_sections[a]["list_of_students"]
                print(f"[DEBUG 4] Section {a} has {len(students_in_section)} students to check")

                for stu in students_in_section:
                    ok, alt = stu.can_move_out(a, _sh_sections, max_ppl_per_sh)
                    print(f"[DEBUG 5] {stu.name}: can_move_out({a}) = ({ok}, {alt})")

                    if ok and alt != None:
                        print(f"[DEBUG 6] >>> SWAPPING! Moving {stu.name} to {alt}, placing {s.name} in {a}")
                        swap_and_move(s, stu, a, alt, _sh_sections)
                        placed = True
                        break

                if placed:
                    break

            if not placed:
                print(f"[DEBUG 7] {s.name}: NOT PLACED - any_passed_spacing={any_passed_spacing}")
                if not any_passed_spacing:
                    s.notes.append("All alternative sections failed spacing check (distance <= 1)")
                else:
                    s.notes.append("No valid alternative found: no student in those sections could be moved out because they lack alternatives")

        else:
            print(f"[DEBUG 8] {s.name}: NO ALTERNATIVES (empty list)")
            s.notes.append("No alternative availability found. This student is assigned on 1 study hall sections")
    

    #TODO: needs to assign 10th graders; also add the min_ppl_per_sh to check somewhere to fix problems after assignments
            
    
    return ninth_grader
    
'''
The problem with the current ninth grader assignment is there are two ninth graders who only have one study hall because the error message said all the sections are full, so there wasn't any other place to put these two ninth graders.  This is a problem that we're going to solve. What I can think of right now is to modify the original loop so that when stuff like this happens, we have to somehow pick some other students who may have openings in other blocks and so that they can make room for these ninth graders who only have one study hall. But when we're making those people leave and make room, we have to make sure that they have somewhere to go. This is something that I think we should resolve before implementing the tenth graders.
'''



#for testing
if __name__ == "__main__":

    path_studentInfo = '/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/data/Study Hall Free Blocks Clean.csv'
    path_sh_sections = '/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/data/Spring Study Hall Sessions.csv'
    
    block_schedule, students_parsed = read_csv_data(path_studentInfo)
    read_students(path_studentInfo)
    read_sections(path_sh_sections)
    nineth = schedule()


    sh_which_blocks = [b.which_block() for b in _sh_sections]
   
    print(f"Number of students: {len(_students)}\n")

    print(f"Example student: \n{_students[0]}")

    if any(len(s.availability) == 0 for s in _students):
        print("There are students with no availability")
    else:
        print("All students have availability")
    

    print(nineth[0])
    print(sum(info["num_of_students_in_here"] for info in _sh_sections.values()) == sum(len(s.scheduled_sh) for s in _students))



    # Debug: Count 9th graders by number of scheduled study halls
    ninth_with_0 = sum(1 for s in nineth if len(s.scheduled_sh) == 0)
    ninth_with_1 = sum(1 for s in nineth if len(s.scheduled_sh) == 1)
    ninth_with_2 = sum(1 for s in nineth if len(s.scheduled_sh) == 2)


    # Debug: Count 9th graders by number of available blocks
    avail_counts = [len(s.availability) for s in nineth]
    max_avail = max(avail_counts) if avail_counts else 0

    print(f"\n--- 9th Grader Availability Distribution ---")
    for count in range(max_avail + 1):
        num_students = sum(1 for a in avail_counts if a == count)
        print(f"  {count} available blocks: {num_students}")
    print(f"  Total 9th graders: {len(nineth)}")


    print(f"\n--- Section Fill Counts ---")
    for block, info in _sh_sections.items():
        print(f"  {block}: {block.which_block()}: {info['num_of_students_in_here']} students")
    

    print(f"\n--- 9th Grader Study Hall Distribution ---")
    print(f"  0 study halls: {ninth_with_0}")
    print(f"  1 study hall:  {ninth_with_1}")
    print(f"  2 study halls: {ninth_with_2}")
    print(f"  Total 9th graders: {len(nineth)}")
