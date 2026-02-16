from student import Student
from block import Block
from modules import compute_sh_section_demand, read_csv_data, parse_blocks, sort_sh_sections, get_valid_candidates, pick_best_section

_block_schedule = []
_students = []
_sh_sections = {}
school_year = 2025

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
    """
    Use this function when a students needs placement but all their options are at max capacity.
    Bumps stu_out to their alternative, freeing up a spot for stu_in
    Use with student.can_move_out()
    """

    #move the student out first
    msg1 = update_sh_section("remove", stu_out, block_of_swapping, _sh_sections)
    msg2 = update_sh_section("add", stu_out, destination_block_for_stu_out, _sh_sections)

    #moves the waiting student in
    msg3 = update_sh_section("add", stu_in, block_of_swapping, _sh_sections)

    #add notes:
    stu_out.notes.append(f"Moved from {block_of_swapping} to {destination_block_for_stu_out} to make room for {stu_in.name}")
    stu_in.notes.append(f"Placed in {block_of_swapping} after bumping {stu_out.name}")

    return msg1, msg2, msg3

def rescue_capacity_swaps_for_ninth(ninth_graders, sh_sections, max_ppl_per_sh):
    rescued = 0

    targets = [s for s in ninth_graders if s.needs_sh()]

    for student in targets:
        alternatives = [b for b in student.availability if b not in student.scheduled_sh]
        placed = False
        any_passed_spacing = False

        for alt in alternatives:
            spacing_ok = all(alt.get_distance(scheduled) > 1 for scheduled in student.scheduled_sh)
            if not spacing_ok:
                continue
            any_passed_spacing = True

            if sh_sections[alt]["num_of_students_in_here"] < max_ppl_per_sh:
                continue #has room, should've been placed in round 2

            for donor in list(sh_sections[alt]["list_of_students"]):
                ok, donor_destination = donor.can_move_out(alt, sh_sections, max_ppl_per_sh)

                if ok and donor_destination is not None:
                    if student.add_sh(alt):
                        swap_and_move(student, donor, alt, donor_destination, sh_sections)
                        rescued += 1
                        placed = True
                        break
            if placed:
                break
        if not placed and alternatives:
              if not any_passed_spacing:
                  student.notes.append("Rescue failed: all alternatives failed spacing check")
              else:
                  student.notes.append("Rescue failed: no donor in full sections could be moved out")

    return rescued




#Public Functions for UI
def read_sections(filename: str) -> str:
    global _sh_sections
    _sh_sections = {}

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
                "list_of_students": [],
                "num_of_students_in_here": 0, #initializes the count here,
                "demand" : 0
            }


        return f"Successfully loaded {len(_sh_sections)} study hall sessions"
    
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"Error reading section data: {e}"


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



