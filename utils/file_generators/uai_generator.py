import json
import os
import sys
from abc import ABC, abstractmethod
from itertools import product
from typing import Any, Dict, List, Set, Tuple, Union
from collections import defaultdict

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../')))

from utils._enums import DirectoryPaths
from utils.canonical_partitions.canonicalPartitions import completeRelaxed
from utils.validator import Validator

class DataOptim:
    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path
        self.column_labels, self.node_cardinalities, self.combination_counts, self.unique_rows = self._process_large_dataset()

    def _process_large_dataset(self):
        header = pd.read_csv(self.csv_path, nrows=0)
        column_labels = header.columns.tolist()

        unique_counts = {col: defaultdict(int) for col in column_labels}
        combination_counts = defaultdict(int)
        agnostic_combination_counts = defaultdict(int)

        
        for chunk in pd.read_csv(self.csv_path, chunksize=100000, usecols=column_labels):
            for col in column_labels:
                for val in chunk[col].values:
                    unique_counts[col][val] += 1

            for _, row in chunk.iterrows():
                # Process for agnostic_combination_counts (tuple version)
                vals = tuple(row[col] for col in column_labels)
                agnostic_combination_counts[vals] += 1
                
                # Process for combination_counts (string key version)
                key = ",".join(f"{col}:{row[col]}" for col in column_labels)
                combination_counts[key] += 1
        
        unique_rows = pd.DataFrame([list(row) + [count] for row, count in agnostic_combination_counts.items()])
        unique_rows.columns = column_labels + ['frequency']
        return column_labels, {col: len(counts) for col, counts in unique_counts.items()}, combination_counts, unique_rows

    def test(self):
        parents_values: List[List[int]] = [
            np.arange(2).tolist()
            for _ in ["E", "T"]
        ]
        parents_combinations = list(product(*parents_values))

        _grouped_df = self.unique_rows.groupby(["E", "T"])
        print(_grouped_df.head())
        for combination in parents_combinations:
            rows = _grouped_df.get_group(combination)
            # print(f"-->{rows}")
            possible_functions = rows["D"].unique()
            print(f">>{len(possible_functions)}")

class Node():
    """Node class to represent a node in a graph.

    Attributes:
        cardinality (int): The cardinality of the node.
        mechanism (Mechanism): The mechanism of the node.
        number (int): The number of the node.
    """
    def __init__(self, value: Any) -> None:
        """Initializes the Node class.

        Args:
            value (Any): The value of the node.
        """
        self._parents: List[Node] = []
        self._children: List[Node] = []
        self._value: str = str(value)
        self.cardinality: int = int(0)
        self.mechanism: Mechanism = None
        self.number: int = None

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Node('{self._value}')"

    def get_value(self) -> str:
        """Returns the value of the node.

        Returns:
            str: The value of the node.
        """
        return str(self._value)

    def get_parents(self) -> List['Node']:
        """Returns the parents of the node.

        Returns:
            List[Node]: The parents of the node.
        """
        return self._parents

    def get_parents_values(self) -> List[str]:
        """Returns the values of the parents of the node.

        Returns:
            List[str]: The values of the parents of the node.
        """
        return [parent.get_value() for parent in self.get_parents()]

    def get_children(self) -> List['Node']:
        """Returns the children of the node.

        Returns:
            List[Node]: The children of the node.
        """
        return self._children

    def get_children_values(self) -> List[str]:
        """Returns the values of the children of the node.

        Returns:
            List[str]: The values of the children of the node.
        """
        return [child.get_value() for child in self.get_children()]

    def add_parent(self, parent: 'Node') -> None:
        """Adds a parent to the node.

        Args:
            parent (Node): The parent node to add.
        """
        self._parents.append(parent)

    def reset_parents(self) -> None:
        """Resets the parents of the node."""
        self._parents = []

    def add_child(self, child: 'Node') -> None:
        """Adds a child to the node.

        Args:
            child (Node): The child node to add.
        """
        self._children.append(child)

    def reset_children(self) -> None:
        """Resets the children of the node."""
        self._children = []

    def reset_node(self):
        """Resets the node, deleting its parents and children."""
        self.reset_parents()
        self.reset_children()

    def is_exogenous(self) -> bool:
        """Returns True if the node is exogenous, False otherwise.

        Returns:
            bool: True if the node is exogenous, False otherwise.
        """
        return not self._parents

    def is_endogenous(self) -> bool:
        """Returns True if the node is endogenous, False otherwise.

        Returns:
            bool: True if the node is endogenous, False otherwise.
        """
        return not self.is_exogenous()


