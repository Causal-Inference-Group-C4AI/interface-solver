import os
import sys
import time
from typing import Tuple

import pandas as pd

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

from lcn.inference.exact.marginal import ExactInferece  # type: ignore
from lcn.model import LCN
from utils._enums import DirectoryPaths, Solvers
from utils.file_generators.lcn_file_generator import create_lcn
from utils.output_writer import OutputWriterLCN
from utils.general_utilities import solver_parse_arguments, get_common_data, configure_environment, log_solver_error
from utils.validator import Validator
from utils.solver_results import SolverResultsFactory, ATE

from flask import Flask, request, jsonify 

app = Flask(__name__)

def lcn_solver(
        test_name: str,
        edges: str,
        unobservables: str,
        csv_path: str,
        treatment: str,
        outcome: str) -> Tuple[float, float]:
    """Solver for causal inference problem using LCN.

    Args:
        test_name (str): The name of the test case.
        edges (str): A string representing the edges of the causal graph.
        unobservables (str): A string representing the unobservables of the
            causal graph.
        csv_path (str): The path to the CSV file containing the data.
        treatment (str): The treatment variable.
        outcome (str): The outcome variable.
    """
    print("LCN solver running...")

    # Setting up the file to write the output
    output_file = f"{DirectoryPaths.OUTPUTS.value}/{test_name}/{Solvers.LCN.value}_{test_name}.txt"
    writer = OutputWriterLCN(output_file)

    # Defining the first intervention
    intervention_input = (outcome, treatment, 1)

    # Loading the data
    data = pd.read_csv(csv_path)

    # Extract nodes from CSV
    nodes = data.columns.tolist()

    # Couting each configuration of the variables
    data_counts = data.value_counts().reset_index()
    data_counts.columns = nodes + ['value_counts']

    # Computing probabilities
    data_counts['prob'] = data_counts['value_counts'] / \
        data_counts['value_counts'].sum()

    # Creating the empirical distributions
    empirical_distributions = []
    for index, row in data_counts.iterrows():
        config = row[nodes].values
        prob = row['prob']
        empirical_distributions.append((config, prob))

    # Defining the order of the variables
    var_order = nodes

    # Creating the first LCN file
    output_file_1 = f"{test_name}_{treatment}1.lcn"

    writer.silent_run(
        lambda: create_lcn(
            edges, unobservables, intervention_input,
            empirical_distributions, var_order, output_file_1
        ), new=True
    )
    writer("==============================================")

    # Defining the second intervention
    intervention_input = (outcome, treatment, 0)

    # Creating the second LCN file
    output_file_0 = f"{test_name}_{treatment}0.lcn"

    writer.silent_run(lambda: create_lcn(
        edges, unobservables, intervention_input,
        empirical_distributions, var_order, output_file_0
    ))
    writer("==============================================")

    # Creating the first LCN object
    l1 = LCN()
    writer.silent_run(lambda: l1.from_lcn(file_name=output_file_1))

    # Defining the first query
    query = f"{outcome}L"
    algo1 = ExactInferece(lcn=l1)

    # Running the first query
    writer.silent_run(lambda: algo1.run(query_formula=query))
    writer("==============================================")
    writer("Bounds for the first intervention")
    writer(f"[{algo1.lower_bound}, {algo1.upper_bound}]")
    writer("==============================================")

    # Creating the second LCN object
    l0 = LCN()
    writer.silent_run(lambda: l0.from_lcn(file_name=output_file_0))

    # Defining the second query
    algo0 = ExactInferece(lcn=l0)

    # Running the second query
    writer.silent_run(lambda: algo0.run(query_formula=query))
    writer("==============================================")
    writer("Bounds for the second intervention")
    writer(f"[{algo0.lower_bound}, {algo0.upper_bound}]")
    writer("==============================================")

    # Calculating the bounds for the ATE
    ate_lower_bound = algo1.lower_bound - algo0.upper_bound
    ate_upper_bound = algo1.upper_bound - algo0.lower_bound

    writer("Bounds for the ATE")
    writer(f"[{ate_lower_bound}, {ate_upper_bound}]")
    writer("==============================================")

    print("LCN solver Done.")
    return ate_lower_bound, ate_upper_bound


def run_lcn_solver(data):
    """Runs the LCN solver."""
    return lcn_solver(
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
        lower_bound, upper_bound = run_lcn_solver(data)
        time_taken = time.time() - start_time

        solver_result = SolverResultsFactory().get_solver_results_object(Solvers.LCN.value, data['test_name'])
        solver_result.log_solver_results(ATE((lower_bound, upper_bound)), time_taken)

        return jsonify({
            "status": "success",
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "time_taken": time_taken
        }), 200
    except Exception as e:
        log_solver_error(e, "lcn", data['test_name'])
        return jsonify({"error": str(e), "error_code": "SOLVER_FAILED"}), 500

def main():
    """Main function to execute the LCN solver."""
    args = solver_parse_arguments()

    configure_environment(args.verbose)

    validator = Validator()
    data = get_common_data(validator.get_valid_path(args.common_data))

    start_time = time.time()
    lower_bound, upper_bound = run_lcn_solver(data)
    end_time = time.time()
    time_taken = end_time - start_time

    solver_result = SolverResultsFactory().get_solver_results_object(Solvers.LCN.value, data['test_name'])
    solver_result.log_solver_results(ATE((lower_bound, upper_bound)), time_taken)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
