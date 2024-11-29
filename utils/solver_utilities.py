import argparse
import os
import sys
from typing import Dict, Tuple

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

from utils._enums import DirectoryPaths, Solvers
from utils.suppressors import suppress_warnings
from utils.output_writer import OutputWriter

class SolverUtilities:
    def __init__(self):
        pass

    def configure_environment(self, is_verbose: bool):
        """Configures the runtime environment."""
        if not is_verbose:
            suppress_warnings()

    def parse_arguments(self):
        """Parses command-line arguments."""
        parser = argparse.ArgumentParser()
        parser.add_argument("--common_data", required=True,
                            help="Path to common data")
        parser.add_argument(
            "--verbose", action="store_true", help="Show solver logs"
        )
        parser.add_argument("--fast", action="store_true", help="Run in fast mode")
        return parser.parse_args()

    def log_solver_results(self, solver_name: str, test_name: str, ate: Dict | Tuple[float, float], time_taken):
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
