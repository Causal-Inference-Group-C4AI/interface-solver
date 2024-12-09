import argparse
import logging
import os
import sys
from typing import Dict, Tuple

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

from utils._enums import DirectoryPaths, Solvers
from utils.output_writer import OutputWriter
from utils.suppressors import suppress_warnings


def configure_environment(is_verbose: bool):
    """Configures the runtime environment."""
    if not is_verbose:
        suppress_warnings()


def input_parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Runs tests of Causal Effect under Partial-Observability."
    )
    parser.add_argument('file_path',
                        help='The path to the file you want to read'
                        )
    parser.add_argument('-v', '--verbose',
                        action='store_true', help="Show solver logs")
    parser.add_argument('-f', '--fast', action='store_true',
                        help="Run the script with fast settings")
    parser.add_argument('-r', '--reset', action='store_true',
                        help="Reset the output file")
    return parser.parse_args()


def input_processor_parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True,
                        help="Path to output the processed data")
    parser.add_argument("--input", required=True, help="Path to input data")
    return parser.parse_args()


def solver_parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--common_data", required=True, help="Path to common data"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show solver logs"
    )
    parser.add_argument(
        "-f", "--fast", action="store_true", help="Run in fast mode"
    )

    parser.add_argument(
        "-d", "--debug", action="store_true", help="Debug mode"
    )
    return parser.parse_args()


def log_solver_results(
    solver_name: str,
    test_name: str,
    ate: Dict | Tuple[float, float],
    time_taken
):
    """Logs the results of the solver."""
    print(f"Time taken by {solver_name}: {time_taken:.6f} seconds")

    overview_file_path = (
        f"{DirectoryPaths.OUTPUTS.value}/{test_name}/overview.txt"
    )
    writer = OutputWriter(overview_file_path, reset=False)

    writer(f"{solver_name}")
    writer(f"   Time taken by {solver_name}: {time_taken:.6f} seconds")

    if solver_name is Solvers.DOWHY.value:
        for method, ate in ate.items():
            writer(f"   Estimate method: {method}")
            writer(f"   ATE is: {ate}")
        writer("--------------------------------------------")
    else:
        lower_bound = ate[0]
        upper_bound = ate[1]
        writer(f"   ATE lies in the interval: [{lower_bound}, {upper_bound}]")
        writer("--------------------------------------------")


def log_solver_error(e, solver_name: str, test_name: str):
    msg = f"Solver {solver_name} failed with error: {e}"
    output_file = (
        f"{DirectoryPaths.OUTPUTS.value}/{test_name}/"
        f"{solver_name}_{test_name}.txt"
    )
    solver_writer = OutputWriter(output_file, reset=False)
    solver_writer("=============================================")
    solver_writer(msg)

    overview_file_path = (
        f"{DirectoryPaths.OUTPUTS.value}/{test_name}/overview.txt"
    )
    overview_writer = OutputWriter(overview_file_path, reset=False)

    overview_writer(f"{solver_name}")
    overview_writer(f"   {msg}")
    overview_writer("--------------------------------------------")

    logging.error(msg)


def get_debug_data_for_dowhy():
    return {
        "test_name": "balke_pearl",
        "csv_path": "data/inputs/csv/balke_pearl.csv",
        "edges": {
            "edges_list": [("Z", "X"), ("X", "Y"), ("U", "X"), ("U", "Y")],
        },
        "treatment": "X",
        "outcome": "Y"
    }
