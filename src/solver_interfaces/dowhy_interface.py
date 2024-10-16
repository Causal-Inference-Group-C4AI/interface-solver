import warnings

import networkx as nx
import pandas as pd
from dowhy import CausalModel

warnings.filterwarnings('ignore', category=UserWarning)


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
    for estimand, value in identified_estimand.estimands.items():
        print(f"{estimand}: {value != None}")

    # # Step 3: Estimate
    # estimate = model.estimate_effect(
    #     identified_estimand,
    #     method_name="backdoor.linear_regression"
    # )

    # # Step 4: Refute
    # refutation = model.refute_estimate(
    #     identified_estimand,
    #     estimate,
    #     method_name="random_common_cause"
    # )


if __name__ == "__main__":
    dowhy_solver(
        csv_path='data/csv/balke_pearl.csv',
        edges_str="Z -> X, X -> Y, U -> X, U -> Y",
        unobservables='Z'
    )
