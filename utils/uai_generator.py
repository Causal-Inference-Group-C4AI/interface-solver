import itertools
from itertools import product

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
    unobservable = unobservables_str.split(", ")
    nodes = observables + unobservable
    mapping = {node: i for i, node in enumerate(nodes)}

    # Define nodes cardinality
    obs_card = []
    for node in observables:
        obs_card.append(len(df[node].unique()))
    canonicalPartitions_data = {
        "num_nodes": len(observables) + len(unobservable),
        "num_edges": len(edges_str.split(", ")),
        "nodes": [],
        "edges": edges_str.split(", ")
    }
    for i, node in enumerate(observables):
        canonicalPartitions_data["nodes"].append(f"{node} {obs_card[i]}")
    for node in unobservable:
        canonicalPartitions_data["nodes"].append(f"{node} 0")
    _, _, unobCard = completeRelaxed(predefined_data=canonicalPartitions_data)
    cardinalities = obs_card + [int(unobCard)]*len(unobservable)

    # Define edges
    edges = [tuple(_.split(" -> ")) for _ in canonicalPartitions_data["edges"]]
    node_parents = {node: [] for node in nodes}
    node_children = {node: [] for node in nodes}
    for parent, child in edges:
        node_parents[child].append(parent)
        node_children[parent].append(child)
    edges_per_node = np.arange(len(nodes)).tolist()
    for node, parents in node_parents.items():
        edges_per_node[mapping[node]] = [mapping[parent] for parent in parents]

    # Define mechanisms
    mechanisms = {}
    r = {}
    r_index = {}
    for i, node in enumerate(nodes):
        if node in unobservable:
            mechanisms[node] = [1/cardinalities[i]]*cardinalities[i]
        elif not edges_per_node[i]:
            values_count = df.value_counts(node).to_list()
            n = df[node].count()
            mechanisms[node] = list(map(lambda x: x/n, values_count))
        else:
            multiplier = 1
            for parent in node_parents[node]:
                if parent in observables:
                    multiplier *= cardinalities[mapping[parent]]
            r[node] = list(
                product(*[list(np.arange(cardinalities[i]))]*multiplier))

    for node in unobservable:
        combinations = list(product(*[list(np.arange(len(r[child])))
                                      for child in node_children[node]]))
        r_index[node] = [{child: combination[i] for i, child in enumerate(
            node_children[node])} for combination in combinations]

    for node in observables:
        if not edges_per_node[mapping[node]]:
            continue
        mechanism = []
        for parent in node_parents[node]:
            if parent in unobservable:
                for indexes in r_index[parent]:
                    mechanism += [*r[node][indexes[node]]]
        mechanisms[node] = mechanism


if __name__ == "__main__":
    uai_generator(
        "balke_pearl",
        "Z -> X, X -> Y, U -> X, U -> Y",
        "X",
        "Y",
        "U",
        "data/csv/balke_pearl.csv"
    )
