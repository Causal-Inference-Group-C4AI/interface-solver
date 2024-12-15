from functools import singledispatch, singledispatchmethod
import json
import os
import sys
from abc import ABC, abstractmethod
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
        self.cardinality: int = 0
        self.mechanism: Mechanism = None

    def __str__(self):
        return self._value

    def __repr__(self):
        return f"Node('{self._value}')"

    def get_value(self):
        return str(self._value)

    def get_parents(self):
        return self._parents

    def get_parents_values(self):
        return [parent.get_value() for parent in self.get_parents()]

    def get_children(self):
        return self._children

    def add_parent(self, parent: 'Node'):
        self._parents.append(parent)

    def add_child(self, child: 'Node'):
        self._children.append(child)

    def is_exogenous(self) -> bool:
        return not self._parents

    def is_endogenous(self) -> bool:
        return not self.is_exogenous()


class Edge():
    def __init__(self, source: Node, destination: Node):
        self._source: Node = source
        self._destination: Node = destination
        self._edge: Tuple[Node, Node] = self._create_edge()

    def __str__(self):
        return f"{self._source} -> {self._destination}"

    def __repr__(self):
        return f"Edge({self._source!r}, {self._destination!r})"

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
        self._nodes: Dict[str, Node] = {}
        self._nodes_parents: Dict[Node, List[Node]] = {}
        self._nodes_children: Dict[Node, List[Node]] = {}
        self._endogenous: List[Node] = []
        self._exogenous: List[Node] = []

        self._create_graph(edges_str)

    def __str__(self):
        return self._edges_str

    def __repr__(self):
        return f"Graph('{self._edges_str}')"

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

    def get_edges_as_str(self):
        return [str(edge) for edge in self.get_edges()]

    def get_nodes(self):
        return list(self._nodes.values())

    def get_node(self, node_value: str):
        if node_value not in self._nodes:
            self._nodes[node_value] = Node(node_value)
        return self._nodes[node_value]

    def get_parents(self):
        if not self._nodes_parents:
            for node in self.get_nodes():
                self._nodes_parents[node] = node.get_parents()

        return self._nodes_parents

    def get_children(self):
        if not self._nodes_children:
            for node in self.get_nodes():
                self._nodes_children[node] = node.get_children()

        return self._nodes_children

    def get_endogenous(self):
        if not self._endogenous:
            for node in self.get_nodes():
                if node.is_endogenous():
                    self._endogenous.append(node)
        return self._endogenous

    def get_exogenous(self):
        if not self._exogenous:
            for node in self.get_nodes():
                if node.is_exogenous():
                    self._exogenous.append(node)
        return self._exogenous


class Mechanism(ABC):
    def __init__(self, mechanism: List[Union[int, float]] = None):
        if mechanism:
            self._mechanism = mechanism
        else:
            self._mechanism: List[Union[int, float]] = None

    def __str__(self):
        return str(self._mechanism)

    @abstractmethod
    def __repr__(self):
        pass

    def set_mechanism(self, mechanism: List[Union[int, float]]):
        self._mechanism = mechanism

    def get_mechanism(self):
        return self._mechanism


class EndogenousMechanism(Mechanism):
    def __init__(self):
        super().__init__()
        self.r_function: List[Tuple[int, ...]] = None

    def __repr__(self):
        return f"EndogenousMechanism({self._mechanism!r})"


class ExogenousMechanism(Mechanism):
    def __init__(self):
        super().__init__()
        self.r_index: List[Dict[Node, int]] = None

    def __repr__(self):
        return f"ExogenousMechanism({self._mechanism!r})"


