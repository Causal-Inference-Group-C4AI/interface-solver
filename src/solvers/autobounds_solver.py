import argparse
import os
import sys
import time
from typing import Tuple

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

from autobounds.causalProblem import causalProblem
from autobounds.DAG import DAG
from utils._enums import DirectoryPaths
from utils.get_common_data import get_common_data
from utils.output_writer import OutputWriter, OutputWriterAutobounds
from utils.suppress_warnings import suppress_warnings
from utils.validator import Validator


def autobounds_solver(
        test_name: str,
        edges: str,
        unobservables: str,
        csv_path: str,
        treatment: str,
        outcome: str) -> Tuple[float, float]:
    """Solver for causal inference problem using AutoBounds.

    Args:
        test_name (str): The name of the test case.
        edges (str): A string representing the edges of the causal graph.
        unobservables (str): A string representing the unobservables
            of the causal graph.
        csv_path (str): The path to the CSV file containing the data.
        treatment (str): The treatment variable.
        outcome (str): The outcome variable.
    """
    print("Autobounds solver running...")
    # Create a DAG object from the edges and unobservables
    dag = DAG()
    if unobservables:
        dag.from_structure(edges=edges, unob=unobservables)
    else:
        dag.from_structure(edges=edges)

    # Loading the data
    data = pd.read_csv(csv_path)

    # Extract nodes from CSV
    nodes = data.columns.tolist()

    # Computing probabilities
    dat = pd.DataFrame(data.groupby(nodes).value_counts()).reset_index()
    dat['prob'] = dat['count'] / dat['count'].sum()
    dat = dat.drop(columns=['count'])

    # Create a causalProblem object
    problem = causalProblem(dag)
    problem.load_data(dat)

    # Adding problem constraints
    problem.add_prob_constraints()

    # Setting up the file to write the output
    output_file = (
        f"{DirectoryPaths.OUTPUTS.value}/{test_name}/"
        f"autobounds_{test_name}.txt"
    )
    writer = OutputWriterAutobounds(output_file)

    try:
        # Calculating bounds
        problem.set_ate(ind=treatment, dep=outcome)
        prog_ate = writer.silent_run(lambda: problem.write_program(), new=True)
        prog_ate_optim = writer.silent_run(lambda: prog_ate.run_scip())

        # Extracting bounds
        lower_bound = np.round(prog_ate_optim[0]['dual'], 3)
        upper_bound = np.round(prog_ate_optim[1]['dual'], 3)
        writer("==============================================")
        writer(
            f"Causal effect lies in the interval "
            f"[{lower_bound}, {upper_bound}]")
        writer("==============================================")
    except Exception as e:
        if "unsupported operand type(s) for -: 'str' and 'str'" in str(e):
            pass
        else:
            raise Exception(e)

    print("Autobounds solver Done.")
    return lower_bound, upper_bound


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--common_data", required=True,
                        help="Path to common data")
    parser.add_argument(
        "--verbose", action="store_true", help="Show solver logs"
    )
    args = parser.parse_args()
    validator = Validator()
    data = get_common_data(validator.get_valid_path(args.common_data))

    if not args.verbose:
        suppress_warnings()

    start_time = time.time()
    lower_bound, upper_bound = autobounds_solver(
        test_name=data['test_name'],
        edges=data['edges']['edges_str'],
        unobservables=data['unobservables'],
        csv_path=data['csv_path'],
        treatment=data['treatment'],
        outcome=data['outcome'],
    )
    end_time = time.time()

    time_taken = end_time - start_time
    print(f"Time taken by Autobounds: {time_taken:.6f} seconds")

    overview_file_path = (
        f"{DirectoryPaths.OUTPUTS.value}/{data['test_name']}/overview.txt"
    )
    writer = OutputWriter(overview_file_path, reset=False)
    writer("Autobounds")
    writer(f"   Time taken by Autobounds: {time_taken:.6f} seconds")
    writer(f"   ATE lies in the interval: [{lower_bound}, {upper_bound}]")
    writer("--------------------------------------------")
