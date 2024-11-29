import argparse
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

def log_solver_results(solver_name: str, test_name: str, ate: Dict | Tuple[float, float], time_taken):
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
        writer(f"--------------------------------------------")
    else:
        lower_bound = ate[0]
        upper_bound = ate[1]
        writer(f"   ATE lies in the interval: [{lower_bound}, {upper_bound}]")
        writer("--------------------------------------------")


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