import numpy as np
import pandas as pd
from canonicalPartitions import completeRelaxed


def uai_generator(
    test_name,
    edges_str,
    treatment,
    outcome,
    unobservables_str,
    csv_file
) -> None:
    # Create UAI file
    uai_filename = f"data/uai/{test_name}.uai"

    df = pd.read_csv(csv_file)  # Read CSV file

    # Define nodes
    observables = df.columns.tolist()
    unobsorvables = unobservables_str.split(", ")
    nodes = observables + unobsorvables
    mapping = {node: i for i, node in enumerate(nodes)}

    # Define nodes cardinality
    obs_card = []
    for node in observables:
        obs_card.append(len(df[node].unique()))
    canonicalPartitions_data = {
        "num_nodes": len(observables) + len(unobsorvables),
        "num_edges": len(edges_str.split(", ")),
        "nodes": [],
        "edges": edges_str.split(", ")
    }
    for i, node in enumerate(observables):
        canonicalPartitions_data["nodes"].append(f"{node} {obs_card[i]}")
    for node in unobsorvables:
        canonicalPartitions_data["nodes"].append(f"{node} 0")
    _, _, unobCard = completeRelaxed(predefined_data=canonicalPartitions_data)
    cardinalities = obs_card + [int(unobCard)]*len(unobsorvables)

    # Define edgesDon
    edges = [tuple(_.split(" -> ")) for _ in canonicalPartitions_data["edges"]]
    node_parents = {node: [] for node in nodes}
    for parent, child in edges:
        node_parents[child].append(parent)
    edges_per_node = np.arange(len(nodes)).tolist()
    for node, parents in node_parents.items():
        edges_per_node[mapping[node]] = [mapping[parent] for parent in parents]


if __name__ == "__main__":
    uai_generator(
        "balke_pearl",
        "Z -> X, X -> Y, U -> X, U -> Y",
        "X",
        "Y",
        "U",
        "data/csv/balke_pearl.csv"
    )
