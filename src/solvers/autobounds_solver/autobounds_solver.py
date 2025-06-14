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
from utils.output_writer import OutputWriterAutobounds
from utils.general_utilities import configure_environment, log_solver_error, get_common_data
from utils.validator import Validator
from utils.solver_error import SolverError, InfeasibleProblemError
from utils.solver_results import ATE, SolverResultsFactory
from flask import Flask, request, jsonify 

app = Flask(__name__)

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
        if "dual" in str(e) or "unsupported operand type(s) for -: 'str' and 'str'" in str(e):
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

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/solve', methods=['POST'])
def solve_endpoint():

    json_input = request.get_json()

    configure_environment(json_input['verbose'])

    validator = Validator()
    data = get_common_data(validator.get_valid_path(json_input['common_data']))
    
    
    try:
        start_time = time.time()
        lower_bound, upper_bound = run_autobounds_solver(data)
        time_taken = time.time() - start_time

        solver_result = SolverResultsFactory().get_solver_results_object(Solvers.AUTOBOUNDS.value, data['test_name'])
        solver_result.log_solver_results(ATE((lower_bound, upper_bound)), time_taken)

        return jsonify({
            "status": "success",
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "time_taken": time_taken
        }), 200
    except Exception as e:
        log_solver_error(e, "autobounds", data['test_name'])
        return jsonify({"error": str(e), "error_code": "SOLVER_FAILED"}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5004)