def schedule():
    global _students, _sh_sections, _block_schedule
    max_ppl_per_sh = 35 #can change this later if needed
    min_ppl_per_sh = 5
    
    #sanity checks
    if not _students:
        return "Error: No student data loaded"
    if not _sh_sections:
        return "Error: No study hall section loaded"

    compute_sh_section_demand(_students, _sh_sections)


    ordered_sh_sections_list = sort_sh_sections(_sh_sections) 

    #set up once availability of each students
    for s in _students: 
        s.set_availability(ordered_sh_sections_list)    


    #sort the things
    ninth_grader = [s for s in _students if s.grade == 9] # 161人
    ninth_grader = sorted(ninth_grader, key=lambda stu: len(stu.availability))
    tenth_grader = [s for s in _students if s.grade == 10] # 32人
    tenth_grader = sorted(tenth_grader, key=lambda stu: len(stu.availability))



    #in this case since 9th graders are the majority, we'll assign them first
    #------------------------------------------------------------------------
    #FIRST ROUND
    for student in ninth_grader:
        if student.needs_sh():

            candidates = get_valid_candidates(student, _sh_sections, max_ppl_per_sh)
            best = pick_best_section(candidates, _sh_sections)
                
            if best and student.add_sh(best):
                msg = update_sh_section("add", student, best, _sh_sections)

                if msg != "added":
                    return msg

    #-----------------------------------------------------------------------
    #SECOND ROUND
    for student in ninth_grader:
        if student.needs_sh():
            candidates = get_valid_candidates(student, _sh_sections, max_ppl_per_sh)
            best = pick_best_section(candidates, _sh_sections)
        
            #if no best is picked, relaxed attempt to pick best by relaxing distance rule
            if not best:
                relaxed_candidates = [avail for avail in student.availability if _sh_sections[avail]["num_of_students_in_here"] < max_ppl_per_sh and avail not in student.scheduled_sh]

                best = pick_best_section(relaxed_candidates, _sh_sections)
                if best:
                    student.notes.append("Placed with relaxed spacing rule for second study hall (consecutive study halls now)")

            if best and student.add_sh(best):
                msg = update_sh_section("add", student, best, _sh_sections)
                if msg != "added":
                    return msg
            
            #failed for some other reasons
            elif not best:
                student.notes.append("Could not place the second study hall: no available section under capacity (after relaxing spacing)")


    #-----------------------------------------------------------------------
    #THIRD ROUND (RESCUE): capacity-based swaps for 9th graders still needing SH after second round placement
    rescued_count = rescue_capacity_swaps_for_ninth(ninth_grader, _sh_sections, max_ppl_per_sh)
    
    #-----------------------------------------------------------------------
    #FOR TENTH GRADER
    for student in tenth_grader:
        if student.needs_sh():

            candidates = get_valid_candidates(student, _sh_sections, max_ppl_per_sh)
            best = pick_best_section(candidates, _sh_sections)
                
            if best and student.add_sh(best):
                msg = update_sh_section("add", student, best, _sh_sections)

                if msg != "added":
                    return msg

    
    #now a checking to try to "enforce" the min people requirement
    underfilled_sections = [sh for sh in _sh_sections if 0 < _sh_sections[sh]["num_of_students_in_here"] < min_ppl_per_sh]

    for und in underfilled_sections:
        moved = False

        while _sh_sections[und]["num_of_students_in_here"] < min_ppl_per_sh: 
            donor_sections = [b for b in _sh_sections if _sh_sections[b]["num_of_students_in_here"] > 25] #instead of hardcoding a number, we can start with the section with the most people and then the next large section, then the next, etc.

            moved = False
            for donor in donor_sections:
                for student in list(_sh_sections[donor]["list_of_students"]):
                    #if they can be moved to underfilled that's not currently their scheduled section
                    if und not in student.availability or und in student.scheduled_sh:
                        continue
                    if not all(und.get_distance(scheduled) > 1 for scheduled in student.scheduled_sh if scheduled != donor):
                        continue
        
                    update_sh_section("add", student, und, _sh_sections)
                    update_sh_section("remove", student, donor, _sh_sections)

                    student.notes.append(
                        f"Reassigned from {donor} to {und} to help meet minimum enrollment in {und} (min {min_ppl_per_sh})."
                    )
                    moved = True
                    break #we have transfered one student from this donor. we will stop looking for other students in this donor
                if moved:
                    break #we already moved one student, stop scanning other donor sections
                
            if not moved:
                for s in _sh_sections[und]["list_of_students"]:
                    s.notes.append(
                        f"Section {und} remained underfilled (min {min_ppl_per_sh}); no eligible transfers found."
                    )
                break

    

    #for error handling and printing in terminal
    total_enrollments = sum(info["num_of_students_in_here"] for info in _sh_sections.values())

    short_ninth = sum(1 for s in ninth_grader if len(s.scheduled_sh) < 2)
    short_tenth = sum(1 for s in tenth_grader if len(s.scheduled_sh) < 1)
    short_total = short_ninth + short_tenth

    underfilled_count = sum(1 for b in _sh_sections if 0 < _sh_sections[b]["num_of_students_in_here"] < min_ppl_per_sh)


    db_path = '/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/output/database_output_class_enrollment.csv'
    report_path = '/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/output/human_report.txt'

    db_success, db_msg, db_count = write_database_output(_sh_sections, db_path)
    report_success, report_msg, report_count = write_human_report(report_path)


    lines = []
    lines.append(f"Successfully scheduled {len(_students)} students.")
    lines.append(f"- {total_enrollments} total enrollments")
    if rescued_count > 0:
        lines.append(f"- {rescued_count} students rescued via capacity swaps")
    lines.append(f"- {short_total} students short of target")

    if underfilled_count > 0:
        lines.append(f"- {underfilled_count} underfilled sections remain")

    lines.append("")
    lines.append("Output files:")

    if db_success:
        lines.append(f"- Database: {db_path} ({db_count} records)")
    else:
        lines.append(f"- Database: FAILED - {db_msg}")

    if report_success:
        lines.append(f"- Report: {report_path}")
    else:
        lines.append(f"- Report: FAILED - {report_msg}")

    return '\n'.join(lines)



def write_database_output(sh_section, output_path):
    global school_year
    rows = []

    for block, section_info in sh_section.items():
        students_in_section = section_info["list_of_students"]

        for stu in students_in_section:
            row = [section_info["internal_class_id"], section_info["class_id"], school_year, str(stu.id), str(stu.grade)]
            rows.append(row)
    
    try:
        with open(output_path, 'w') as f:
            f.write("internal_class_id,class_id,school_year,veracross_student_id,grade_level\n")
            for row in rows:
                line = ",".join(str(val) for val in row)
                f.write(line+"\n")
        

        return (True, f"Exported {len(rows)} enrollment records", len(rows))
    
    except Exception as e:
        return (False, f"Exported failed: {e}", 0)


from datetime import datetime