class Edge():
    """Edge class to represent an edge in a graph."""
    def __init__(self, source: Node, destination: Node) -> None:
        """Initializes the Edge class.

        Args:
            source (Node): The source node of the edge.
            destination (Node): The destination node of the edge.
        """
        self._source: Node = source
        self._destination: Node = destination
        self._edge: Tuple[Node, Node] = self._create_edge()

    def __str__(self) -> str:
        return f"{self._source} -> {self._destination}"

    def __repr__(self) -> str:
        return f"Edge({self._source!r}, {self._destination!r})"

    def _create_edge(self) -> Tuple[Node, Node]:
        """Creates an edge between the source and destination nodes.

        Returns:
            Tuple[Node, Node]: The edge value.
        """
        self._source.add_child(self._destination)
        self._destination.add_parent(self._source)
        return (self._source, self._destination)

    def get_edge(self) -> Tuple[Node, Node]:
        """Returns the edge.

        Returns:
            Tuple[Node, Node]: The edge.
        """
        return self._edge

    def get_nodes(self) -> List[Node]:
        """Returns the nodes of the edge.

        Returns:
            List[Node]: The nodes of the edge.
        """
        return [self._source, self._destination]


class Graph():
    """Graph class to represent a graph."""
    def __init__(self, edges_str: str, data_optim: DataOptim) -> None:
        """Initializes the Graph class.

        Args:
            edges_str (str): The edges of the graph as a string, using the
                format "A -> B, B -> C, C -> D".
        """
        self._validator: Validator = Validator()

        self._edges_str: str = str("")
        self._edges: List[Edge] = []
        self._nodes: Dict[str, Node] = {}
        self._nodes_parents: Dict[Node, List[Node]] = {}
        self._nodes_children: Dict[Node, List[Node]] = {}
        self._endogenous: List[Node] = []
        self._exogenous: List[Node] = []
        self.data_optim = data_optim
        self._create_graph(edges_str)

    def __str__(self) -> str:
        return self._edges_str

    def __repr__(self) -> str:
        return f"Graph('{self._edges_str}')"

    def _create_edge(self, source: str, destination: str) -> None:
        """Creates an edge between the source and destination nodes.

        Args:
            source (str): The value of the source node of the edge.
            destination (str): The value of the destination node of the edge.
        """
        source_node = self.get_node(source)
        destination_node = self.get_node(destination)
        self._edges.append(Edge(source_node, destination_node))

    def _create_graph(self, edges_str: str) -> None:
        """Creates a graph based on the edges string.

        Args:
            edges_str (str): The edges of the graph as a string, using the
                format "A -> B, B -> C, C -> D".
        """
        self._edges_str, edges = self._validator.get_valid_edges_in_string(
            edges_str)
        for source, destination in edges:
            self._create_edge(source, destination)

        self.set_parents()
        self.set_children()
        self.set_endogenous()
        self.set_exogenous()
        self.set_nodes_numbers()

    def get_edges(self) -> List[Edge]:
        """Returns the edges of the graph.

        Returns:
            List[Edge]: The edges of the graph.
        """
        return self._edges

    def get_edges_as_str(self) -> List[str]:
        """Returns the edges of the graph as strings.

        Returns:
            List[str]: The edges of the graph as strings.
        """
        return [str(edge) for edge in self.get_edges()]

    def get_nodes(self) -> List[Node]:
        """Returns the nodes of the graph.

        Returns:
            List[Node]: The nodes of the graph.
        """
        return list(self._nodes.values())

    def get_node(self, node_value: str) -> Node:
        """Returns a node from the graph. If the node does not exist, it is
        created.

        Args:
            node_value (str): The value of the node.

        Returns:
            Node: The node from the graph with the specified value.
        """
        if node_value not in self._nodes:
            self._nodes[node_value] = Node(node_value)
        return self._nodes[node_value]

    def get_parents(self) -> Dict[Node, List[Node]]:
        """Returns the parents of the nodes in the graph. If the parents have
        not been set, they are set.

        Returns:
            Dict[Node, List[Node]]: The parents of the nodes in the graph. The
                keys are the nodes and the values are the parents of the nodes.
        """
        if not self._nodes_parents:
            self.set_parents()
        return self._nodes_parents

    def set_parents(self) -> None:
        """Sets the nodes parents dictionary."""
        for node in self.get_nodes():
            self._nodes_parents[node] = node.get_parents()

    def get_children(self) -> Dict[Node, List[Node]]:
        """Returns the children of the nodes in the graph. If the children have
        not been set, they are set.

        Returns:
            Dict[Node, List[Node]]: The children of the nodes in the graph. The
                keys are the nodes and the values are the children of the nodes
        """
        if not self._nodes_children:
            self.set_children()
        return self._nodes_children

    def set_children(self) -> None:
        """Sets the nodes children dictionary."""
        for node in self.get_nodes():
            self._nodes_children[node] = node.get_children()

    def get_endogenous(self) -> List[Node]:
        """Returns the endogenous nodes in the graph. If the list of endogenous
        nodes has not been set, it is set.

        Returns:
            List[Node]: The endogenous nodes in the graph.
        """
        if not self._endogenous:
            self.set_endogenous()
        return self._endogenous

    def set_endogenous(self) -> None:
        """Sets the list of endogenous nodes in the graph."""
        endogenous: List[Node] = []
        for node in self.get_nodes():
            if node.is_endogenous():
                endogenous.append(node)
        self._endogenous = endogenous

    def get_exogenous(self) -> List[Node]:
        """Returns the exogenous nodes in the graph. If the list of exogenous
        nodes has not been set, it is set.

        Returns:
            List[Node]: The exogenous nodes in the graph.
        """
        if not self._exogenous:
            self.set_exogenous()
        return self._exogenous

    def set_exogenous(self) -> None:
        """Sets the list of exogenous nodes in the graph."""
        exogenous: List[Node] = []
        for node in self.get_nodes():
            if node.is_exogenous():
                exogenous.append(node)
        self._exogenous = exogenous

    def get_ex_parents(self, node: Node) -> Set[Node]:
        """Returns the exogenous parents of a node.

        Args:
            node (Node): The node to get the exogenous parents from.

        Returns:
            Set[Node]: The exogenous parents of the node.
        """
        return set(self._exogenous).intersection(node.get_parents())

    def set_nodes_numbers(self) -> None:
        """Sets the numbers of all nodes in the graph. The numbers are used to
        identify the sequence of nodes in the graph."""
        for i, node in enumerate(self._nodes.values()):
            node.number = i

    def add_dummy_node(
        self, node: Node, cardinality: int = None
    ) -> Node:
        """Adds a dummy node to the graph.

        Args:
            node (Node): The node to add the dummy node to.
            cardinality (:obj:`int`, optional): The cardinality of the dummy
                node. Defaults to None.

        Returns:
            Node: The dummy node added to the graph.
        """
        if not cardinality:
            cardinality = node.cardinality

        dummy_node = self.get_node(f"{node}_dummy")
        dummy_node.cardinality = cardinality
        self._edges_str += f", {node}_dummy -> {node}"
        self._create_edge(f"{dummy_node}", f"{node}")
        self.set_endogenous()
        self.set_exogenous()
        self.set_nodes_numbers()
        return dummy_node

    def define_latents_cardinalities(
        self, latents: List[str], lat_card: str
    ) -> None:
        """Defines the cardinalities of the latent nodes in the relaxed graph.

        Args:
            latents (List[str]): The values of the latent nodes in the graph.
            lat_card (str): The cardinalities of the latent nodes in the graph.
                Using the format "2, 3, 4".
        """
        latents_card = [int(card) for card in lat_card.split(", ") if card]
        for card, latent in zip(latents_card, latents):
            self.get_node(latent).cardinality = card


