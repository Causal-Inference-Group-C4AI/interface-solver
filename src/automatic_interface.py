#!/usr/bin/python3

from solver_interfaces.bcause_interface import bcause_solver

def automatic_interface():
    filename = input('Type the filename: ')

    with open(filename, 'r') as file:
        for line in file:
            # Process the line (e.g., strip whitespace and print)
            print(line.strip())

    print(">> 1 DoWhy")
    print(">> 2 Bcause")
    print(">> 3 LCN")
    print(">> 4 Autobounds")
    print(">> 5 ALL")


if __name__ == "__main__":
    automatic_interface()