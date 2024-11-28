import argparse
import json
import os
import sys
from typing import Dict

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../')))

from utils._enums import Solvers
from utils.file_generators.parser_uai import UAIParser
from utils.file_generators.uai_generator import UAIGenerator
from utils.suppressors import suppress_print
from utils.validator import InvalidInputFormatError, Validator


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
            csv_path = parser.generate_data(data_test['test_name'])
            data_test['csv_path'] = validator.get_valid_csv_path(csv_path)

        if (data_test['uai_path'] is None) and \
           (Solvers.BCAUSE.value in data_test['solvers']):
            uai = UAIGenerator(data_test['test_name'], data_test['edges']
                               ['edges_str'], data_test['csv_path'])
            data_test['uai_path'] = validator.get_valid_uai_path(uai.uai_path)
            data_test['uai_mapping'] = validator.get_valid_mapping(
                uai.get_mapping_str())
        data_test['nodes'] = validator.get_nodes(
            data_test['edges']['edges_str'])
        data_test['unobservables'] = validator.get_unobservables(
            data_test['nodes'], data_test['csv_path'])
        return data_test

    def get_input_data(self) -> Dict:
        data_test = {}
        validator = Validator()
        self.input_path = validator.get_valid_path(self.input_path)
        try:
            with open(self.input_path, 'r') as file:
                data_test['test_name'] = validator.get_valid_test_name(
                    file.readline().strip())
                data_test['solvers'] = validator.get_valid_solver_list(
                    file.readline().strip())

                data_test['edges'] = {}
                edges_str, edges_list = validator.get_valid_edges_in_string(
                    file.readline().strip())
                data_test['edges']['edges_str'] = edges_str
                data_test['edges']['edges_list'] = edges_list

                data_test['treatment'] = validator.get_valid_variable(
                    file.readline().strip(), edges_str)
                data_test['outcome'] = validator.get_valid_variable(
                    file.readline().strip(), edges_str)

                data_test['csv_path'] = None
                data_test['uai_path'] = None
                data_test['uai_mapping'] = None
                for _ in range(3):
                    line = file.readline().strip()
                    if line.endswith('.csv'):
                        data_test['csv_path'] = validator.get_valid_csv_path(
                            line)
                    elif line.endswith('.uai'):
                        data_test['uai_path'] = validator.get_valid_uai_path(
                            line)
                    elif line != "" and line != "\n":
                        data_test['uai_mapping'] = validator.get_valid_mapping(
                            line)

                if not data_test['csv_path'] and not data_test['uai_path']:
                    raise InvalidInputFormatError(
                        "Invalid input format: There should be at least a " +
                        ".csv or a .uai file path."
                    )
                if (data_test['uai_mapping'] is None) ^ \
                   (data_test['uai_path'] is None):
                    raise InvalidInputFormatError(
                        "Invalid input format: .uai file and uai mapping " +
                        "should come together."
                    )
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True,
                        help="Path to output the processed data")
    parser.add_argument("--input", required=True, help="Path to input data")
    args = parser.parse_args()

    processed_data = InputProcessor(args.input)
    generate_shared_data(args.output, processed_data.data_test)

    print("Input processor Done!")