class Mechanism(ABC):
    """Abstract class to represent a mechanism.

    Attributes:
        _mechanism (List[int | float]): The mechanism.
    """
    def __init__(self, mechanism: List[Union[int, float]] = None) -> None:
        """Initializes the Mechanism class.

        Args:
            mechanism (:obj:`List[int | float]`, optional): The mechanism.
                Defaults to None.
        """
        self._mechanism = mechanism

    def __str__(self) -> str:
        return str(self._mechanism)

    @abstractmethod
    def __repr__(self) -> str:
        pass

    def set_mechanism(self, mechanism: List[Union[int, float]]) -> None:
        """Sets the mechanism."""
        self._mechanism = mechanism

    def get_mechanism(self) -> List[Union[int, float]]:
        """Returns the mechanism.

        Returns:
            List[int | float]: The mechanism.
        """
        return self._mechanism


class EndogenousMechanism(Mechanism):
    """Class to represent an endogenous mechanism. Inherits from Mechanism.

    Attributes:
        r_function (List[Tuple[int, ...]]): The r function. The r function is a
            list of tuples, where each tuple represents a possible combination
            of values for the node's parents. For example, if the node has two
            parents with cardinalities 2 and 3, the r function will be
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)].
    """
    def __init__(self, mechanism: List[Union[int, float]] = None) -> None:
        """Initializes the EndogenousMechanism class.

        Args:
            mechanism (:obj:`List[Union[int, float]]`, optional): The
                mechanism. Defaults to None.
        """
        super().__init__(mechanism)
        self.r_function: List[Tuple[int, ...]] = None

    def __repr__(self) -> str:
        return f"EndogenousMechanism({self._mechanism!r})"


