import argparse
import logging
import os
import sys
import time
from typing import Tuple

import pandas as pd

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

from bcause.inference.causal.multi import EMCC
from bcause.models.cmodel import StructuralCausalModel

from utils._enums import DirectoryPaths
from utils.get_common_data import get_common_data
from utils.output_writer import OutputWriter, OutputWriterBcause
from utils.suppressors import suppress_warnings
from utils.validator import Validator


def bcause_solver(
        test_name: str,
        uai_path: str,
        csv_path: str,
        treatment: str,
        outcome: str,
        mapping: dict) -> Tuple[float, float]:
    print("Bcause solver running...")
    model = StructuralCausalModel.read(uai_path)
    renamed_model = model.rename_vars(mapping)

    dataset = pd.read_csv(csv_path)
    inf = EMCC(renamed_model, dataset, max_iter=100, num_runs=20)

    p_do0 = inf.causal_query(outcome, do={treatment: 0})
    p_do1 = inf.causal_query(outcome, do={treatment: 1})

    lower_bound = p_do1.values[1] - p_do0.values[1]
    upper_bound = p_do1.values[3] - p_do0.values[3]

    output_file = (
        f"{DirectoryPaths.OUTPUTS.value}/{test_name}/bcause_{test_name}.txt"
    )
    writer = OutputWriterBcause(output_file)

    writer("==============================================")
    writer(
        f'P({outcome}=1|do({treatment}=0)) = '
        f'{[p_do0.values[1], p_do0.values[3]]}')
    writer(
        f'P({outcome}=1|do({treatment}=1)) = '
        f'{[p_do1.values[1], p_do1.values[3]]}')
    writer(
        f"Causal effect lies in the interval [{lower_bound}, {upper_bound}]")
    writer("==============================================")
    print("Bcause solver Done.")
    return lower_bound, upper_bound


def configure_environment(is_verbose: bool):
    """Configures the runtime environment."""
    if not is_verbose:
        suppress_warnings()

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--common_data", required=True,
                        help="Path to common data")
    parser.add_argument(
        "--verbose", action="store_true", help="Show solver logs"
    )
    return parser.parse_args()


def run_bcause_solver(data):
    """Runs the Bcause solver."""
    return bcause_solver(
        test_name=data['test_name'],
        uai_path=data['uai_path'],
        csv_path=data['csv_path'],
        treatment=data['treatment'],
        outcome=data['outcome'],
        mapping=data['uai_mapping'],
    )


def log_solver_results(test_name, lower_bound, upper_bound, time_taken):
    """Logs the results of the solver."""
    print(f"Time taken by Bcause: {time_taken:.6f} seconds")

    overview_file_path = (
        f"{DirectoryPaths.OUTPUTS.value}/{data['test_name']}/overview.txt"
    )
    writer = OutputWriter(overview_file_path, reset=False)
    writer("Bcause")
    writer(f"   Time taken by Bcause: {time_taken:.6f} seconds")
    writer(f"   ATE lies in the interval: [{lower_bound}, {upper_bound}]")
    writer("--------------------------------------------")


def main():
    """Main function to execute the Bcause solver."""
    args = parse_arguments()

    configure_environment(args.verbose)

    validator = Validator()
    data = get_common_data(validator.get_valid_path(args.common_data))

    start_time = time.time()
    lower_bound, upper_bound = run_bcause_solver(data)
    time_taken = time.time() - start_time

    log_solver_results(data['test_name'], lower_bound, upper_bound, time_taken)

if __name__ == "__main__":
    main()
