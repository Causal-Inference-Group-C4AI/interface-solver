import json
import os
import sys
from itertools import product
from typing import Any, Dict, List, Tuple, Union

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

from utils._enums import DirectoryPaths
from utils.canonical_partitions.canonicalPartitions import completeRelaxed
from utils.validator import Validator


class Node():
    def __init__(self, value: Any):
        self._parents: List[Node] = []
        self._children: List[Node] = []
        self._value: str = str(value)

    def __str__(self):
        return self._value

    def __repr__(self):
        return f"Node({str(self)})"

    def get_value(self):
        return self._value

    def get_parents(self):
        return self._parents

    def get_children(self):
        return self._children

    def add_parent(self, parent: 'Node'):
        self._parents.append(parent)

    def add_child(self, child: 'Node'):
        self._children.append(child)


class Edge():
    def __init__(self, source: Node, destination: Node):
        self._source: Node = source
        self._destination: Node = destination
        self._edge: Tuple[Node, Node] = self._create_edge()

    def __str__(self):
        return f"{self._source} -> {self._destination}"

    def __repr__(self):
        return f"Edge({str(self)})"

    def _create_edge(self):
        self._source.add_child(self._destination)
        self._destination.add_parent(self._source)
        return (self._source, self._destination)

    def get_edge(self):
        return self._edge

    def get_nodes(self):
        return [self._source, self._destination]


class Graph():
    def __init__(self, edges_str: str):
        self._validator: Validator = Validator()

        self._edges_str: str = ""
        self._edges: List[Edge] = []
        self._nodes_str: List[str] = []
        self._nodes: Dict[str, Node] = {}
        self._nodes_parents: Dict[Node, List[Node]] = {}
        self._nodes_children: Dict[Node, List[Node]] = {}
        self._endogenous: List[Node] = []
        self._exogenous: List[Node] = []

        self._create_graph(edges_str)

    def __str__(self):
        return self._edges_str

    def __repr__(self):
        return f"Graph({str(self._edges)})"

    def _create_graph(self, edges_str: str):
        self._edges_str, edges = self._validator.get_valid_edges_in_string(
            edges_str)
        for source, destination in edges:
            source_node = self.get_node(source)
            destination_node = self.get_node(destination)
            self._edges.append(Edge(source_node, destination_node))

        self.get_parents()
        self.get_children()
        self.get_endogenous()
        self.get_exogenous()

    def get_edges(self):
        return self._edges

    def get_nodes(self):
        return list(self._nodes.values())

    def get_node(self, node_value: str):
        if node_value not in self._nodes:
            self._nodes[node_value] = Node(node_value)
        return self._nodes[node_value]

    def get_parents(self):
        if not self._nodes_parents:
            for node in list(self._nodes.values()):
                self._nodes_parents[node] = node.get_parents()

        return self._nodes_parents

    def get_children(self):
        if not self._nodes_children:
            for node in list(self._nodes.values()):
                self._nodes_children[node] = node.get_children()

        return self._nodes_children

    def get_endogenous(self):
        if not self._endogenous:
            for node, children in list(self.get_children().items()):
                if not children:
                    self._endogenous.append(node)
        return self._endogenous

    def get_exogenous(self):
        if not self._exogenous:
            for node, parents in list(self.get_parents().items()):
                if not parents:
                    self._exogenous.append(node)
        return self._exogenous


graph = Graph("E -> D, T -> D, T -> Y, D -> Y, U -> T, U -> Y")
print(graph._nodes_parents)


# TODO: Implement the following functions
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


# class UAIGenerator:
#     """
#     A class to generate UAI files for causal inference.

#     This class provides methods to parse edges, define nodes, and mechanisms,
#     and write UAI files based on the provided parameters.
#     """

#     def __init__(self, test_name: str, edges_str: str, csv_file: str) -> None:
#         """
#         Initializes the UaiGenerator with the given test name, edges string,
#         and CSV file path.

#         Args:
#             test_name (str): The name of the test.
#             edges_str (str): A string representing the edges of the graph,
#                 where each edge is in the format "parent -> child" and edges
#                 are separated by commas.
#             csv_file (str): The path to the CSV file containing the data.
#         """
#         self.test_name: str = test_name
#         self.edges_str: str = edges_str
#         self.csv_file: str = csv_file
#         self.uai_path: str = f"{DirectoryPaths.UAI.value}/{self.test_name}.uai"
#         self.mapping: Dict[str, int] = {}
#         self.generate()

#     def write_uai_file(
#         self,
#         nodes: List[str],
#         cardinalities: Dict[str, int],
#         edges_per_node: Dict[str, List[int]],
#         mechanisms: Dict[str, List[Union[int, float]]]
#     ) -> None:
#         """
#         Writes the UAI file with the specified parameters.

