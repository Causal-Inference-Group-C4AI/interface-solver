import networkx as nx
import pandas as pd
from dowhy import CausalModel

from utils.unused.dataGen import dataGen
from utils.canonical_partitions.graph import Graph


def estimatedATE(graph: Graph, query: list[str]):
    data: pd.DataFrame = pd.DataFrame(
        dataGen(graph=graph, numSamp=int(1e2)),
        columns=[
            graph.index_to_label[i] for i in range(1, graph.num_nodes + 1)
        ]
    )
    data = data.replace(to_replace=2, value=0)
    print(data)
    model = CausalModel(data=data,
                        treatment=query[0],
                        outcome=query[1],
                        graph=createDag(graph=graph)
                        )
    # model.view_model()
    identified_estimand = model.identify_effect()
    print(identified_estimand)
    estimate_weighting = model.estimate_effect(
        identified_estimand,
        method_name="backdoor.linear_regression")

    print("ATE: ", estimate_weighting.value)
    return estimate_weighting.value


def createDag(graph: Graph):
    inpDAG: nx.DiGraph = nx.DiGraph()

    for i in range(1, graph.num_nodes+1):
        inpDAG.add_node(i)

    for parent, edge in enumerate(graph.adj):
        if bool(edge):
            for ch in edge:
                inpDAG.add_edge(parent, ch)

    for i in range(1, graph.num_nodes + 1):

        name_node = graph.index_to_label[i]

        nx.relabel_nodes(inpDAG, {i: name_node}, copy=False)
    return inpDAG


if __name__ == "__main__":
    graph: Graph = Graph.parse()
    for i in range(1, graph.num_nodes + 1):
        if graph.cardinalities[i] < 1:
            graph.cardinalities[i] = 2
    print(estimatedATE(graph=graph, query=["V2", "V3"]))