class ExogenousMechanism(Mechanism):
    """Class to represent an exogenous mechanism. Inherits from Mechanism.

    Attributes:
        r_index (List[Dict[Node, int]]): The r index. The keys are the children
            of the node and the values are the indexes. For example, if the
            node has two children, the r index will be
            [{child1: 0, child2: 0}, ...].
    """
    def __init__(self, mechanism: List[Union[int, float]] = None) -> None:
        """Initializes the ExogenousMechanism class.

        Args:
            mechanism (:obj:`List[Union[int, float]]`, optional): The
                mechanism. Defaults to None.
        """
        super().__init__(mechanism)
        self.r_index: List[Dict[Node, int]] = None

    def __repr__(self) -> str:
        return f"ExogenousMechanism({self._mechanism!r})"


class MechanismsDefiner():
    """Class to define the mechanisms of the nodes in a graph."""
    def __init__(self, graph: Graph) -> None:
        """Initializes the MechanismsDefiner class.

        Args:
            graph (Graph): The graph.
        """
        self._graph: Graph = graph

    def _define_r_functions(self, node: Node) -> None:
        """Defines the r functions for endogenous nodes.

        Args:
            node (Node): The node to define the r functions for. Must be
                endogenous.

        Raises:
            ValueError: If the node is not endogenous.
        """
        if not node.is_endogenous():
            raise ValueError("Node must be endogenous to use this method.")
        mult = int(1)
        for parent in node.get_parents():
            if parent.is_endogenous():
                mult *= parent.cardinality

        node.mechanism.r_function = list(
            product(*[np.arange(node.cardinality).tolist()]*mult))

    def _define_r_index(self, node: Node) -> None:
        """Defines the r index for exogenous nodes.

        Args:
            node (Node): The node to define the r index for. Must be exogenous.

        Raises:
            ValueError: If the node is not exogenous.
        """
        if not node.is_exogenous():
            raise ValueError("Node must be exogenous to use this method.")
        if "dummy" in node.get_value():
            combinations = list(
                product(*[np.arange(node.cardinality).tolist()])
            )
        else:
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

    def _define_exogenous_mechanisms(self, node: Node) -> None:
        """Defines the mechanisms for exogenous nodes.

        Args:
            node (Node): The node to define the mechanisms for. Must be
                exogenous.

        Raises:
            ValueError: If the node is not exogenous.
        """
        if not node.is_exogenous():
            raise ValueError("Node must be exogenous to use this method.")
        node.mechanism.set_mechanism([1/node.cardinality]*node.cardinality)
        self._define_r_index(node)

    def _define_mechanism_for_exogenous_parents(
        self, node: Node, ex_parents: Set[Node]
    ) -> None:
        """Defines the mechanism for endogenous nodes with exogenous parents.

        Args:
            node (Node): The node to define the mechanism for.
            ex_parents (Set[Node]): The exogenous parents of the node.
        """
        mechanism: List[int] = []
        for ex_parent in ex_parents:
            for indexes in ex_parent.mechanism.r_index:
                mechanism += [*node.mechanism.r_function[indexes[node]]]
            num_columns = len(node.mechanism.r_function[0])
            reshaped_mechanism = np.array(
                mechanism).reshape(-1, num_columns).T
            mechanism = reshaped_mechanism.flatten().tolist()
        node.mechanism.set_mechanism(mechanism)

    def _define_mechanism_for_endogenous_parents(self, node: Node) -> None:
        """Defines the mechanism for endogenous nodes with only endogenous
        parents.

        Args:
            node (Node): The node to define the mechanism for.
        """
        mechanism: List[int] = []
        parents_values: List[List[int]] = [
            np.arange(parent.cardinality).tolist()
            for parent in node.get_parents()
        ]
        parents_combinations = list(product(*parents_values))
        parents_str = [
            parent.get_value() for parent in node.get_parents()
        ]
        _grouped_df = self._graph.data_optim.unique_rows.groupby(parents_str)
        for combination in parents_combinations:
            try:
                rows = _grouped_df.get_group(combination)
                possible_functions = rows[node.get_value()].unique()
            except KeyError:
                possible_functions = []
            if len(possible_functions) == 1:
                mechanism += [int(possible_functions[0])]
            else:  # Not in the data
                mechanism += [0]

        node.mechanism.set_mechanism(mechanism)

    def _define_endogenous_mechanisms(self, node: Node) -> None:
        """Defines the mechanisms for endogenous nodes.

        Args:
            node (Node): The node to define the mechanisms for. Must be
                endogenous.

        Raises:
            ValueError: If the node is not endogenous.
        """
        if not node.is_endogenous():
            raise ValueError("Node must be endogenous to use this method.")
        ex_parents = self._graph.get_ex_parents(node)
        if ex_parents:
            self._define_mechanism_for_exogenous_parents(node, ex_parents)
        else:
            self._define_mechanism_for_endogenous_parents(node)

    def define_mechanisms(self) -> None:
        """Defines the mechanisms for the nodes in the graph."""
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
    """Class to generate a relaxed graph."""
    _graph: Graph = None

    @classmethod
    def _define_observable_cardinality(cls, node: Node) -> None:
        """Defines the cardinality of an observable node, based on the unique
        values in the data frame.

        Args:
            node (Node): The node to define the cardinality for. Must be
                observable.

        Raises:
            Exception: If an error occurs while defining the cardinality.
        """
        try:
            node.cardinality = cls._graph.data_optim.node_cardinalities[node.get_value()]
        except Exception as e:
            print(e)

    @classmethod
    def generate(cls, graph: Graph) -> 'ValidUAIGraph':
        """Generates a relaxed graph.

        Args:
            graph (Graph): The graph to generate the relaxed graph from.
            df (pd.DataFrame): The data frame.

        Returns:
            ValidUAIGraph: The relaxed graph.
        """
        cls._graph = graph
        nodes_str: List[str] = []
        for node in cls._graph.get_nodes():
            if node.get_value() in cls._graph.data_optim.column_labels:
                cls._define_observable_cardinality(node)
                nodes_str.append(f"{node} {node.cardinality}")
            else:
                nodes_str.append(f"{node} 0")

        relaxed, lat, lat_card = CanonicalPartitionsAdapter.get_relaxed_graph(
            nodes_str, cls._graph.get_edges_as_str()
        )

        cls._graph = ValidUAIGraph(relaxed, cls._graph)
        lat = lat.split(", ")
        cls._graph.define_latents_cardinalities(lat, lat_card)
        cls._graph._mechanisms_definer.define_mechanisms()

        return cls._graph


