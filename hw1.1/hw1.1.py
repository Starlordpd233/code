

def part_2(input_file): #modified after solving part 1; dump approach personally speaking

    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    instruction_list = [l.strip() for l in lines]

    current_dial = 50
    count_0 = 0

    for rotation in instruction_list: 
        direction = rotation[0] 
        amount = int(rotation[1:])

        if direction == "R":
            
            count_0 += (current_dial + amount) // 100

            current_dial = (current_dial + amount) % 100 #update position

        
        else:

            new_dial = (current_dial - amount) % 100 

            count_0 += (new_dial + amount) // 100 #treat as if it's right turn from the new dial

            if current_dial == 0: #integer division counts once if you start at 0
                count_0 -= 1
            
            if new_dial == 0: #integer division is start-exclusive
                count_0 += 1

            current_dial = new_dial

    return count_0


def brute_force(input_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    instruction_list = [l.strip() for l in lines]
    current_dial = 50
    part_1_count = 0
    part_2_count = 0
 
    #simulate every click one at a time
    for each_rotation in instruction_list:
        direction = each_rotation[0]
        amount = int(each_rotation[1:])
        
        for _ in range(amount):

            if direction == "R":
                current_dial = (current_dial + 1) % 100 #update position after each click

            elif direction == "L":
                current_dial = (current_dial - 1) % 100
                
            if current_dial == 0: #check 0 after each click
                part_2_count += 1
        
        if current_dial == 0: #check 0 after the full rotation for part I only
            part_1_count += 1

    return part_1_count, part_2_count


    

if __name__ == "__main__":
    input_file = "hw1.1/input.txt"  
    print(brute_force(input_file))








