import argparse
import logging
from pathlib import Path
from typing import List

from src.solvers.autobounds_solver import autobounds_solver
from src.solvers.bcause_solver import bcause_solver
from src.solvers.dowhy_solver import dowhy_solver
# from src.solvers.lcn_solver import lcn_solver
from utils._enums import Solvers
from utils.file_generators.uai_generator import UaiGenerator
from utils.suppress_print import suppress_print
from utils.validator import Validator


@suppress_print
def get_files(test, file):
    val = Validator()
    first_path = val.get_valid_path(file.readline().strip())
    second_path = file.readline().strip()
    if '.csv' in first_path:
        csv_path = first_path
        if 'bcause' in test['solvers']:
            if not ('.' in second_path):
                uai = UaiGenerator(test['test_name'], test['edges']
                                   ['edges_str'], csv_path)
                uai_path = val.get_valid_path(uai.uai_path)
                uai_mapping = val.get_valid_mapping(
                    uai.get_mapping_str())
            else:
                # TODO: If user inputs uai_path, must input mapping
                pass
        else:
            uai_path = None
            uai_mapping = None
    elif 'uai' in first_path:
        # TODO: Implement csv generation
        pass

    return uai_mapping, csv_path, uai_path


def process_test_data(file_path: str) -> List:
    validator = Validator()
    validator.get_valid_path(file_path)
    with open(file_path, 'r') as file:
        test = {}

        test['test_name'] = validator.get_valid_test_name(
            file.readline().strip())
        test['solvers'] = validator.get_valid_solver_list(
            file.readline().strip())

        test['edges'] = {}
        edges_str, edges_list = validator.get_valid_edges_in_string(
            file.readline().strip())
        test['edges']['edges_str'] = edges_str
        test['edges']['edges_list'] = edges_list

        test['treatment'] = validator.get_valid_variable(
            file.readline().strip(), edges_str)
        test['outcome'] = validator.get_valid_variable(
            file.readline().strip(), edges_str)
        test['unobservables'] = validator.get_valid_unobservables(
            file.readline().strip(), edges_str)

        test['mapping'], test['csv_path'], test['uai_path'] = get_files(
            test, file)

        return test


def print_test_info(test_info: dict):
    print(f"Test Name {test_info['test_name']}:")
    print(f"  Edges: {test_info['edges']['edges_str']}")
    print(f"  Treatment: {test_info['treatment']}")
    print(f"  Outcome: {test_info['outcome']}")
    print(f"  Unobservable Variables: {test_info['unobservables']}")
    print(f"  CSV Path: {test_info['csv_path']}")
    print(f"  UAI Path: {test_info['uai_path']}")
    print()


def interface(file_path: str):
    test = process_test_data(file_path)
    print_test_info(test)

    folder_name = Path(f"outputs/{test['test_name']}")
    folder_name.mkdir(parents=True, exist_ok=True)

    if Solvers.DOWHY.value in test['solvers']:
        print("TEST DOWHY")
        dowhy_solver(
            test['test_name'], test['csv_path'],
            test['edges']['edges_list'],
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
                   test['unobservables'], test['csv_path'],
                   test['treatment'], test['outcome'])

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
    parser.add_argument('-v', '--verbose',
                        action='store_true', help="Show solver logs")
    args = parser.parse_args()
    try:
        if not args.verbose:
            logging.getLogger().setLevel(logging.CRITICAL)
        interface(args.file_path)
    except Exception as e:
        print(f"{type(e).__module__}.{type(e).__name__}: {e}")