def write_human_report(output_path):
    global _students, _sh_sections
    WIDTH = 60
    min_ppl_per_sh = 5
    lines = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    #helpers
    def get_target(grade):
        if grade == 9:
            return 2
        return 1

    def get_reason(student):
        if student.notes:
            return " | ".join(student.notes)
        if len(student.availability) == 0:
            return "No study hall blocks available"
        if len(student.availability) <= len(student.scheduled_sh):
            return "No remaining available sections"
        return "Capacity or spacing constraints"


    ninth = [s for s in _students if s.grade == 9]
    tenth = [s for s in _students if s.grade == 10]

    ninth_0 = sum(1 for s in ninth if len(s.scheduled_sh) == 0)
    ninth_1 = sum(1 for s in ninth if len(s.scheduled_sh) == 1)
    ninth_2 = sum(1 for s in ninth if len(s.scheduled_sh) == 2)

    tenth_0 = sum(1 for s in tenth if len(s.scheduled_sh) == 0)
    tenth_1 = sum(1 for s in tenth if len(s.scheduled_sh) == 1)

    total_enrollments = sum(info["num_of_students_in_here"] for info in _sh_sections.values())

    empty_sections = [b for b in _sh_sections if _sh_sections[b]["num_of_students_in_here"] == 0]
    underfilled = [b for b in _sh_sections if 0 < _sh_sections[b]["num_of_students_in_here"] < min_ppl_per_sh]
    ok_sections = [b for b in _sh_sections if _sh_sections[b]["num_of_students_in_here"] >= min_ppl_per_sh]

    short_students = [s for s in _students if len(s.scheduled_sh) < get_target(s.grade)]

    students_with_notes = [s for s in _students if s.notes]


    lines.append("=" * WIDTH)
    lines.append("DAYTIME STUDY HALL SCHEDULING REPORT".center(WIDTH))
    lines.append(f"Generated: {timestamp}".center(WIDTH))
    lines.append("=" * WIDTH)
    lines.append("")

    if not short_students:
        lines.append(f"{'  ALL TARGETS MET  ':=^{WIDTH}}")
    else:
        lines.append(f"{'  WARNING: Some students below target  ':=^{WIDTH}}")
    lines.append("")

    lines.append("1. SUMMARY")
    lines.append("-" * WIDTH)
    lines.append(f"{'Total Students:':<20} {len(_students):>6}")
    lines.append(f"{'Total Enrollments:':<20} {total_enrollments:>6}")
    lines.append("")

    lines.append("9th Graders (target: 2 study halls):")
    lines.append(f"  {'2 study halls:':<18} {ninth_2:>4}")
    lines.append(f"  {'1 study hall:':<18} {ninth_1:>4}")
    lines.append(f"  {'0 study halls:':<18} {ninth_0:>4}")
    lines.append(f"  {'Total:':<18} {len(ninth):>4}")
    lines.append("")


    lines.append("10th Graders (target: 1 study hall):")
    lines.append(f"  {'1 study hall:':<18} {tenth_1:>4}")
    lines.append(f"  {'0 study halls:':<18} {tenth_0:>4}")
    lines.append(f"  {'Total:':<18} {len(tenth):>4}")
    lines.append("")


    lines.append("=" * WIDTH)
    lines.append("2. SECTION FILL SUMMARY")
    lines.append("-" * WIDTH)
    lines.append(f"  {'Section':<8}  {'Block':<8}  {'Enrolled':<13}  Status")
    lines.append("")

    for block in sorted(_sh_sections.keys(), key=lambda b: (b.day, b.block)): #order by day and block for readability
        count = _sh_sections[block]["num_of_students_in_here"]
        if count == 0:
            status = "EMPTY"
        elif count < min_ppl_per_sh:
            status = "UNDERFILLED"
        else:
            status = "OK"
        lines.append(f"  {str(block):<8}  Block {block.which_block():<2}  {count:>3} students   [{status}]")

    lines.append("")
    lines.append(f"Active Study Hall Sections Counts: {len(ok_sections) + len(underfilled)}  |  Empty: {len(empty_sections)}  |  Underfilled: {len(underfilled)}")
    lines.append("")


    lines.append("=" * 60)
    lines.append("STUDENTS SHORT OF DESIRED NUM OF STUDY HALLS")

    if not short_students:
        lines.append("All students received their target.")
    else:
        for s in sorted(short_students, key=lambda x: (x.grade, x.id)): #sort by grade and id
            target = get_target(s.grade)
            actual = len(s.scheduled_sh)
            reason = get_reason(s)
            lines.append(f"{s.id} (Grade {s.grade}): scheduled: {actual}   |    target: {target} - Reason: {reason}")

    lines.append("")


    lines.append("=" * 60)
    lines.append("3. NOTES FROM ASSIGNMENT PROCESS")
    lines.append("-" * 50)

    if not students_with_notes:
        lines.append("None.")
    else:
        for s in sorted(students_with_notes, key=lambda x: x.id):
            lines.append(f"{s.id}:")
            for note in s.notes:
                lines.append(f"  - {note}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("END")

    try:
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))

        return (True, f"Report written to {output_path}", len(short_students))

    except Exception as e:
        return (False, f"Report failed: {e}", 0)



#for testing
if __name__ == "__main__":

      path_studentInfo = '/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/data/Study Hall Free Blocks Clean.csv'
      path_sh_sections = '/Users/MatthewLi/Desktop/Senior Year/Winter/Comp_Sci/code/daytime_studyhall_project/data/Spring Study Hall Sessions.csv'

      print(read_students(path_studentInfo))
      print(read_sections(path_sh_sections))
      print()
      print(schedule())




   