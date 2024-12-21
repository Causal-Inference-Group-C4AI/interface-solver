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
from utils.output_writer import OutputWriterDoWhy
from utils.general_utilities import  get_common_data, configure_environment, log_solver_error
from utils.validator import Validator
from utils.solver_results import ATE, SolverResultsFactory
from flask import Flask, request, jsonify 

app = Flask(__name__)


def get_estimands(identified_estimand) -> List[str]:
    estimands = []
    for estimand, value in identified_estimand.estimands.items():
        if estimand in ["backdoor", "iv", "frontdoor"] and value is not None:
            estimands.append(estimand)
    return estimands


def load_data_and_graph(csv_path: str, edges: List[Tuple[str, str]]) -> Tuple[pd.DataFrame, nx.DiGraph]:
    """Loads data from a CSV file and creates a causal graph."""
    data = pd.read_csv(csv_path)
    graph = nx.DiGraph(edges)
    return data, graph


def get_estimation_and_refutation_methods(fast_mode: bool):
    estimation_methods = {
        "backdoor": [
            "linear_regression"
        ],
        "iv": [
            "instrumental_variable"
        ],
        "frontdoor": []
    }

    refutation_methods = [
        "placebo_treatment_refuter",
        "dummy_outcome_refuter"
    ]

    if not fast_mode:
        estimation_methods["backdoor"].extend([
            "propensity_score_matching",
            "propensity_score_stratification",
            "propensity_score_weighting"
        ])
        refutation_methods.extend([
            "random_common_cause",
            "data_subset_refuter"
        ])

    return estimation_methods, refutation_methods


def perform_estimations_and_refutations(
    model: CausalModel,
    identified_estimand,
    estimands: List[str],
    writer,
    fast: bool
) -> Dict[str, float]:
    """Performs causal effect estimations and refutations."""

    estimation_methods, refutation_methods = get_estimation_and_refutation_methods(fast)

    methods_estimate = {}
    for estimand in estimands:
        for method in estimation_methods.get(estimand, []):
            method_name = f"{estimand}.{method}"
            writer("-" * 80)
            try:
                estimate = estimate_effect(model, identified_estimand, method_name, writer)
                methods_estimate[str(method_name)] = float(estimate.value)
                refute_effect(model, identified_estimand, estimate, refutation_methods, writer)
            except Exception as e:
                writer(f"Failed to estimate using {method_name}: {str(e)}")
    return methods_estimate


def estimate_effect(model, identified_estimand, method_name: str, writer) -> object:
    """Estimates the causal effect using a specified method."""
    start_time = time.time()
    estimate = model.estimate_effect(
        identified_estimand,
        method_name=method_name,
        test_significance=True,
        confidence_intervals=True
    )
    end_time = time.time()
    time_taken = end_time - start_time
    writer(f"Estimation using {method_name}:")
    writer(f"Time taken: {time_taken:.6f} seconds")
    writer(f"ATE = {estimate.value}")

    # Log p-value and confidence interval
    log_estimation_results(estimate, writer)
    return estimate


def log_estimation_results(estimate, writer):
    """Logs estimation results including p-value and confidence intervals."""
    p_value = estimate.test_stat_significance()["p_value"]
    writer(f"P-value: {p_value}")

    confidence_intervals = estimate.get_confidence_intervals()
    if isinstance(confidence_intervals, np.ndarray):
        confidence_intervals = confidence_intervals.flatten()
        confidence_intervals = confidence_intervals.tolist()
    else:
        confidence_intervals = [float(_)
                                for _ in confidence_intervals]

    writer(f"Confidence interval: {confidence_intervals}\n")


def get_refutation_method(refuter_name, is_last_position: bool, refutation) -> Tuple[str, str]:
    if is_last_position:
        end="" 
    else:
        end="\n"
    if refuter_name != "dummy_outcome_refuter":
        return str(refutation), end
    return str(refutation[0]), end

def refute_effect(model, identified_estimand, estimate, refutation_methods: List[str], writer):
    """Applies refutation methods to the estimated causal effect."""
    for i, refuter_name in enumerate(refutation_methods):
        start_time_refute = time.time()
        try:
            refutation = model.refute_estimate(
                identified_estimand,
                estimate,
                method_name=refuter_name,
                placebo_type="permute"
            )
            end_time_refute = time.time()
            time_taken = end_time_refute - start_time_refute
            writer(f"Time taken: {time_taken:.6f} seconds")
            
            refutation_method_str, end_of_line = get_refutation_method(
                refuter_name, 
                i == len(refutation_methods)-1,
                refutation
            )
            writer(refutation_method_str, end=end_of_line)

        except Exception as e:
            writer(
                f"Failed to refute using {refuter_name}. Error:{str(e)}"
            )
            writer()


def dowhy_solver(
    test_name: str,
    csv_path: str,
    edges: List[Tuple[str, str]],
    treatment: str,
    outcome: str,
    fast: bool = False
) -> Dict[str, float]:
    """Solves a causal inference problem using DoWhy.

    Args:
        test_name (str): Name of the test case.
        csv_path (str): Path to the CSV file with the data.
        edges_str (str): String with the edges of the graph.
        treatment (str): Name of the treatment variable.
        outcome (str): Name of the outcome variable.
        fast (bool, optional): Whether to run in fast mode. Defaults to False.

    Returns:
        Dict: A dictionary with the method used as key and the ATE as value.
    """
    print("DoWhy solver running...")
    
    # Configure output
    output_file = (
        f"{DirectoryPaths.OUTPUTS.value}/{test_name}/{Solvers.DOWHY.value}_{test_name}.txt"
    )
    writer = OutputWriterDoWhy(output_file)

    # Load data and graph
    data, graph = load_data_and_graph(csv_path, edges)

    # Initialize causal model
    model = CausalModel(
        data=data,
        treatment=treatment,
        outcome=outcome,
        graph=graph
    )

    # Identify causal effect
    identified_estimand = model.identify_effect()
    estimands = get_estimands(identified_estimand)  
    writer(f"Estimands found: {', '.join(estimands)}")

    # Perform estimations and refutations
    methods_estimate = perform_estimations_and_refutations(
        model, identified_estimand, estimands, writer, fast
    )

    print("DoWhy solver Done.")
    return methods_estimate


def run_dowhy_solver(data, fast_mode):
    """Runs the DoWhy solver."""
    return dowhy_solver(
        test_name=data['test_name'],
        csv_path=data['csv_path'],
        edges=data['edges']['edges_list'],
        treatment=data['treatment'],
        outcome=data['outcome'],
        fast=fast_mode
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
        method_and_ate = run_dowhy_solver(data, json_input['fast'])
        time_taken = time.time() - start_time

        solver_result = SolverResultsFactory().get_solver_results_object(Solvers.DOWHY.value, data['test_name'])
        solver_result.log_solver_results(ATE(method_and_ate), time_taken)

        return jsonify({
            "status": "success",
            "time_taken": time_taken
        }), 200
    except Exception as e:
        log_solver_error(e, "dowhy", data['test_name'])
        return jsonify({"error": str(e), "error_code": "SOLVER_FAILED"}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
