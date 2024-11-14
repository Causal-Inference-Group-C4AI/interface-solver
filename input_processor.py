from typing import Dict

from utils.validator import Validator


class InputProcessor:
    def __init__(self, input_path: str):
        self.input_path = input_path
        self.data_test = self.process_test_data()


    def process_test_data(self) -> Dict:
        test = {}
        validator = Validator()
        self.input_path = validator.get_valid_path(self.input_path)
        with open(self.input_path, 'r') as file:
            test['test_name'] = validator.get_valid_test_name(file.readline().strip())
            test['solvers'] = validator.get_valid_solver_list(file.readline().strip())

            test['edges'] = {}
            edges_str, edges_list = validator.get_valid_edges_in_string(file.readline().strip())
            test['edges']['edges_str'] = edges_str
            test['edges']['edges_list'] = edges_list

            test['treatment'] = validator.get_valid_variable(file.readline().strip(), edges_str)
            test['outcome'] = validator.get_valid_variable(file.readline().strip(), edges_str)
            test['unobservables'] = validator.get_valid_unobservables(file.readline().strip(), edges_str)

            test['mapping'] = validator.get_valid_mapping(file.readline().strip())
            test['csv_path'] = validator.get_valid_path(file.readline().strip())
            test['uai_path'] = validator.get_valid_path(file.readline().strip())
            return test
