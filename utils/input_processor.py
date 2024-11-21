import argparse
import json
import logging
import os
import sys
from io import TextIOWrapper

from typing import Any, Dict, Tuple, Union

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from utils._enums import Solvers
from utils.validator import Validator, InvalidInputFormatError
from utils.file_generators.parser_uai import UAIParser
from utils.file_generators.uai_generator import UAIGenerator
from utils.suppress_print import suppress_print

class InputProcessor:
    def __init__(self, input_path: str):
        self.input_path = input_path
        self.data_test = self.process_input_data()

    @suppress_print
    def process_input_data(self) -> Dict:
        data_test = self.get_input_data()
        validator = Validator()
        if data_test['csv_path'] is None:
            nodes = list(data_test['uai_mapping'].values())
            parser = UAIParser(data_test["uai_path"], nodes)
            parser.parse()
            data_test['csv_path'] = validator.get_valid_csv_path(
                parser.generate_data(data_test['test_name']))

        if data_test['uai_path'] is None and Solvers.BCAUSE.value in data_test['solvers']:
            uai = UAIGenerator(data_test['test_name'], data_test['edges']
                                ['edges_str'], data_test['csv_path'])
            data_test['uai_path'] = validator.get_valid_uai_path(uai.uai_path)
            data_test['uai_mapping'] = validator.get_valid_mapping(uai.get_mapping_str())
        return data_test


    def get_input_data(self) -> Dict:
        data_test = {}
        validator = Validator()
        self.input_path = validator.get_valid_path(self.input_path)
        try:
            with open(self.input_path, 'r') as file:
                data_test['test_name'] = validator.get_valid_test_name(file.readline().strip())
                data_test['solvers'] = validator.get_valid_solver_list(file.readline().strip())

                data_test['edges'] = {}
                edges_str, edges_list = validator.get_valid_edges_in_string(file.readline().strip())
                data_test['edges']['edges_str'] = edges_str
                data_test['edges']['edges_list'] = edges_list

                data_test['treatment'] = validator.get_valid_variable(file.readline().strip(), edges_str)
                data_test['outcome'] = validator.get_valid_variable(file.readline().strip(), edges_str)
                data_test['unobservables'] = validator.get_valid_unobservables(file.readline().strip(), edges_str)

                first_file_line = validator.get_valid_path(file.readline().strip())
                if first_file_line.endswith('.csv'):
                    data_test['csv_path'] = first_file_line
                    next_file_line = file.readline()
                    if next_file_line == "" or next_file_line == "\n":
                        data_test['uai_path'], data_test['uai_mapping'] = None, None
                    else:
                        data_test['uai_path'] = validator.get_valid_uai_path(file.readline())
                        data_test['uai_mapping'] = validator.get_valid_mapping(file.readline().strip())
                else:
                    data_test['csv_path'] = None
                    data_test['uai_path'] = validator.get_valid_uai_path(first_file_line, False)
                    data_test['uai_mapping'] = validator.get_valid_mapping(file.readline().strip())

                return data_test

        except Exception as e:
            raise InvalidInputFormatError(f"Invalid input format: {e}.") from e


def generate_shared_data(output_path: str, data_test: Dict):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data_test, f)
    print(f"Data generated at {output_path}")


if __name__ == "__main__":
    print("Running Input Processor...")
    logging.getLogger().setLevel(logging.CRITICAL)
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Path to output the processed data")
    parser.add_argument("--input", required=True, help="Path to input data")
    args = parser.parse_args()

    processed_data = InputProcessor(args.input)

    generate_shared_data(args.output, processed_data.data_test)

    print("Input processor Done!")
