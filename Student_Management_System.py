import sys

database = ["pritesh","sarthak","sarika","priyanka"]

def view_studentList():
    for i in database:
        print(i)

def add_studentList(name):
    database.append(name)

def search_student(name):
    if name in database:
        print("Student Found!")
    else:
        print("Student not found!")
def remove_student(name):
    database.remove(name)

print("Welcome To Student Management System!")
print()
print("1.View Student")
print("2.Add Student")
print("3.Search Student")
print("4.Remove Student")
print("5.Exit")

while True:
    print()
    ch = input("Please selecet an option : ")
    if ch == '1':
        print()
        print("-------------List of Students-------------")
        view_studentList()
    elif ch == '2':
        print("-------------Add Student-------------")
        name = input("Enter name : ")
        add_studentList(name)
    elif ch == '3':
        print()
        print("-------------Search Student-------------")
        name = input("Enter name to search : ")
        search_student(name)
    elif ch == '4':
        print()
        print("-------------Remove Student-------------")
        name = input("Enter name to remove : ")
        remove_student(name)
    elif ch == '5':
        print("Exiting the Student Management System. Goodbye!")
        sys.exit()
    else:
        print("Invalid option! Please try again.")
        
        