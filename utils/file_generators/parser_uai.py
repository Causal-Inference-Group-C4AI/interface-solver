import itertools

import networkx as nx
import numpy as np
from pandas import DataFrame

from utils.file_generators.csv_generator import probsHelper
from utils._enums import DirectoryPaths


class UAIParser:
    """
    A class to parse a UAI file and generate data from it.

    Attributes:
        filepath (str): path to the UAI file
        nodes (list[str]): list of node names in order of appearance
            in the UAI file
        network_type: type of network
        num_variables: number of variables
        domain_sizes: list of domain sizes
        parents: list of parents for each variable
        tables: list of conditional probability tables
        graph: networkx DiGraph object representing the network
        data: pandas DataFrame with the generated data
    """

    def __init__(self, filepath: str, nodes: list[str]) -> None:
        """
        Initialize the parser with the file path and node names.

        Args:
            filepath (str): path to the UAI file
            nodes (list[str]): list of node names in order of appearance
                in the UAI file
        """
        self.filepath = filepath
        self.info = None
        self.nodes = nodes
        self.network_type = None
        self.num_variables = None
        self.domain_sizes = []
        self.parents = []
        self.tables = []
        self.graph = nx.DiGraph()
        self.index = 0

    def parse(self) -> None:
        """
        Parse the UAI file and store the network information.
        """
        with open(self.filepath, 'r') as file:
            self.info = file.read().replace('\n', ' ').split()
            self.index = 0

            # Cabeçalho: tipo de rede
            self.network_type = self.info[self.index]
            self.index += 1

            # Número de variáveis
            self.num_variables = int(self.info[self.index])
            self.index += 1

            # Tamanhos dos domínios
            self.domain_sizes = list(
                map(int, self.info[2:2+self.num_variables]))
            self.index += self.num_variables

            # Lendo a lista de pais
            num_factors = int(self.info[self.index])
            self.index += 1
            self.parents = []
            for _ in range(num_factors):
                num_parents = int(self.info[self.index]) - 1
                self.index += 1
                self.parents.append(
                    list(map(int,
                             self.info[self.index:self.index + num_parents])))
                self.index += num_parents + 1

            # Lendo as tabelas de mecanismos
            self.tables = []
            if self.network_type == 'BAYES':
                self.index = self.bayes_parser()
            elif self.network_type == 'CAUSAL':
                self.index = self.causal_parser()

        # Gerar o grafo
        self.graph = nx.DiGraph()
        for i in range(self.num_variables):
            self.graph.add_node(i)
        for i, parents in enumerate(self.parents):
            for parent in parents:
                self.graph.add_edge(parent, i)

        for i, title in enumerate(self.nodes):
            nx.relabel_nodes(self.graph, {i: title}, copy=False)

    def bayes_parser(self) -> None:
        """Parse the network for a Bayesian network."""
        for i in range(self.num_variables):
            # Quantidade de entradas na tabela
            num_entries = int(self.info[self.index])
            self.index += 1
            flat_table = list(
                map(float, self.info[self.index:self.index + num_entries])
            )
            self.index += num_entries

            # Obtenha o número de dimensões da tabela (pais + nó)
            dims = [
                self.domain_sizes[parent] for parent in self.parents[i]
            ] + [self.domain_sizes[i]]

            # Reformatar a tabela plana em uma matriz multidimensional
            table = np.array(flat_table).reshape(dims)
            self.tables.append(table)

    def causal_parser(self) -> None:
        """Parse the network for a Causal network."""
        for i in range(self.num_variables):
            # Quantidade de entradas na tabela
            num_entries = int(self.info[self.index])
            self.index += 1
            flat_table = []
            for value in self.info[self.index:self.index + num_entries]:
                if "." in value:
                    flat_table.append(float(value))
                else:
                    one_hot = [0] * self.domain_sizes[i]
                    one_hot[int(value)] = 1
                    flat_table.extend(one_hot)
            self.index += num_entries

            # Obtenha o número de dimensões da tabela (pais + nó)
            dims = [self.domain_sizes[parent]
                    for parent in self.parents[i]] + [self.domain_sizes[i]]

            # Reformatar a tabela plana em uma matriz multidimensional
            table = np.array(flat_table).reshape(dims)
            self.tables.append(table)

    def calculate_probability(self, outcome: list[int]) -> float:
        """
        Calculate the probability of a given outcome.

        Args:
            outcome (list[int]): list of variable values

        Returns:
            float: probability of the outcome
        """
        probability = 1.0

        for i, value in enumerate(outcome):
            if len(self.parents[i]) == 0:
                probability *= self.tables[i][value]
            else:
                parent_values = tuple(outcome[parent]
                                      for parent in self.parents[i])
                probability *= self.tables[i][parent_values + (value,)]

        return probability

    def calculate_probabilities_for_outcomes(
        self, outcomes: list[list[int]]
    ) -> list[float]:
        """
        Calculate the probabilities of a list of outcomes.

        Args:
            outcomes (list[list[int]]): list of outcomes

        Returns:
            list[float]: list of probabilities
        """
        probabilities = []
        for outcome in outcomes:
            prob = self.calculate_probability(outcome)
            probabilities.append(prob)
        return probabilities

    def generate_data(
        self, test_name: str, csv_flag: bool = True
    ) -> str | DataFrame:
        """
        Generate data from the network.

        Returns:
            DataFrame: DataFrame with the generated data
        """
        values = [list(range(size)) for size in self.domain_sizes]
        outcomes = list(itertools.product(*values))
        probs = self.calculate_probabilities_for_outcomes(outcomes)
        probabilities = [[sublist, val]
                         for sublist, val in zip(outcomes, probs)]
        return probsHelper(self.nodes, probabilities, test_name, csv_flag)

    def display(self) -> None:
        """
        Display the network information.
        """
        print(f"Tipo de rede: {self.network_type}")
        print(f"Número de variáveis: {self.num_variables}")
        print(f"Tamanhos dos domínios: {self.domain_sizes}")
        print("Pais das variáveis:")
        for parents in self.parents:
            print(f"  {parents}")
        print("Tabelas de probabilidades condicionais:")
        for table in self.tables:
            print(table, end="\n\n\n")


if __name__ == "__main__":
    # Parsing the UAI file
    model_uai = UAIParser(f"{DirectoryPaths.UAI.value}/variation_1.uai",
                          ["X1", "X2", "U1", "U2", "U3"])
    model_uai.parse()

    # Load the data
    data = model_uai.generate_data()
    print(data)
