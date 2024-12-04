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
from utils._enums import DirectoryPaths, Solvers
from utils.get_common_data import get_common_data
from utils.output_writer import OutputWriterAutobounds
from utils.general_utilities import solver_parse_arguments, log_solver_results, configure_environment, log_solver_error
from utils.validator import Validator
from utils.solver_error import SolverError, InfeasibleProblemError


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
        f"{Solvers.AUTOBOUNDS.value}_{test_name}.txt"
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
            raise InfeasibleProblemError()
        else:
            raise SolverError(f"Unexpected error in autobounds_solver: {e}")

    print("Autobounds solver Done.")
    return lower_bound, upper_bound


def run_autobounds_solver(data):
    return autobounds_solver(
        test_name=data['test_name'],
        edges=data['edges']['edges_str'],
        unobservables=data['unobservables'],
        csv_path=data['csv_path'],
        treatment=data['treatment'],
        outcome=data['outcome'],
    )

def main():
    """Main function to execute the Autobounds solver."""
    args = solver_parse_arguments()

    configure_environment(args.verbose)

    validator = Validator()
    data = get_common_data(validator.get_valid_path(args.common_data))

    try:
        start_time = time.time()
        lower_bound, upper_bound = run_autobounds_solver(data)
        time_taken = time.time() - start_time

        log_solver_results(Solvers.AUTOBOUNDS.value, data['test_name'], [lower_bound, upper_bound], time_taken)
    except Exception as e:
        log_solver_error(e, "autobounds", data['test_name'])
        # TODO: LOGGING NÃO FUNCIONANDO
        print(e)

if __name__ == "__main__":
    main()
