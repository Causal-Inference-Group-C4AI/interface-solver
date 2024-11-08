from itertools import product

import numpy as np
import pandas as pd

from utils.canonical_partitions.canonicalPartitions import completeRelaxed


def get_edges(edges_str: str) -> list:
    return [tuple(_.split(" -> ")) for _ in edges_str.split(", ")]


def get_nodes(edges: list) -> tuple[list, dict, dict]:
    node_parents = {}
    node_children = {}
    nodes = []
    for parent, child in edges:
        if node_parents.get(child) is None:
            node_parents[child] = []
        node_parents[child].append(parent)
        if node_children.get(parent) is None:
            node_children[parent] = []
        node_children[parent].append(child)
        if parent not in nodes:
            nodes.append(parent)
        if child not in nodes:
            nodes.append(child)

    return nodes, node_parents, node_children


def uai_generator(
    test_name,
    edges_str,
    csv_file
) -> None:
    # Load data
    df = pd.read_csv(csv_file)
    df = df.drop(columns=["E"])
    df.to_csv(f"data/csv/{test_name}.csv", index=False)

    # Define edges
    edges = get_edges(edges_str)

    # Define nodes
    nodes, node_parents, node_children = get_nodes(edges)
    endogenous, exogenous = [], []
    for node in nodes:
        if node in node_parents:
            endogenous.append(node)
        else:
            exogenous.append(node)

    # Define endogenous nodes cardinality
    end_card = []
    for node in endogenous:
        end_card.append(len(df[node].unique()))

    # Define canonical partitions and relaxed graph
    canonicalPartitions_data = {
        "num_nodes": len(nodes),
        "num_edges": len(edges_str.split(", ")),
        "nodes": [],
        "edges": edges_str.split(", ")
    }
    for i, node in enumerate(endogenous):
        canonicalPartitions_data["nodes"].append(f"{node} {end_card[i]}")

    for node in exogenous:
        canonicalPartitions_data["nodes"].append(f"{node} 0")

    relaxed, ex, ex_card = completeRelaxed(
        predefined_data=canonicalPartitions_data
    )
    edges = get_edges(relaxed)
    nodes, node_parents, node_children = get_nodes(edges)
    exogenous = ex.split(", ")
    endogenous = [node for node in nodes if node not in exogenous]
    nodes = endogenous + exogenous  # Reorder nodes

    # Define cardinalities, mapping and edges per node
    ex_card = list(map(int, ex_card.split(", ")))
    cardinalities = end_card + ex_card
    mapping = {node: i for i, node in enumerate(nodes)}
    edges_per_node = np.arange(len(nodes)).tolist()
    for end, parents in node_parents.items():
        edges_per_node[mapping[end]] = [mapping[parent] for parent in parents]
        edges_per_node[mapping[end]].sort()

    for ex in exogenous:
        edges_per_node[mapping[ex]] = []

    # Define r functions
    r = {}
    for end in endogenous:
        multiplier = 1
        for parent in node_parents[end]:
            if parent in endogenous:
                multiplier *= cardinalities[mapping[parent]]

        r[end] = list(
            product(*[list(np.arange(cardinalities[i]))]*multiplier))

    # Define exogenous mechanisms and r functions indexing
    mechanisms = {}
    r_index = {}
    for i, ex in enumerate(exogenous):
        mechanisms[ex] = [1/ex_card[i]]*ex_card[i]
        combinations = list(product(*[list(np.arange(len(r[child])))
                                      for child in node_children[ex]]))
        r_index[ex] = [{child: combination[i] for i, child in enumerate(
            node_children[ex])} for combination in combinations]

    # Define endogenous mechanisms
    for end in endogenous:
        ex_parents = set(exogenous).intersection(node_parents[end])
        mechanism = []
        if ex_parents:
            for ex_parent in ex_parents:
                for indexes in r_index[ex_parent]:
                    mechanism += [*r[end][indexes[end]]]

            num_columns = len(r[end][0])
            reshaped_mechanism = np.array(
                mechanism).reshape(-1, num_columns).T
            mechanism = reshaped_mechanism.flatten().tolist()
        else:
            parents_values = [
                list(np.arange(cardinalities[mapping[parent]]))
                for parent in node_parents[end]
            ]
            parents_combinations = list(product(*parents_values))
            for combination in parents_combinations:
                rows = df[(df[node_parents[end]] == combination).all(1)]
                mechanism += list(rows[end].unique()
                                  if not rows.empty else [0])

        mechanisms[end] = mechanism
    print(mapping)
    # Write UAI file
    with open(f"data/uai/{test_name}.uai", "w") as uai:
        uai.write("CAUSAL\n")
        uai.write(f"{len(nodes)}\n")
        uai.write(" ".join(map(str, cardinalities)) + "\n")
        uai.write(f"{len(nodes)}\n")
        for i, edges in enumerate(edges_per_node):
            uai.write(
                f"{len(list(edges))+1}   {' '.join(map(str, edges+[i]))}\n")

        uai.write("\n")
        for node in nodes:
            mechanism = mechanisms[node]
            uai.write(f"{len(mechanism)}   {' '.join(map(str, mechanism))}\n")


# Example
if __name__ == "__main__":
    uai_generator(
        "balke_pearl_2",
        "Z -> X, X -> Y, U -> X, U -> Y, A -> Z",
        "data/csv/balke_pearl_2.csv"
    )
