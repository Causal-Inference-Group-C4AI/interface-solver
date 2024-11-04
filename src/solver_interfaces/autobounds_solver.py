import contextlib
import glob
import os
import warnings

import numpy as np
import pandas as pd

from autobounds.causalProblem import causalProblem
from autobounds.DAG import DAG
from utils.output_writer import OutputWriterAutobounds


warnings.simplefilter(action='ignore')


def cleanup_logs():
    """Remove all log files in the current directory."""
    log_files = glob.glob(".*.log")
    for log_file in log_files:
        try:
            os.remove(log_file)
        except Exception as e:
            print(f"Error deleting {log_file}: {e}")


def silent_run(func, output_file=None, new=False, ):
    """Run a function and redirect output to a specified file.

    Args:
        func (function): The function to run.
        output_file (str, optional): The file path to redirect output to. Defaults to None.
        new (bool, optional): Whether to write a new file or append to an existing one. Defaults to False.
    """
    mode = "w" if new else "a"
    if output_file:
        with open(output_file, mode) as f:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                return func()
    else:
        with open(os.devnull, 'w') as fnull:
            with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
                return func()


def autobounds_solver(
        test_name,
        edges,
        unobservables,
        csv_path,
        treatment,
        outcome):
    """Solver for causal inference problem using AutoBounds.

    Args:
        test_name (str): The name of the test case.
        edges (str): A string representing the edges of the causal graph.
        unobservables (str): A string representing the unobservables of the causal graph.
        csv_path (str): The path to the CSV file containing the data.
        treatment (str): The treatment variable.
        outcome (str): The outcome variable.
    """
    # Create a DAG object from the edges and unobservables
    dag = DAG()
    dag.from_structure(edges=edges, unob=unobservables)

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
    output_file = f"outputs/{test_name}/autobounds_{test_name}.txt"
    write = OutputWriterAutobounds(output_file)

    # Calculating bounds
    problem.set_ate(ind=treatment, dep=outcome)
    prog_ate = silent_run(lambda: problem.write_program(),
                          output_file=output_file, new=True)
    prog_ate_optim = silent_run(
        lambda: prog_ate.run_scip(), output_file=output_file)

    # Extracting bounds
    lower_bound = np.round(prog_ate_optim[0]['dual'], 3)
    upper_bound = np.round(prog_ate_optim[1]['dual'], 3)
    write("==============================================")
    write(f"Causal effect lies in the interval [{lower_bound}, {upper_bound}]")
    write("==============================================")


# Example usage
if __name__ == "__main__":
    edges = "Z -> X, X -> Y, Uxy -> X, Uxy -> Y"
    unobservables = "Uxy"
    csv_path = 'data/csv/balke_pearl.csv'
    autobounds_solver('balke_pearl', edges, unobservables, csv_path, 'X', 'Y')
    cleanup_logs()