class ValidUAIGraph(Graph):
    """Class to represent a valid UAI graph. Inherits from Graph."""
    def __init__(self, edges_str: str, graph: Graph = None) -> None:
        """Initializes the ValidUAIGraph class.

        Args:
            edges_str (str): The edges of the graph as a string, using the
                format "A -> B, B -> C, C -> D".
            df (pd.DataFrame): The data frame.
            graph (:obj:`Graph`, optional): The graph used to create the valid
                UAI graph. Defaults to None.
            fixed_nodes (:obj:`List[str]`, optional): The nodes to be fixed.
                Defaults to None.
        """
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
            if graph.data_optim.column_labels:
                self._fix_nodes(graph.data_optim.column_labels)
            self._create_graph(edges_str)

        self._mechanisms_definer: MechanismsDefiner = None
        self._complete_valid_uai_graph()

    def _complete_valid_uai_graph(self) -> None:
        """Completes the valid UAI graph by defining the mechanisms and
        checking the validity of the graph.
        """
        self.check_validity()
        self._mechanisms_definer = MechanismsDefiner(self)

    def _fix_nodes(self, fixed_nodes: List[str]) -> None:
        """Fixes the selected nodes in the graph. The fixed nodes are added to
        the new graph.

        Args:
            fixed_nodes (List[str]): The nodes to be fixed.
        """
        for node_str in fixed_nodes:
            self._nodes[node_str] = self.__old_graph.get_node(node_str)
            self._nodes[node_str].reset_node()

    def _check_exogenous_nodes(self) -> None:
        """Checks the exogenous nodes in the graph. If an exogenous node is in
        the data frame (is observable), a dummy node is added to the graph."""
        for ex in self._exogenous:
            ex_str = ex.get_value()
            if ex_str in self.__old_graph.data_optim.column_labels:
                self.add_dummy_node(ex)

    def _check_non_deterministic_nodes(self) -> None:
        """Checks for non-deterministic nodes in the graph. If a node has
        parents and the number of functions is different from the number of
        parent combinations (it means the functions are probabilistic),a dummy
        node is added to the graph.
        """
        for node in self._endogenous:
            if self.get_ex_parents(node):
                continue
            subset_cols = node.get_parents_values() + [node.get_value()]            
            functions = self.__old_graph.data_optim.unique_rows.drop_duplicates(subset=subset_cols)
            parents_combinations = functions.drop_duplicates(subset=node.get_parents_values())

            if len(functions) != len(parents_combinations):
                self.add_dummy_node(node, len(functions))

    def _reorder_nodes(self) -> None:
        """Reorders the nodes in the graph. The endogenous nodes are placed
        first, followed by the exogenous nodes. The nodes are numbered in the
        order they are placed in the graph."""
        self._nodes = {end.get_value(): end for end in self._endogenous}
        self._nodes.update({ex.get_value(): ex for ex in self._exogenous})
        self.set_nodes_numbers()

    def check_validity(self) -> None:
        """Checks the validity of the graph, calling the necessary methods to
        check the exogenous nodes, non-deterministic nodes, and reorder the
        nodes."""
        self._check_exogenous_nodes()
        self._check_non_deterministic_nodes()
        self._reorder_nodes()


