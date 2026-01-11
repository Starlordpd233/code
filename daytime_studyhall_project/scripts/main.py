#from modules import read_csv_data, parse_blocks
#from student import Student

if __name__ == "__main__":

    block_schedule, students_parsed = read_csv_data()
    student1 = students_parsed[0]
    name = student1[0]
    grade = student1[1]
    student1_blocks = parse_blocks(students_parsed)[0]

    student_test = Student(name, grade)
    student_test.get_freeBlocks(block_schedule, student1_blocks)

    print(student_test)

