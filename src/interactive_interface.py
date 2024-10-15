#!/usr/bin/python3
from solver_interfaces.bcause_interface import bcause_solver
from solver_interfaces.dowhy_interface import dowhy_solver

def interactive_interface():
    print("Choose solver:")
    print(">> 1 DoWhy")
    print(">> 2 Bcause")
    print(">> 3 LCN")
    print(">> 4 Autobounds")
    print(">> 5 ALL")
    solver_index = int(input('Type solver index: '))

    while solver_index < 0 or solver_index > 5:
        print(f"The index {solver_index} is not valid. Please select a valid solver:")
        print(">> 1 DoWhy")
        print(">> 2 Bcause")
        print(">> 3 LCN")
        print(">> 4 Autobounds")
        print(">> 5 ALL")
        solver_index = int(input('Type solver index: '))
    

    if solver_index == 1:
        dowhy_solver()
    elif solver_index == 2:
        bcause_solver()
    elif solver_index == 3:
        print("LCN solver not implemented yet")
    elif solver_index == 4:
        print("Autobounds solver not implemented yet")
    elif solver_index == 5:
        print("ALL solver not implemented yet")


if __name__ == "__main__":
    interactive_interface()