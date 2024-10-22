#!/usr/bin/python3

import argparse
import json
from pathlib import Path

from src.solver_interfaces.autobounds_solver import autobounds_solver
from src.solver_interfaces.bcause_interface import bcause_solver
from src.solver_interfaces.dowhy_interface import dowhy_solver
from src.solver_interfaces.lcn_solver import lcn_solver


def process_test_data(file_path):
    tests = []

    with open(file_path, 'r') as file:
        # First line is the number of tests
        num_tests = int(file.readline().strip())

        for _ in range(num_tests):
            test = {}  # Dictionary to store a single test's data

            test['test_name'] = file.readline().strip()
            test['solvers'] = file.readline().strip().split(' ')
            test['edges'] = file.readline().strip()
            test['treatment'] = file.readline().strip()
            test['outcome'] = file.readline().strip()
            test['unobservables'] = file.readline().strip()
            test['mapping'] = json.loads(file.readline().strip())
            test['csv_path'] = file.readline().strip()
            test['uai_path'] = file.readline().strip()
            test['lcn_path'] = file.readline().strip()

            tests.append(test)

    return tests


def automatic_interface(file_path):
    tests = process_test_data(file_path)
    j = 0
    for i, test in enumerate(tests, 1):

        folder_name = Path(f"outputs/{test['test_name']}")
        folder_name.mkdir(parents=True, exist_ok=True)

        if '1' in test['solvers']:
            print(f"Test {i+j} -- DoWhy:")
            print(f"  Edges: {test['edges']}")
            print(f"  Unobservable Variables: {test['unobservables']}")
            print(f"  CSV Path: {test['csv_path']}")
            print()
            dowhy_solver(test['csv_path'], test['edges'])
            j += 1

        if '2' in test['solvers']:
            print(f"Test {i+j} -- Bcause:")
            print(f"  Edges: {test['edges']}")
            print(f"  CSV Path: {test['csv_path']}")
            print(f"  UAI Path: {test['uai_path']}")
            print()
            bcause_solver(test['test_name'], test['uai_path'],
                          test['csv_path'], test['treatment'],
                          test['outcome'], test['mapping'])
            j += 1

        if '3' in test['solvers']:
            print(f"Test {i+j} -- LCN:")
            print(f"  Edges: {test['edges']}")
            print(f"  .LCN Path: {test['lcn_path']}")
            print()
            lcn_solver()
            j += 1

        if '4' in test['solvers']:
            print(f"Test {i+j} -- AUTOBOUNDS:")
            print(f"  Edges: {test['edges']}")
            print(f"  Unobservable Variables: {test['unobservables']}")
            print(f"  CSV Path: {test['csv_path']}")
            autobounds_solver(
                test['edges'], test['unobservables'], test['csv_path'])
            j += 1


def main():
    parser = argparse.ArgumentParser(
        description="Runs tests of Causal Effect under Partial-Observability.")
    parser.add_argument('file_path',
                        help='The path to the file you want to read')
    args = parser.parse_args()
    automatic_interface(args.file_path)


if __name__ == "__main__":
    main()
