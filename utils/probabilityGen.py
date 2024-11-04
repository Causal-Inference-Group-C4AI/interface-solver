import random as rand

import numpy as np

from graph import Graph


def distribution(graph: Graph, prec=3):

    probs: list[np.array] = []

    for i in graph.exogenous:
        card = graph.cardinalities[i]

        dist = np.array([rand.uniform(1, 100) for _ in range(card)])

        dist /= np.sum(dist)
        dist = np.trunc(dist*10**prec)/10**prec
        dist[-1] = 1 - np.sum(dist[0: card-1])
        probs.append(dist)

    return probs


def findExogen(graph: Graph):
    # function that finds all exogenous indexs(implement in graph parser?)

    exogenIndex: list[int] = []
    endogenIndex: list[int] = []

    for i in range(1, graph.num_nodes + 1):
        if not (bool(graph.parents[i])):
            exogenIndex.append(i)
        else:
            endogenIndex.append(i)

    return exogenIndex, endogenIndex


# test function
if __name__ == "__main__":
    graph: Graph = Graph.parse()
    for i in range(1, graph.num_nodes + 1):
        if graph.cardinalities[i] < 1:
            graph.cardinalities[i] = 2

    print(graph.adj)