#         Args:
#             nodes (List[str]): List of all unique nodes in the graph.
#             cardinalities (Dict[str, int]): List of cardinalities for each
#                 node.
#             edges_per_node (Dict[str, List[int]]): Dict of edges for each node.
#             mechanisms (Dict[str, List[Union[int, float]]]): A dictionary where
#                 keys are nodes and values are their corresponding mechanisms.
#         """
#         with open(self.uai_path, "w") as uai:
#             uai.write("CAUSAL\n")
#             uai.write(f"{len(nodes)}\n")
#             uai.write(
#                 " ".join(
#                     map(str, [cardinalities[node] for node in nodes])
#                 ) + "\n"
#             )
#             uai.write(f"{len(nodes)}\n")
#             for node, node_i in self.mapping.items():
#                 node_edges = edges_per_node[node]
#                 uai.write(
#                     f"{len(node_edges)+1}   "
#                     f"{' '.join(map(str, node_edges+[node_i]))}\n"
#                 )

#             uai.write("\n")
#             for node in nodes:
#                 mechanism = mechanisms[node]
#                 mechanism_str = ' '.join(
#                     f'{val:.15f}'.rstrip('0').rstrip('.')
#                     if isinstance(val, float) else str(val)
#                     for val in mechanism
#                 )
#                 uai.write("{}   {}\n".format(len(mechanism), mechanism_str))

#     def get_mapping_str(self) -> str:
#         """
#         Returns the mapping of nodes to their corresponding variable names as a
#         JSON string.

#         This method creates a new mapping where each node is assigned a
#         variable name in the format "V{i}", where {i} is the index of the
#         node in the original mapping.

#         Returns:
#             str: A JSON string representing the new mapping of variable names
#             to nodes.
#         """
#         new_mapping = {f"V{i}": node for i, node in enumerate(self.mapping)}
#         return json.dumps(new_mapping)

#     def generate(self) -> None:
#         """
#         Generates a UAI file based on the provided parameters.
#         """
#         # Load data
#         df = pd.read_csv(self.csv_file)

#         # Define edges
#         edges = get_edges(self.edges_str)

#         # Define nodes
#         nodes, node_parents, node_children = get_nodes(edges)
#         endogenous, exogenous = define_nodes(nodes, node_parents)
#         # Create dummy variable for exogenous observed nodes
#         for ex in exogenous:
#             new_exogenous = exogenous.copy()
#             if ex in df.columns:
#                 new_exogenous.append(f"{ex}_dummy")
#                 endogenous.append(ex)
#                 new_exogenous.remove(ex)
#                 self.edges_str += f", {ex}_dummy -> {ex}"
#             exogenous = new_exogenous

#         # Define endogenous nodes cardinality
#         end_card = {end: len(df[end].unique()) for end in endogenous}

#         # Define canonical partitions and relaxed graph
#         canonicalPartitions_data = {
#             "num_nodes": len(endogenous) + len(exogenous),
#             "num_edges": len(self.edges_str.split(", ")),
#             "nodes": [f"{end} {end_card[end]}" for end in endogenous]
#             + [f"{ex} 0" for ex in exogenous],
#             "edges": self.edges_str.split(", ")
#         }

#         relaxed, ex, ex_card = completeRelaxed(
#             predefined_data=canonicalPartitions_data
#         )
#         edges = get_edges(relaxed)
#         nodes, node_parents, node_children = get_nodes(edges)
#         endogenous, exogenous = define_nodes(nodes, node_parents)
#         nodes = endogenous + exogenous  # Reorder nodes

#         # Define cardinalities, mapping and edges per node
#         ex_card = list(map(int, ex_card.split(", ")))
#         cardinalities = {**end_card, **
#                          {f"U{i}": card for i, card in enumerate(ex_card)}}
#         self.mapping = {node: i for i, node in enumerate(nodes)}
#         print(self.mapping)
#         edges_per_node = {
#             node:
#             sorted([self.mapping[parent]
#                     for parent in node_parents.get(node, [])])
#             for node in nodes
#         }

#         # Define mechanisms
#         mechanisms = define_mechanisms(
#             df, node_parents, node_children,
#             cardinalities, endogenous, exogenous
#         )

#         # Write UAI file
#         uai_path = self.write_uai_file(
#             nodes, cardinalities, edges_per_node, mechanisms)

#         return uai_path


# Example
if __name__ == "__main__":
    # uai = UAIGenerator(
    #     "itau_teste",
    #     "E -> D, T -> D, T -> Y, D -> Y, U -> T, U -> Y",
    #     "data/csv/unob_itau_teste.csv"
    # )
    pass
