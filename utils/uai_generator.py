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
    # Load data
    df = pd.read_csv(csv_file)

    # Define nodes
    observables = df.columns.tolist()
    unobservables = unobservables_str.split(", ")
    nodes = observables + unobservables
    mapping = {node: i for i, node in enumerate(nodes)}

    # Define nodes cardinality
    obs_card = []
    for node in observables:
        obs_card.append(len(df[node].unique()))
    canonicalPartitions_data = {
        "num_nodes": len(observables) + len(unobservables),
        "num_edges": len(edges_str.split(", ")),
        "nodes": [],
        "edges": edges_str.split(", ")
    }
    for i, node in enumerate(observables):
        canonicalPartitions_data["nodes"].append(f"{node} {obs_card[i]}")
    for node in unobservables:
        canonicalPartitions_data["nodes"].append(f"{node} 0")
    _, _, unobCard = completeRelaxed(predefined_data=canonicalPartitions_data)
    cardinalities = obs_card + [int(unobCard)]*len(unobservables)

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
        if node in unobservables:
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

    for node in unobservables:
        combinations = list(product(*[list(np.arange(len(r[child])))
                                      for child in node_children[node]]))
        r_index[node] = [{child: combination[i] for i, child in enumerate(
            node_children[node])} for combination in combinations]

    for node in observables:
        if edges_per_node[mapping[node]]:
            unob_parents = set(unobservables).intersection(node_parents[node])
            mechanism = []
            if unob_parents:
                for unob_parent in unob_parents:
                    for indexes in r_index[unob_parent]:
                        mechanism += [*r[node][indexes[node]]]
            else:
                parents_values = [
                    list(np.arange(cardinalities[mapping[parent]]))
                    for parent in node_parents[node]
                ]
                parents_combinations = list(product(*parents_values))
                for combination in parents_combinations:
                    rows = df[(df[node_parents[node]] == combination).all(1)]
                    mechanism += list(rows[node].unique()
                                      if not rows.empty else [0])
            mechanisms[node] = mechanism

    # Write UAI file
    with open(f"data/uai/{test_name}.uai", "w") as uai:
        uai.write("CAUSAL\n")
        uai.write(f"{len(nodes)}\n")
        uai.write(" ".join(map(str, cardinalities)) + "\n")
        uai.write(f"{len(nodes)}\n")
        for i, edges in enumerate(edges_per_node):
            uai.write(f"{len(edges)+1}   {' '.join(map(str, edges+[i]))}\n")
        uai.write("\n")
        for node in nodes:
            mechanism = mechanisms[node]
            uai.write(f"{len(mechanism)}   {' '.join(map(str, mechanism))}\n")


# Example
if __name__ == "__main__":
    uai_generator(
        "balke_pearl_2",
        "Z -> X, X -> Y, U -> X, U -> Y, A -> Z",
        "X",
        "Y",
        "U",
        "data/csv/balke_pearl_2.csv"
    )