class MechanismsDefiner():
    def __init__(self, graph: Graph, df: pd.DataFrame):
        self._graph: Graph = graph
        self._df: pd.DataFrame = df

    def _define_r_functions(self, node: Node):
        if not node.is_endogenous():
            raise ValueError("Node must be endogenous to use this method.")
        mult = 1
        for parent in node.get_parents():
            if parent.is_endogenous():
                mult *= parent.cardinality

        node.mechanism.r_function = list(
            product(*[np.arange(node.cardinality).tolist()]*mult))

    def _define_r_index(self, node: Node):
        combinations: List[Tuple[int, ...]] = list(
            product(*[
                np.arange(len(child.mechanism.r_function)).tolist()
                for child in node.get_children()
            ])
        )
        node.mechanism.r_index = [
            {child: combination[i] for i, child in enumerate(
                node.get_children())}
            for combination in combinations
        ]

    def _define_exogenous_mechanisms(self, node: Node):
        if not node.is_exogenous():
            raise ValueError("Node must be exogenous to use this method.")
        node.mechanism.set_mechanism([1/node.cardinality]*node.cardinality)
        self._define_r_index(node)

    def _define_mechanism_for_exogenous_parents(
        self, node: Node, ex_parents: set[Node]
    ):
        mechanism: List[int] = []
        for ex_parent in ex_parents:
            for indexes in ex_parent.mechanism.r_index:
                mechanism += [*node.mechanism.r_function[indexes[node]]]

            num_columns = len(node.mechanism.r_function[0])
            reshaped_mechanism = np.array(
                mechanism).reshape(-1, num_columns).T
            mechanism = reshaped_mechanism.flatten().tolist()

        node.mechanism.set_mechanism(mechanism)

    def _define_mechanism_for_endogenous_parents(self, node: Node):
        mechanism: List[int] = []
        parents_values: List[List[int]] = [
            np.arange(parent.cardinality).tolist()
            for parent in node.get_parents()
        ]
        parents_combinations = list(product(*parents_values))
        for combination in parents_combinations:
            parents_str = [
                parent.get_value() for parent in node.get_parents()
            ]
            rows = df[(df[parents_str] == combination).all(1)]
            # FIXME: Implements creation of latent variable for non
            # deterministic functions
            mechanism += [int(rows[node.get_value()].value_counts().idxmax())
                          ] if not rows.empty else [0]

        node.mechanism.set_mechanism(mechanism)

    def _define_endogenous_mechanisms(self, node: Node):
        if not node.is_endogenous():
            raise ValueError("Node must be endogenous to use this method.")
        ex_parents = set(self._graph.get_exogenous()).intersection(
            node.get_parents())
        if ex_parents:
            self._define_mechanism_for_exogenous_parents(node, ex_parents)
        else:
            self._define_mechanism_for_endogenous_parents(node)

    def define_mechanisms(self):
        # 1st: Define r functions for endogenous nodes
        for endogenous_node in self._graph.get_endogenous():
            endogenous_node.mechanism = EndogenousMechanism()
            self._define_r_functions(endogenous_node)

        # 2nd: Define mechanisms and r functions indexing for exogenous nodes
        for exogenous_node in self._graph.get_exogenous():
            exogenous_node.mechanism = ExogenousMechanism()
            self._define_exogenous_mechanisms(exogenous_node)

        # 3rd: Define mechanisms for endogenous nodes
        for endogenous_node in self._graph.get_endogenous():
            self._define_endogenous_mechanisms(endogenous_node)


class RelaxedGraphGenerator():
    _graph: Graph = None
    _df: pd.DataFrame = None

    @classmethod
    def _define_observable_cardinality(cls, node: Node):
        node.cardinality = len(cls._df[node.get_value()].unique())

    @classmethod
    def _define_latents_cardinalities(cls, lat: str, lat_card: str):
        latents = lat.split(", ")
        latents_card = [int(card) for card in lat_card.split(", ")]
        for card, latent in zip(latents_card, latents):
            cls._graph.get_node(latent).cardinality = card

    @classmethod
    def generate(cls, graph: Graph, df: pd.DataFrame):
        cls._graph = graph
        cls._df = df
        nodes_str: List[str] = []
        obs_nodes: List[str] = []
        for node in cls._graph.get_nodes():
            if node.get_value() in cls._df.columns:
                cls._define_observable_cardinality(node)
                nodes_str.append(f"{node} {node.cardinality}")
                obs_nodes.append(node.get_value())
            else:
                nodes_str.append(f"{node} 0")

        relaxed, lat, lat_card = CanonicalPartitionsAdapter.get_relaxed_graph(
            nodes_str, cls._graph.get_edges_as_str()
        )
        cls._graph = ValidUAIGraph(relaxed, cls._df, cls._graph, obs_nodes)
        cls._define_latents_cardinalities(lat, lat_card)

        return cls._graph


