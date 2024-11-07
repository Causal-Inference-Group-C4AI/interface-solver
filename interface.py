import argparse
from pathlib import Path
from typing import List

from src.solver_interfaces.autobounds_solver import autobounds_solver
from src.solver_interfaces.bcause_interface import bcause_solver
from src.solver_interfaces.dowhy_interface import dowhy_solver
from src.solver_interfaces.lcn_solver import lcn_solver
from utils._enums import Solvers
from utils.validator import (get_valid_edges_in_string, get_valid_mapping,
                             get_valid_number_of_tests, get_valid_path,
                             get_valid_solver_list, get_valid_test_name,
                             get_valid_unobservable, get_valid_variable)


def process_test_data(file_path: str) -> List:
    tests = []
    with open(file_path, 'r') as file:
        num_tests = get_valid_number_of_tests(file.readline().strip())

        for _ in range(num_tests):
            test = {}

            test['test_name'] = get_valid_test_name(file.readline().strip())
            test['solvers'] = get_valid_solver_list(file.readline().strip())

            test['edges'] = {}
            edges_str, edges_list = get_valid_edges_in_string(file.readline().strip())
            test['edges']['edges_str'] = edges_str
            test['edges']['edges_list'] = edges_list

            test['treatment'] = get_valid_variable(file.readline().strip(), edges_str)
            test['outcome'] = get_valid_variable(file.readline().strip(), edges_str)
            test['unobservables'] = get_valid_unobservable(file.readline().strip(), edges_str)

            test['mapping'] = get_valid_mapping(file.readline().strip())
            test['csv_path'] = get_valid_path(file.readline().strip())
            test['uai_path'] = get_valid_path(file.readline().strip())

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
    print()


def interface(file_path: str):
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
            lcn_solver(test['test_name'], test['edges']['edges_str'],
                              test['unobservables'], test['csv_path'], test['treatment'], test['outcome'])

        if Solvers.AUTOBOUNDS.value in test['solvers']:
            print("TEST AUTOBOUNDS")
            autobounds_solver(test['test_name'], test['edges']['edges_str'],
                              test['unobservables'], test['csv_path'],
                              test['treatment'], test['outcome']
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Runs tests of Causal Effect under Partial-Observability."
    )
    parser.add_argument('file_path',
                        help='The path to the file you want to read'
    )
    args = parser.parse_args()
    try:
        interface(get_valid_path(args.file_path))
    except Exception as e:
        print(f"{type(e).__module__}.{type(e).__name__}: {e}")