class CanonicalPartitionsAdapter():
    """Adapter class to use the canonical partitions method."""
    """[INTERNAL COMMENT]
            DESIGN PATTERN: Adapter

            O padrão Adapter permite que objetos com interfaces incompatíveis
            trabalhem juntos, convertendo a interface de uma classe em outra
            interface que um cliente espera.

            Benefícios do padrão Adapter:
            - Permite a integração de classes que, de outra forma, não poderiam
            trabalhar juntas devido a interfaces incompatíveis.
            - Promove a reutilização de código, permitindo o uso de classes
            existentes sem modificação.
            - Aumenta a flexibilidade e a manutenibilidade ao desacoplar o
            código do cliente das implementações específicas das classes que
            ele usa.
    """
    @staticmethod
    def get_relaxed_graph(
        nodes: List[str], edges: List[str]
    ) -> Tuple[str, str, str]:
        """Gets the relaxed graph using the canonical partitions method.

        Args:
            nodes (List[str]): The list of nodes in the graph.
            edges (List[str]): The list of edges in the graph. The edges are
                represented as strings, using the format "A -> B".

        Returns:
            relaxed (str): The relaxed graph, represented as a string using the
                format "A -> B, B -> C, C -> D".
            ex (str): The exogenous nodes in the graph, represented as a string
                using the format "A, B, C".
            ex_card (str): The cardinalities of the exogenous nodes in the
                graph, represented as a string using the format "2, 3, 4".
        """
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


