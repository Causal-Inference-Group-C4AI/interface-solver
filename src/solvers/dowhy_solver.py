from typing import List, Tuple

import networkx as nx
import numpy as np
import pandas as pd
from dowhy import CausalModel
from utils.validator import Validator
from utils.output_writer import OutputWriterDoWhy


def dowhy_solver(
    test_name: str,
    csv_path: str,
    edges: List[Tuple[str, str]],
    treatment: str,
    outcome: str
) -> None:
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
    output_file = f"outputs/{test_name}/dowhy_{test_name}.txt"
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

            except KeyError as e:
                writer(f"Failed to refute using {refuter}. Error:{str(e)}")
            except Exception as e:
                writer(f"Failed to estimate using {method_name}: {str(e)}")
    print("DoWhy solver Done.")

if __name__ == "__main__":
    validator = Validator()
    dowhy_solver(
        test_name='balke_pearl',
        csv_path='data/csv/balke_pearl.csv',
        edges=validator.get_valid_edge_tuple_list("Z -> X, X -> Y"),
        treatment='X',
        outcome='Y'
    )