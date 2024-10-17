import warnings

import networkx as nx
import numpy as np
import pandas as pd
from dowhy import CausalModel

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


def dowhy_solver(csv_path: str, edges_str: str):
    """Solves a causal inference problem using DoWhy.

    Args:
        csv_path (str): Path to the CSV file with the data.
        edges_str (str): String with the edges of the graph.
    """
    # Data and graph
    data = pd.read_csv(csv_path)
    edges = [tuple(edge.split(' -> ')) for edge in edges_str.split(', ')]
    graph = nx.DiGraph(edges)

    # Step 1: Model
    model = CausalModel(
        data=data,
        treatment="X",
        outcome="Y",
        graph=graph
    )

    # Step 2: Identify
    identified_estimand = model.identify_effect()
    estimands = {"backdoor": None, "iv": None, "frontdoor": None}
    print("Estimands found:", end=" ")
    for estimand, value in identified_estimand.estimands.items():
        if estimand in estimands:
            estimands[estimand] = value is not None
            print(f"{estimand} " if estimands[estimand] else "", end="")
    print()

    # Step 3: Estimate with all available methods
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

    for estimand in estimation_methods.keys():
        if estimands[estimand]:
            for method in estimation_methods[estimand]:
                method_name = f"{estimand}.{method}"
                try:
                    estimate = model.estimate_effect(
                        identified_estimand,
                        method_name=method_name,
                        test_significance=True,
                        confidence_intervals=True
                    )
                    print("-" * 80)
                    print(f"Estimation using {method_name}:")
                    print(f"ATE = {estimate.value}")

                    # Print the p-value
                    p_value = estimate.test_stat_significance()["p_value"]
                    print("P-value:", p_value)

                    # Print the confidence interval
                    confidence_intervals = estimate.get_confidence_intervals()
                    if isinstance(confidence_intervals, np.ndarray):
                        confidence_intervals = confidence_intervals.flatten()
                        confidence_intervals = confidence_intervals.tolist()
                    else:
                        confidence_intervals = [float(_)
                                                for _ in confidence_intervals]

                    print("Confidence interval:", confidence_intervals)
                    print("-" * 80)
                except Exception as e:
                    print(f"Failed to estimate using {method_name}: {str(e)}")

    # # Step 4: Refute
    # refutation = model.refute_estimate(
    #     identified_estimand,
    #     estimate,
    #     method_name="random_common_cause"
    # )


if __name__ == "__main__":
    dowhy_solver(
        csv_path='data/csv/balke_pearl.csv',
        edges_str="Z -> X, X -> Y",
    )
