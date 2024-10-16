#!/usr/bin/python3

from solver_interfaces.bcause_interface import bcause_solver

def process_test_data(file_path):
    tests = []  # List to store all tests

    with open(file_path, 'r') as file:
        num_tests = int(file.readline().strip())  # First line is the number of tests
        
        for _ in range(num_tests):
            test = {}  # Dictionary to store a single test's data
            
            test['edge'] = file.readline().strip()
            test['unobserved_variables'] = file.readline().strip()
            test['csv_path'] = file.readline().strip()
            test['uai_path'] = file.readline().strip()
            
            tests.append(test)

    return tests

def automatic_interface():
    filename = input('Type the filename: ')
    tests = process_test_data(filename)

    for i, test in enumerate(tests, 1):
        print(f"Test {i}:")
        print(f"  Edge: {test['edge']}")
        print(f"  Unobserved Variables: {test['unobserved_variables']}")
        print(f"  CSV Path: {test['csv_path']}")
        print(f"  UAI Path: {test['uai_path']}")
        print()

    print(">> 1 DoWhy")
    print(">> 2 Bcause")
    print(">> 3 LCN")
    print(">> 4 Autobounds")
    print(">> 5 ALL")




if __name__ == "__main__":
    automatic_interface()