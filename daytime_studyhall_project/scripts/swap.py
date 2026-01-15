        
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

    #move the student out first
    stu_out.scheduled_sh.remove(block_of_swapping)
    msg1 = update_sh_section("remove", stu_in, block_of_swapping, _sh_sections)
    stu_out.scheduled_sh.append(destination_block_for_stu_out)
    msg2 = update_sh_section("add", stu_in, destination_block_for_stu_out, _sh_sections)

    #moves the waiting student in
    stu_in.scheduled_sh.append(block_of_swapping)
    msg3 = update_sh_section("add", stu_in, block_of_swapping, _sh_sections)

    #add notes:
    stu_out.notes.append(f"Moved from {block_of_swapping} to {destination_block_for_stu_out} to make room for {stu_in.name}")
    stu_in.notes.append(f"Placed in {block_of_swapping} after bumping {stu_out.name}")

    return msg1, msg2, msg3








# ---------------------------------------------------------
    # BALANCING LOGIC: Move students from Overfilled to Underfilled
    # ---------------------------------------------------------
    
    # 1. Identify the empty rooms we need to fill
    underfilled_sections = [sh for sh in _sh_sections if _sh_sections[sh]["num_of_students_in_here"] < min_ppl_per_sh]
    
    # 2. Define the safe limits
    safe_donor_threshold = 25 # Don't let donors drop below this
    
    # Helper to find valid donors (sections that have spare students)
    def get_donors():
        return [b for b in _sh_sections if _sh_sections[b]["num_of_students_in_here"] > safe_donor_threshold]

    for und in underfilled_sections:
        # We try to fill this specific underfilled section until it hits the minimum
        
        # --- PHASE 1: Try to move students keeping the spacing rule ---
        donor_sections = get_donors() # Refresh donors for this target
        
        for donor in donor_sections:
            # OPTIMIZATION: Stop if our target section is full enough
            if _sh_sections[und]["num_of_students_in_here"] >= min_ppl_per_sh:
                break 
            
            # CRITICAL: Iterate over a COPY so we don't break the loop when removing
            candidates = list(_sh_sections[donor]["list_of_students"])
            
            for student in candidates:
                # --- THE SAFETY BRAKE ---
                # Check explicitly: Does the donor STILL have enough people?
                if _sh_sections[donor]["num_of_students_in_here"] <= safe_donor_threshold:
                    break # Stop taking from this donor immediately!
                
                # Check: Is target full?
                if _sh_sections[und]["num_of_students_in_here"] >= min_ppl_per_sh:
                    break
                # ------------------------

                # 1. Basic Eligibility
                if und not in student.availability or und in student.scheduled_sh:
                    continue
                
                # 2. Spacing Check (Strict)
                other_blocks = [b for b in student.scheduled_sh if b != donor]
                spacing_ok = all(und.get_distance(scheduled) > 1 for scheduled in other_blocks)

                if spacing_ok:
                    update_sh_section("add", student, und, _sh_sections)
                    update_sh_section("remove", student, donor, _sh_sections)
                    student.notes.append(f"Balanced: Moved from {donor} to {und}")

        # --- PHASE 2: Desperate Measures (Ignore Spacing) ---
        # Only runs if Phase 1 didn't fill the section
        if _sh_sections[und]["num_of_students_in_here"] < min_ppl_per_sh:
            donor_sections = get_donors() # Refresh donors again
            
            for donor in donor_sections:
                if _sh_sections[und]["num_of_students_in_here"] >= min_ppl_per_sh:
                    break 
                
                candidates = list(_sh_sections[donor]["list_of_students"])
                for student in candidates:
                    
                    # --- THE SAFETY BRAKE (Repeated for Phase 2) ---
                    if _sh_sections[donor]["num_of_students_in_here"] <= safe_donor_threshold:
                        break 
                    
                    if _sh_sections[und]["num_of_students_in_here"] >= min_ppl_per_sh:
                        break
                    # -----------------------------------------------

                    if und not in student.availability or und in student.scheduled_sh:
                        continue
                    
                    # Move without checking spacing
                    update_sh_section("add", student, und, _sh_sections)
                    update_sh_section("remove", student, donor, _sh_sections)
                    student.notes.append(f"Balanced (Forced): Moved from {donor} to {und} (Ignored Spacing)")

    return ninth_grader, tenth_grader



# [Existing code inside the loop: for student in ninth_grader:]

        # 1. First Study Hall Assignment (The Critical Step)
        if not student.scheduled_sh:
            # Filter for valid choices (actual study halls this student is free for)
            valid_choices = [b for b in student.availability if b in sh_sections]
            
            if valid_choices:
                # STRATEGY CHANGE: "Least-Filled First"
                # We simply sort the valid choices by how many people are currently in them.
                # The one with the lowest count becomes index 0.
                valid_choices.sort(key=lambda b: sh_sections[b]["num_of_students_in_here"])
                
                # Pick the emptiest one
                best_section = valid_choices[0]
                
                # Assign it
                if update_sh_section("add", student, best_section, sh_sections):
                    pass # Success
            else:
                pass # No valid choices (rare if availability is parsed right)

        # 2. Second Study Hall Assignment (Round 2)
        # [This part can stay similar, but we should apply the same logic]
        elif student.needs_sh():
             # ... (logic to find valid_choices) ...
             
             # Filter valid_choices to only those that respect spacing
             spaced_choices = [b for b in valid_choices if 
                               all(b.get_distance(existing) > 1 for existing in student.scheduled_sh)]
             
             if spaced_choices:
                 # Apply the same "Least-Filled First" logic here
                 spaced_choices.sort(key=lambda b: sh_sections[b]["num_of_students_in_here"])
                 best_section = spaced_choices[0]
                 
                 update_sh_section("add", student, best_section, sh_sections)