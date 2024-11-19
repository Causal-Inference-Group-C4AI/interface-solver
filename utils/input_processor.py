import os
import logging
import argparse
from typing import Dict
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


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


def generate_common_data(output_path, input_path):
    processed_data = InputProcessor(input_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(processed_data.data_test, f)
    print(f"Data generated at {output_path}")

if __name__ == "__main__":
    print("Running Input Processor...")
    logging.getLogger().setLevel(logging.CRITICAL)
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Path to output the processed data")
    parser.add_argument("--input", required=True, help="Path to input data")
    args = parser.parse_args()
    generate_common_data(args.output, args.input)
    print("Input processor Done!")
