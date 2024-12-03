import os
import sys
import time
from typing import List, Tuple

import pandas as pd

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

from bcause.inference.causal.multi import EMCC
from bcause.models.cmodel import StructuralCausalModel

from utils._enums import DirectoryPaths, Solvers
from utils.general_utilities import (configure_environment, log_solver_results,
                                     solver_parse_arguments)
from utils.get_common_data import get_common_data
from utils.output_writer import OutputWriterBcause
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
        f"{DirectoryPaths.OUTPUTS.value}/{test_name}/"
        f"{Solvers.BCAUSE.value}_{test_name}.txt"
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


def main():
    """Main function to execute the Bcause solver."""
    args = solver_parse_arguments()

    configure_environment(args.verbose)

    validator = Validator()
    data = get_common_data(validator.get_valid_path(args.common_data))

    start_time = time.time()
    lower_bound, upper_bound = run_bcause_solver(data)
    time_taken = time.time() - start_time

    log_solver_results(Solvers.BCAUSE.value, data['test_name'], [
                       lower_bound, upper_bound], time_taken)


if __name__ == "__main__":
    main()