class UAIGenerator:
    """Class to generate a UAI file.

    Attributes:
        uai_path (str): The path of the UAI file.
        test_name (str): The name of the test.
        edges_str (str): The edges of the graph as a string, using the format
            "A -> B, B -> C, C -> D".
        csv_file (str): The path of the CSV file.
        graph (ValidUAIGraph): The graph.
        df (pd.DataFrame): The data frame.
    """
    def __init__(self, test_name: str, edges_str: str, csv_file: str) -> None:
        """Initializes the UAIGenerator class.

        Args:
            test_name (str): The name of the test.
            edges_str (str): The edges of the graph as a string, using the
                format "A -> B, B -> C, C -> D".
            csv_file (str): The path of the CSV file.
        """
        self.uai_path: str = ""
        self.test_name: str = test_name
        self.edges_str: str = edges_str
        self.csv_file: str = csv_file
        self.graph: ValidUAIGraph = None

        self.generate()

    def _get_edges_per_node(self) -> Dict[Node, List[int]]:
        """Gets the edges for each node. The edges are represented as a list of
        integers, where each integer is the number of the node.

        Returns:
            Dict[Node, List[int]]: The edges for each node. The keys are the
                nodes and the values are the nodes parents and the node itself
                numbers.
        """
        nodes = self.graph.get_nodes()
        edges_per_node: Dict[Node, List[int]] = {}
        for node in nodes:
            edges_per_node[node] = sorted(
                [parent.number for parent in node.get_parents()]
            )
            edges_per_node[node].append(node.number)
        return edges_per_node

    def write_uai_file(self) -> None:
        """Writes the UAI file with the specified parameters."""
        edges_per_node = self._get_edges_per_node()
        nodes = self.graph.get_nodes()
        with open(self.uai_path, "w") as uai:
            uai.write("CAUSAL\n")
            uai.write(f"{len(nodes)}\n")
            uai.write(
                " ".join(
                    map(str, [node.cardinality for node in nodes])
                ) + "\n"
            )
            uai.write(f"{len(nodes)}\n")
            for node in edges_per_node:
                uai.write(
                    f"{len(edges_per_node[node])}   "
                    f"{' '.join(map(str, edges_per_node[node]))}\n"
                )
            uai.write("\n")
            for node in nodes:
                mechanism = node.mechanism.get_mechanism()
                mechanism_str = ' '.join(
                    f'{val:.15f}'.rstrip('0').rstrip('.')
                    if isinstance(val, float) else str(val)
                    for val in mechanism
                )
                uai.write("{}   {}\n".format(len(mechanism), mechanism_str))

    def get_mapping_str(self) -> str:
        """Returns the mapping of nodes to their corresponding variable names
        as a JSON string.

        This method creates a new mapping where each node is assigned a
        variable name in the format "V{i}", where {i} is the index of the
        node in the original mapping.

        Returns:
            str: A JSON string representing the new mapping of variable names
            to nodes.
        """
        nodes = self.graph.get_nodes()
        mapping = {f"V{node.number}": node.get_value() for node in nodes}
        return json.dumps(mapping)

    def generate(self) -> str:
        """Generates a UAI file based on the provided parameters.

        Returns:
            str: The path of the generated UAI file.
        """
        # Define UAI path
        self.uai_path = f"{DirectoryPaths.UAI.value}/{self.test_name}.uai"

        data_optim = DataOptim(csv_path=self.csv_file)

        # Define graph
        self.graph = RelaxedGraphGenerator.generate(Graph(self.edges_str,data_optim))

        # Write UAI file
        self.write_uai_file()

        return self.uai_path




# Example
if __name__ == "__main__":
    # r = DataOptim("data/inputs/csv/OBSERVAVEL_itau.csv")
    # r.test()


    uai = UAIGenerator(
        "OBSERVAVEL_itau",
        "T -> Y, T -> D, U -> Y, U -> T, D -> Y, E -> D",
        "data/inputs/csv/OBSERVAVEL_itau.csv"
    )
    print(uai.get_mapping_str())
