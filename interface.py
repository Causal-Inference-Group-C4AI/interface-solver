import argparse
import json
from pathlib import Path

from src.solver_interfaces.autobounds_solver import autobounds_solver
from src.solver_interfaces.bcause_interface import bcause_solver
from src.solver_interfaces.dowhy_interface import dowhy_solver
from src.solver_interfaces.lcn_solver import lcn_solver
from utils._enums import Solvers
from utils.conversor import convert_str_edges_into_a_tuple_list


def process_test_data(file_path):
    tests = []

    with open(file_path, 'r') as file:
        num_tests = int(file.readline().strip())

        for _ in range(num_tests):
            test = {}

            test['test_name'] = file.readline().strip()
            test['solvers'] = file.readline().strip().lower().split(' ')
            
            test['edges'] = {}
            edges_str = file.readline().strip().upper()
            test['edges']['edges_str'] = edges_str
            test['edges']['edges_list'] = convert_str_edges_into_a_tuple_list(edges_str)

            test['treatment'] = file.readline().strip().upper()
            test['outcome'] = file.readline().strip().upper()

            unobservables = file.readline().strip().upper()
            if unobservables == "-":
                test['unobservables'] = None
            else:
                test['unobservables'] = unobservables
            
            test['mapping'] = json.loads(file.readline().strip().upper())
            test['csv_path'] = file.readline().strip()
            test['uai_path'] = file.readline().strip()
            test['lcn_path'] = file.readline().strip()

            tests.append(test)

    return tests


def print_test_info(test_info: dict, test_number: int):
    print(f"Test Number {test_number}:")
    print(f"Test Name {test_info['test_name']}:")
    print(f"  Edges: {test_info['edges']}")
    print(f"  Treatment: {test_info['treatment']}")
    print(f"  Outcome: {test_info['outcome']}")
    print(f"  Unobservable Variables: {test_info['unobservables']}")
    print(f"  CSV Path: {test_info['csv_path']}")
    print(f"  UAI Path: {test_info['uai_path']}")
    print(f"  .LCN Path: {test_info['lcn_path']}")
    print()


def interface(file_path):
    tests = process_test_data(file_path)
    for i, test in enumerate(tests, 1):
        print_test_info(test, i+1)

        folder_name = Path(f"outputs/{test['test_name']}")
        folder_name.mkdir(parents=True, exist_ok=True)

        if Solvers.DOWHY.value in test['solvers']:
            print("TEST DOWHY")
            dowhy_solver(
                test['test_name'], test['csv_path'], test['edges']['edges_list'],
                test['treatment'], test['outcome']
            )

        if Solvers.BCAUSE.value in test['solvers']:
            print("TEST BCAUSE")
            bcause_solver(test['test_name'], test['uai_path'],
                          test['csv_path'], test['treatment'],
                          test['outcome'], test['mapping']
            )

        if Solvers.LCN.value in test['solvers']:
            print("TEST LCN")
            lcn_solver()

        if Solvers.AUTOBOUNDS.value in test['solvers']:
            print("TEST AUTOBOUNDS")
            autobounds_solver(test['test_name'], test['edges']['edges_str'],
                              test['unobservables'], test['csv_path'],
                              test['treatment'], test['outcome']
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs tests of Causal Effect under Partial-Observability.")
    parser.add_argument('file_path',
                        help='The path to the file you want to read')
    args = parser.parse_args()
    interface(args.file_path)
