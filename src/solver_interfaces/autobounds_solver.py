import contextlib
import glob
import os
import warnings

import numpy as np
import pandas as pd
from autobounds.causalProblem import causalProblem
from autobounds.DAG import DAG


warnings.simplefilter(action='ignore')


def cleanup_logs():
    """Remove all log files in the current directory."""
    log_files = glob.glob("*.log")
    for log_file in log_files:
        try:
            os.remove(log_file)
        except Exception as e:
            print(f"Error deleting {log_file}: {e}")


def write_output(output, output_path="outputs/autobounds_output.txt", new=False):
    """Write the output to a file.

    Args:
        output (str): The output to write to the file.
        output_path (str, optional): The path to the output file. Defaults to "outputs/autobounds_output.txt".
        new (bool, optional): Whether to write a new file or append to an existing one. Defaults to False.
    """
    mode = "w" if new else "a"
    with open(output_path, mode) as f:
        f.write(output + "\n")


def silent_run(func, output_file=None, new=False):
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


def autobounds_solver(test_name, edges, unobservables, csv_path):
    """Solver for causal inference problem using AutoBounds.

    Args:
        edges (str): A string representing the edges of the causal graph.
        unobservables (str): A string representing the unobservables of the causal graph.
        csv_path (str): The path to the CSV file containing the data.
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

    output_file = f"outputs/{test_name}/autobounds_{test_name}.txt"

    # Calculating bounds
    problem.set_ate(ind="X", dep="Y")
    prog_ate = silent_run(lambda: problem.write_program(), output_file=output_file, new=True)
    prog_ate_optim = silent_run(lambda: prog_ate.run_scip(), output_file=output_file)

    # Extracting bounds
    lower_bound = np.round(prog_ate_optim[0]['dual'], 3)
    upper_bound = np.round(prog_ate_optim[1]['dual'], 3)
    write_output("==============================================", output_path=output_file)
    write_output(f"Causal effect lies in the interval [{lower_bound}, {upper_bound}]", output_path=output_file)
    write_output("==============================================", output_path=output_file)


# Example usage
if __name__ == "__main__":
    edges = "Z -> X, X -> Y, Uxy -> X, Uxy -> Y"
    unobservables = "Uxy"
    csv_path = 'autobounds_demo/balke_pearl.csv'
    autobounds_solver(edges, unobservables, csv_path)
    cleanup_logs()
