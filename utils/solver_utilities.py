import argparse
import os
import sys
import time
from typing import Dict, List, Tuple

import networkx as nx
import numpy as np
import pandas as pd
from dowhy import CausalModel

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

from utils._enums import DirectoryPaths, Solvers
from utils.get_common_data import get_common_data
from utils.output_writer import OutputWriter, OutputWriterDoWhy
from utils.suppressors import suppress_warnings
from utils.validator import Validator

class SolverUtilities:
    def __init__(self, directory_paths, output_writer):
        self.directory_paths = directory_paths
        self.output_writer = output_writer

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
        return parser.parse_args()

    def log_solver_results(self, solver_name: str, test_name: str, ate: Any[Dict, Tuple[float, float]], time_taken):
        """Logs the results of the solver."""
        print(f"Time taken by {solver_name}: {time_taken:.6f} seconds")

        overview_file_path = (
            f"{self.directory_paths.OUTPUTS.value}/{test_name}/overview.txt"
        )
        writer = self.output_writer(overview_file_path, reset=False)

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
