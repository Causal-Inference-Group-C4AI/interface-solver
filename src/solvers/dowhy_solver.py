from typing import List, Tuple, Dict
import time
import argparse
import logging
import os
import sys
from typing import List, Tuple, Dict
import warnings

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import networkx as nx
import numpy as np
import pandas as pd
from dowhy import CausalModel

from utils.get_common_data import get_common_data
from utils.output_writer import OutputWriter, OutputWriterDoWhy
from utils.validator import Validator
from utils._enums import DirectoryPaths


# TODO: VERIFICAR TIPOS
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


def perform_estimations_and_refutations(
    model: CausalModel,
    identified_estimand,
    estimands: List[str],
    writer
) -> Dict:
    """Performs causal effect estimations and refutations."""
    estimation_methods = {
        "backdoor": [
            "linear_regression",
            "propensity_score_matching",
            "propensity_score_stratification",
            "propensity_score_weighting"
        ],
        "iv": ["instrumental_variable"],
        "frontdoor": []
    }

    refutation_methods = [
        "placebo_treatment_refuter",
        "data_subset_refuter",
        "random_common_cause",
        "dummy_outcome_refuter"
    ]

    methods_estimate = {}
    for estimand in estimands:
        for method in estimation_methods.get(estimand, []):
            method_name = f"{estimand}.{method}"
            writer("-" * 80)
            try:
                estimate = estimate_effect(model, identified_estimand, method_name, writer)
                methods_estimate[method_name] = estimate.value
                refute_effect(model, identified_estimand, estimate, refutation_methods, writer)
            except Exception as e:
                writer(f"Failed to estimate using {method_name}: {str(e)}")
    return methods_estimate


def estimate_effect(model, identified_estimand, method_name: str, writer) -> object:
    """Estimates the causal effect using a specified method."""
    estimate = model.estimate_effect(
        identified_estimand,
        method_name=method_name,
        test_significance=True,
        confidence_intervals=True
    )
    writer(f"Estimation using {method_name}:")
    writer(f"ATE = {estimate.value}")

    # Log p-value and confidence interval
    log_estimation_results(estimate, writer)
    return estimate


def log_estimation_results(estimate, writer):
    """Logs estimation results including p-value and confidence intervals."""
    p_value = estimate.test_stat_significance().get("p_value")
    confidence_intervals = estimate.get_confidence_intervals()

    # Format confidence intervals as a list
    if isinstance(confidence_intervals, np.ndarray):
        confidence_intervals = confidence_intervals.flatten().tolist()

    writer(f"P-value: {p_value}")
    writer(f"Confidence interval: {confidence_intervals}\n")


def refute_effect(model, identified_estimand, estimate, refutation_methods: List[str], writer):
    """Applies refutation methods to the estimated causal effect."""
    for refuter in refutation_methods:
        try:
            refutation = model.refute_estimate(
                identified_estimand,
                estimate,
                method_name=refuter,
                placebo_type="permute"
            )
            writer(str(refutation))
        except KeyError as e:
            writer(f"Failed to refute using {refuter}. Error: {str(e)}")


def dowhy_solver(
    test_name: str,
    csv_path: str,
    edges: List[Tuple[str, str]],
    treatment: str,
    outcome: str
) -> Dict:
    """
    Solves a causal inference problem using DoWhy.

    Args:
        test_name (str): Name of the test case.
        csv_path (str): Path to the CSV file with the data.
        edges (List[Tuple[str, str]]): List of edges defining the causal graph.
        treatment (str): Name of the treatment variable.
        outcome (str): Name of the outcome variable.
    Returns:
        Dict: A dictionary with the estimation methods and their results.
    """
    print("DoWhy solver running...")
    
    # Configure output
    output_file = f"{DirectoryPaths.OUTPUTS.value}/{test_name}/dowhy_{test_name}.txt"
    writer = OutputWriterDoWhy(output_file)

    # Load data and graph
    data, graph = load_data_and_graph(csv_path, edges)

    # Initialize causal model
    model = CausalModel(data=data, treatment=treatment, outcome=outcome, graph=graph)

    # Identify causal effect
    identified_estimand = model.identify_effect()
    estimands = get_estimands()
    writer(f"Estimands found: {', '.join(estimands)}")

    # Perform estimations and refutations
    methods_estimate = perform_estimations_and_refutations(
        model, identified_estimand, estimands, writer
    )

    print("DoWhy solver Done.")
    return methods_estimate


def configure_environment():
    """Configures the runtime environment."""
    warnings.filterwarnings("ignore", category=UserWarning)
    logging.getLogger().setLevel(logging.CRITICAL)


def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--common_data", required=True, help="Path to common data")
    return parser.parse_args()


def run_dowhy_solver(data):
    """Runs the DoWhy solver."""
    return dowhy_solver(
        test_name=data['test_name'],
        csv_path=data['csv_path'],
        edges=data['edges']['edges_list'],
        treatment=data['treatment'],
        outcome=data['outcome']
    )


def log_solver_results(test_name, method_and_ate, time_taken):
    """Logs the results of the solver."""
    print(f"Time taken by DoWhy: {time_taken:.6f} seconds")

    overview_file_path = f"{DirectoryPaths.OUTPUTS.value}/{test_name}/overview.txt"
    writer = OutputWriter(overview_file_path, reset=False)

    writer("DoWhy")
    writer(f"   Time taken by DoWhy: {time_taken:.6f} seconds")
    for method, ate in method_and_ate.items():
        writer(f"   Estimate method: {method}")
        writer(f"   ATE is: {ate}")
    writer(f"--------------------------------------------")


def main():
    """Main function to execute the DoWhy solver."""
    configure_environment()

    args = parse_arguments()
    validator = Validator()
    data = get_common_data(validator.get_valid_path(args.common_data))

    start_time = time.time()
    method_and_ate = run_dowhy_solver(data)
    time_taken = time.time() - start_time

    log_solver_results(data['test_name'], method_and_ate, time_taken)


if __name__ == "__main__":
    main()
