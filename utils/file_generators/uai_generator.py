import json
from itertools import product
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd

from utils._enums import DirectoryPaths
from utils.canonical_partitions.canonicalPartitions import completeRelaxed


def get_edges(edges_str: str) -> List[Tuple[str, str]]:
    """
    Parses a string of edges and returns a list of tuples representing the
    edges.

    Args:
        edges_str (str): A string representing the edges of the graph,
            where each edge is in the format "parent -> child" and edges
            are separated by commas.

    Returns:
        List: A list of tuples where each Tuple represents an
        edge in the format (parent, child).
    """
    return [tuple(_.split(" -> ")) for _ in edges_str.split(", ")]


def get_nodes(
    edges: List[Tuple[str, str]]
) -> Tuple[List[str], Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Extracts nodes, their parents, and their children from a list of edges.

    Args:
        edges (List[Tuple[str, str]]): A list of tuples where each tuple
            represents an edge in the format (parent, child).

    Returns:
        Tuple:
            - nodes (List[str]): A list of all unique nodes in the graph.
            - node_parents (Dict[str, List[str]]): A dictionary where keys
            are nodes and values are lists of parent nodes.
            - node_children (Dict[str, List[str]]): A dictionary where keys
            are nodes and values are lists of child nodes.
    """
    node_parents = {}
    node_children = {}
    nodes = set()
    for parent, child in edges:
        node_parents.setdefault(child, []).append(parent)
        node_children.setdefault(parent, []).append(child)
        nodes.update([parent, child])

    return list(nodes), node_parents, node_children


def define_nodes(
    nodes: List[str],
    node_parents: Dict[str, List[str]]
) -> Tuple[List[str], List[str]]:
    """Define endogenous and exogenous nodes

    Args:
        nodes (List[str]): List of all unique nodes in the graph.
        node_parents (Dict[str, List[str]]): A dictionary where keys are nodes
            and values are lists of parent nodes.

    Returns:
        Tuple:
            - endogenous (List[str]): A list of endogenous nodes.
            - exogenous (List[str]): A list of exogenous nodes.
    """
    endogenous = [node for node in nodes if node in node_parents]
    exogenous = [node for node in nodes if node not in node_parents]
    return endogenous, exogenous


def define_mechanisms(
    df: pd.DataFrame,
    node_parents: Dict[str, List[str]],
    node_children: Dict[str, List[str]],
    cardinalities: Dict[str, int],
    endogenous: List[str],
    exogenous: List[str]
) -> Dict[str, List[Union[int, float]]]:
    """
    Defines the mechanisms for endogenous and exogenous nodes in the graph.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        node_parents (Dict[str, List[str]]): A dictionary where keys are nodes
            and values are lists of parent nodes.
        node_children (Dict[str, List[str]]): A dictionary where keys are nodes
            and values are lists of child nodes.
        cardinalities (Dict[str, int]): List of cardinalities for each node.
        endogenous (List[str]): List of endogenous nodes.
        exogenous (List[str]): List of exogenous nodes.

    Returns:
        Dict: A dictionary where keys are nodes and values are their
        corresponding mechanisms.
    """
    # Define r functions
    r = {}
    for end in endogenous:
        mult = 1
        for parent in node_parents[end]:
            if parent in endogenous:
                mult *= cardinalities[parent]

        r[end] = list(
            product(*[list(np.arange(cardinalities[end]))]*mult))

    # Define exogenous mechanisms and r functions indexing
    mechanisms: Dict[str, List[Union[int, float]]] = {}
    r_index = {}
    for ex in exogenous:
        mechanisms[ex] = [1/cardinalities[ex]]*cardinalities[ex]
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
                list(np.arange(cardinalities[parent]))
                for parent in node_parents[end]
            ]
            parents_combinations = list(product(*parents_values))
            for combination in parents_combinations:
                rows = df[(df[node_parents[end]] == combination).all(1)]
                mechanism += [rows[end].value_counts().idxmax()
                              ] if not rows.empty else [0]

        mechanisms[end] = mechanism

    return mechanisms


class UAIGenerator:
    """
    A class to generate UAI files for causal inference.

    This class provides methods to parse edges, define nodes, and mechanisms,
    and write UAI files based on the provided parameters.
    """

    def __init__(self, test_name: str, edges_str: str, csv_file: str) -> None:
        """
        Initializes the UaiGenerator with the given test name, edges string,
        and CSV file path.

        Args:
            test_name (str): The name of the test.
            edges_str (str): A string representing the edges of the graph,
                where each edge is in the format "parent -> child" and edges
                are separated by commas.
            csv_file (str): The path to the CSV file containing the data.
        """
        self.test_name: str = test_name
        self.edges_str: str = edges_str
        self.csv_file: str = csv_file
        self.uai_path: str = f"{DirectoryPaths.UAI.value}/{self.test_name}.uai"
        self.mapping: Dict[str, int] = {}
        self.generate()

    def write_uai_file(
        self,
        nodes: List[str],
        cardinalities: Dict[str, int],
        edges_per_node: Dict[str, List[int]],
        mechanisms: Dict[str, List[Union[int, float]]]
    ) -> None:
        """
        Writes the UAI file with the specified parameters.

        Args:
            nodes (List[str]): List of all unique nodes in the graph.
            cardinalities (Dict[str, int]): List of cardinalities for each
                node.
            edges_per_node (Dict[str, List[int]]): Dict of edges for each node.
            mechanisms (Dict[str, List[Union[int, float]]]): A dictionary where
                keys are nodes and values are their corresponding mechanisms.
        """
        with open(self.uai_path, "w") as uai:
            uai.write("CAUSAL\n")
            uai.write(f"{len(nodes)}\n")
            uai.write(
                " ".join(
                    map(str, [cardinalities[node] for node in nodes])
                ) + "\n"
            )
            uai.write(f"{len(nodes)}\n")
            for node, node_i in self.mapping.items():
                node_edges = edges_per_node[node]
                uai.write(
                    f"{len(node_edges)+1}   "
                    f"{' '.join(map(str, node_edges+[node_i]))}\n"
                )

            uai.write("\n")
            for node in nodes:
                mechanism = mechanisms[node]
                uai.write(
                    f"{len(mechanism)}   {' '.join(map(str, mechanism))}\n")

    def get_mapping_str(self) -> str:
        """
        Returns the mapping of nodes to their corresponding variable names as a
        JSON string.

        This method creates a new mapping where each node is assigned a
        variable name in the format "V{i}", where {i} is the index of the
        node in the original mapping.

        Returns:
            str: A JSON string representing the new mapping of variable names
            to nodes.
        """
        new_mapping = {f"V{i}": node for i, node in enumerate(self.mapping)}
        return json.dumps(new_mapping)

    def generate(self) -> None:
        """
        Generates a UAI file based on the provided parameters.
        """
        # Load data
        df = pd.read_csv(self.csv_file)

        # Define edges
        edges = get_edges(self.edges_str)

        # Define nodes
        nodes, node_parents, node_children = get_nodes(edges)
        endogenous, exogenous = define_nodes(nodes, node_parents)
        # Create dummy variable for exogenous observed nodes
        for ex in exogenous:
            new_exogenous = exogenous.copy()
            if ex in df.columns:
                new_exogenous.append(f"{ex}_dummy")
                endogenous.append(ex)
                new_exogenous.remove(ex)
                self.edges_str += f", {ex}_dummy -> {ex}"
            exogenous = new_exogenous

        # Define endogenous nodes cardinality
        end_card = {end: len(df[end].unique()) for end in endogenous}

        # Define canonical partitions and relaxed graph
        canonicalPartitions_data = {
            "num_nodes": len(endogenous) + len(exogenous),
            "num_edges": len(self.edges_str.split(", ")),
            "nodes": [f"{end} {end_card[end]}" for end in endogenous]
            + [f"{ex} 0" for ex in exogenous],
            "edges": self.edges_str.split(", ")
        }

        relaxed, ex, ex_card = completeRelaxed(
            predefined_data=canonicalPartitions_data
        )
        edges = get_edges(relaxed)
        nodes, node_parents, node_children = get_nodes(edges)
        endogenous, exogenous = define_nodes(nodes, node_parents)
        nodes = endogenous + exogenous  # Reorder nodes

        # Define cardinalities, mapping and edges per node
        ex_card = list(map(int, ex_card.split(", ")))
        cardinalities = {**end_card, **
                         {f"U{i}": card for i, card in enumerate(ex_card)}}
        self.mapping = {node: i for i, node in enumerate(nodes)}
        print(self.mapping)
        edges_per_node = {
            node:
            sorted([self.mapping[parent]
                    for parent in node_parents.get(node, [])])
            for node in nodes
        }

        # Define mechanisms
        mechanisms = define_mechanisms(
            df, node_parents, node_children,
            cardinalities, endogenous, exogenous
        )

        # Write UAI file
        uai_path = self.write_uai_file(
            nodes, cardinalities, edges_per_node, mechanisms)

        return uai_path


# Example
if __name__ == "__main__":
    uai = UAIGenerator(
        "itau_teste",
        "E -> D, T -> D, T -> Y, D -> Y, U -> T, U -> Y",
        "data/csv/unob_itau_teste.csv"
    )
