import glob
import os
import warnings

import numpy as np
import pandas as pd
from autobounds.causalProblem import causalProblem
from autobounds.DAG import DAG
from utils.output_writer import OutputWriterAutobounds
from utils.silent_run import silent_run

warnings.simplefilter(action='ignore')


def cleanup_logs():
    """Remove all log files in the current directory."""
    log_files = glob.glob(".*.log")
    for log_file in log_files:
        try:
            os.remove(log_file)
        except Exception as e:
            print(f"Error deleting {log_file}: {e}")

def autobounds_solver(
        test_name: str,
        edges: str,
        unobservables: str,
        csv_path: str,
        treatment: str,
        outcome: str):
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

    cleanup_logs()


# Example usage
if __name__ == "__main__":
    edges = "Z -> X, X -> Y, Uxy -> X, Uxy -> Y"
    unobservables = "Uxy"
    csv_path = 'data/csv/balke_pearl.csv'
    autobounds_solver('balke_pearl', edges, unobservables, csv_path, 'X', 'Y')
