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


def dowhy_solver(
    test_name: str,
    csv_path: str,
    edges: List[Tuple[str, str]],
    treatment: str,
    outcome: str
) -> Dict:
    """Solves a causal inference problem using DoWhy.

    Args:
        test_name (str): Name of the test case.
        csv_path (str): Path to the CSV file with the data.
        edges_str (str): String with the edges of the graph.
        treatment (str): Name of the treatment variable.
        outcome (str): Name of the outcome variable.
    """
    print("DoWhy solver running...")
    
    # Configure output
    output_file = f"{DirectoryPaths.OUTPUTS.value}/{test_name}/dowhy_{test_name}.txt"
    writer = OutputWriterDoWhy(output_file)

    # Data and graph
    data = pd.read_csv(csv_path)
    graph = nx.DiGraph(edges)

    # Step 1: Model
    model = CausalModel(
        data=data,
        treatment=treatment,
        outcome=outcome,
        graph=graph
    )

    # Step 2: Identify
    identified_estimand = model.identify_effect()
    estimands = []
    for estimand, value in identified_estimand.estimands.items():
        if estimand in ["backdoor", "iv", "frontdoor"] and value is not None:
            estimands.append(estimand)
    writer("Estimands found: "+", ".join(estimands))

    # Step 3 + 4: Estimate and Refute (for each estimand)
    estimation_methods = {
        "backdoor": [
            "linear_regression",
            "propensity_score_matching",
            "propensity_score_stratification",
            "propensity_score_weighting"
        ],
        "iv": [
            "instrumental_variable"
        ],
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
        for method in estimation_methods[estimand]:
            method_name = f"{estimand}.{method}"
            writer("-" * 80)
            try:
                estimate = model.estimate_effect(
                    identified_estimand,
                    method_name=method_name,
                    test_significance=True,
                    confidence_intervals=True
                )
                writer(f"Estimation using {method_name}:")
                writer(f"ATE = {estimate.value}")
                methods_estimate[str(method_name)] = float(estimate.value)

                # output the p-value
                p_value = estimate.test_stat_significance()["p_value"]
                writer(f"P-value: {p_value}")

                # output the confidence interval
                confidence_intervals = estimate.get_confidence_intervals()
                if isinstance(confidence_intervals, np.ndarray):
                    confidence_intervals = confidence_intervals.flatten()
                    confidence_intervals = confidence_intervals.tolist()
                else:
                    confidence_intervals = [float(_)
                                            for _ in confidence_intervals]

                writer(f"Confidence interval: {confidence_intervals}\n")

                # Step 4: Refute
                for refuter in refutation_methods:
                    ref = model.refute_estimate(
                        identified_estimand,
                        estimate,
                        method_name=refuter,
                        placebo_type="permute"
                    )
                    if refuter != refutation_methods[-1]:
                        writer(str(ref))
                    else:
                        writer(str(ref[0]), end="")

            # except KeyError as e:
            #     writer(f"Failed to refute using {refuter}. Error:{str(e)}")
            except Exception as e:
                writer(f"Failed to estimate using {method_name}: {str(e)}")
    print("DoWhy solver Done.")
    return methods_estimate


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning)
    logging.getLogger().setLevel(logging.CRITICAL)
    parser = argparse.ArgumentParser()
    parser.add_argument("--common_data", required=True, help="Path to common data")
    args = parser.parse_args()
    validator = Validator()
    data = get_common_data(validator.get_valid_path(args.common_data))

    start_time = time.time()
    method_and_ate = dowhy_solver(
        test_name=data['test_name'],
        csv_path=data['csv_path'],
        edges=data['edges']['edges_list'],
        treatment=data['treatment'],
        outcome=data['outcome']
    )
    end_time = time.time()

    time_taken = end_time - start_time
    print(f"Time taken by DoWhy: {time_taken:.6f} seconds")

    overview_file_path = f"{DirectoryPaths.OUTPUTS.value}/{data['test_name']}/overview.txt"
    writer = OutputWriter(overview_file_path, reset=False)

    writer("DoWhy")
    writer(f"   Time taken by DoWhy: {time_taken:.6f} seconds")
    for key, value in method_and_ate.items():
        writer(f"   Estimate method: {key}")
        writer(f"   ATE is: {value}")
    writer(f"--------------------------------------------")