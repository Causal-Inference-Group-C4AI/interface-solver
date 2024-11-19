import argparse
import json
import logging
import os
import sys
from io import TextIOWrapper

from typing import Any, Dict, Tuple, Union

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


from utils.validator import Validator
from utils.file_generators.parser_uai import UAIParser
from utils.file_generators.uai_generator import UAIGenerator
from utils.suppress_print import suppress_print

class InputProcessor:
    def __init__(self, input_path: str):
        self.input_path = input_path
        self.data_test = self.process_test_data()

    @suppress_print
    def get_files(
        self,
        test: Dict[str, Any],
        file: TextIOWrapper
    ) -> Tuple[Union[Dict, None], str, Union[str, None]]:
        val = Validator()
        first_line = val.get_valid_path(file.readline().strip())

        if first_line.endswith('.csv'):
            csv_path = first_line
            if 'bcause' in test['solvers']:
                second_line = file.readline().strip()
                if not ('.' in second_line):
                    uai = UAIGenerator(test['test_name'], test['edges']
                                    ['edges_str'], csv_path)
                    uai_path = val.get_valid_uai_path(uai.uai_path)
                    uai_mapping = val.get_valid_mapping(
                        uai.get_mapping_str())
                else:
                    uai_path = val.get_valid_uai_path(second_line)
                    uai_mapping = val.get_valid_mapping(file.readline().strip())
            else:
                uai_path = None
                uai_mapping = None
        else:
            uai_path = val.get_valid_uai_path(first_line, False)
            uai_mapping = val.get_valid_mapping(file.readline().strip())
            nodes = list(uai_mapping.values())
            parser = UAIParser(first_line, nodes)
            parser.parse()
            csv_path = val.get_valid_csv_path(
                parser.generate_data(test['test_name']))

        return uai_mapping, csv_path, uai_path


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
