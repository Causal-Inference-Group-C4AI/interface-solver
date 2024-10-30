import math

from c_component import CComponent
from graph import Graph
from logger import Logger


def bound_canonical_partitions(
    dag_components: list[list[int]],
    cardinalities: list[int],
    parents: list[int]
):
    partitions: list[int] = []
    for i, component in enumerate(dag_components):
        canonical_partition = 1
        for node in component.nodes:
            if cardinalities[node] > 1:
                base = cardinalities[node]
                exponent = 1
                for parent in parents[node]:
                    if cardinalities[parent] > 1:
                        exponent *= cardinalities[parent]
                canonical_partition *= math.pow(base, exponent)
        print(
            f"For the c-component #{i + 1} the "
            f"equivalent canonical partition = {int(canonical_partition)}"
        )
        partitions.append(canonical_partition)

    return partitions


def generateRelaxed(graph: Graph, latentCardinalities: list[int]):
    relaxedGraph: str = ""
    unob: str = ""
    unobCardinalities: str = ", ".join(
        map(lambda x: str(int(x)), latentCardinalities))

    for index, component in enumerate(graph.dag_components):
        currUnobLabel: str = "U" + str(index)
        unob += f", {currUnobLabel}"
        for node in component.nodes:
            if graph.cardinalities[node] > 1:
                relaxedGraph += (
                    f", {currUnobLabel} -> {graph.index_to_label[node]}"
                )

    # adicionar arestas que saem do node depois, pois se nao tiver pai exogeno
    # nao pertence a nenhum c-component
    for index, label in graph.index_to_label.items():
        if graph.cardinalities[index] > 1:
            for node in graph.adj[index]:
                relaxedGraph += f", {label} -> {graph.index_to_label[node]}"

    return relaxedGraph[2:], unob[2:], unobCardinalities


def completeRelaxed(verbose=False):
    graph = Graph.parse()

    CComponent.find_cComponents(graph)

    if verbose:
        Logger.debugGraph(graph)
        Logger.debugCcomponents(graph)

    latentCardinalities: list[int] = bound_canonical_partitions(
        graph.dag_components, graph.cardinalities, graph.parents)

    return generateRelaxed(graph, latentCardinalities)


def main():
    adjRelaxed, unobRelaxed, unobCard = completeRelaxed(verbose=True)

    print(
        f"Relaxed graph edges: {adjRelaxed} \n \n"
        f"Unobservable variables: {unobRelaxed} \n \n"
        f"Cardinalities: {unobCard}")


if __name__ == "__main__":
    main()