class ValidUAIGraph(Graph):
    def __init__(self, edges_str: str, df: pd.DataFrame, graph: Graph = None,
                 fixed_nodes: List[str] = None):
        if not graph:
            super().__init__(edges_str)
        else:
            self._validator: Validator = graph._validator
            self._edges_str: str = ""
            self._edges: List[Edge] = []
            self._nodes: Dict[str, Node] = {}
            self._nodes_parents: Dict[Node, List[Node]] = {}
            self._nodes_children: Dict[Node, List[Node]] = {}
            self._endogenous: List[Node] = []
            self._exogenous: List[Node] = []
            self.__old_graph: Graph = graph
            if fixed_nodes:
                self._fix_nodes(fixed_nodes)
            self._create_graph(edges_str)

        self._df = df
        self.check_validity()

    def _fix_nodes(self, fixed_nodes: List[str]):
        for node_str in fixed_nodes:
            self._nodes[node_str] = self.__old_graph.get_node(node_str)

    def _check_observable_exogenous_nodes(self):
        new_exogenous = set(self.get_exogenous())
        for ex in self._exogenous:
            ex_str = ex.get_value()
            if ex_str in self._df.columns:
                dummy_node = self.get_node(f"{ex_str}_dummy")
                dummy_node.cardinality = ex.cardinality
                new_exogenous.add(dummy_node)
                self._endogenous.append(ex)
                new_exogenous.remove(ex)
                self._edges_str += f", {ex_str}_dummy -> {ex_str}"

        self._exogenous = list(new_exogenous)

    def check_validity(self):
        self._check_observable_exogenous_nodes()


class CanonicalPartitionsAdapter():
    @staticmethod
    def get_relaxed_graph(nodes: List[str], edges: List[str]):
        canonicalPartitions_data = {
            "num_nodes": len(nodes),
            "num_edges": len(edges),
            "nodes": nodes,
            "edges": edges
        }

        relaxed, ex, ex_card = completeRelaxed(
            predefined_data=canonicalPartitions_data
        )

        return relaxed, ex, ex_card


df = pd.read_csv("data/inputs/csv/balke_pearl.csv")
graph = RelaxedGraphGenerator.generate(Graph("Z -> X, Z -> Y, X -> Y, U -> X, U -> Y"), df)
for node in graph.get_nodes():
    print(node, node.cardinality)


class UAIGenerator:
    def __init__(self, test_name: str, edges_str: str, csv_file: str) -> None:
        self._uai_path: str = ""
        self._mapping: Dict[str, int] = {}
        self.test_name: str = test_name
        self.edges_str: str = edges_str
        self.csv_file: str = csv_file
        self.graph: ValidUAIGraph = None
        self.df = pd.read_csv(csv_file)

        self.generate()

# TODO: Implement the following functions
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
                mechanism_str = ' '.join(
                    f'{val:.15f}'.rstrip('0').rstrip('.')
                    if isinstance(val, float) else str(val)
                    for val in mechanism
                )
                uai.write("{}   {}\n".format(len(mechanism), mechanism_str))

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
        # Define UAI path
        self._uai_path = f"{DirectoryPaths.UAI.value}/{self.test_name}.uai"

        # Load data
        df = pd.read_csv(self.csv_file)

        # Define graph
        self.graph = RelaxedGraphGenerator.generate(Graph(self.edges_str), df)

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
    # uai = UAIGenerator(
    #     "itau_teste",
    #     "E -> D, T -> D, T -> Y, D -> Y, U -> T, U -> Y",
    #     "data/csv/unob_itau
    pass