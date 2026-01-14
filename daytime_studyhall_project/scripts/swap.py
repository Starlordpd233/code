        
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

