import numpy as np
import pandas as pd
import argparse
import json
from pathlib import Path

from generator import generateMechanisms
from graph import Graph
from probabilityGen import distribution


def dataGen(graph: Graph, numSamp=int(1e3), csv_path='./data/csv/unobDataGenOutput.csv'):

    distExogen: list[np.array] = distribution(graph)
    truthTable: list[list[np.array]] = generateMechanisms(graph)

    experiment: list[list[int]] = []
    print(graph.exogenous)
    for _ in range(numSamp):
        vals: list[int] = np.zeros(graph.num_nodes, dtype=int)

        exogen_vals: list[int] = [np.random.choice(a=np.arange(
            1, len(dist) + 1),  p=dist) for dist in distExogen]
        for num_exog, node_exog in enumerate(graph.exogenous):

            vals[node_exog - 1] = exogen_vals[num_exog]

        for num_endo, node_endo in enumerate(graph.endogenous):

            parents_vals: np.array = np.array(
                [vals[j - 1] for j in graph.parents[node_endo]], dtype=int)

            for event in truthTable[num_endo]:
                if (parents_vals == event[:-1]).all():
                    vals[node_endo - 1] = event[-1]

        if 0 in vals:
            print("data generation failed")
            return None

        experiment.append(vals)
    
    experiment = [[element - 1 for element in row] for row in experiment]
    df = pd.DataFrame(experiment)

    df_label = []
    for i in range(1, graph.num_nodes+1):   
        df_label.append(graph.index_to_label[i])

    df.columns = df_label
    df = df.drop(columns=["U"])
    df.to_csv(csv_path, index=False)

    return experiment


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generates csv from a giving DAG.")
    parser.add_argument('file_path',
                        help='The path to the file you want to read')
    args = parser.parse_args()

    graph: Graph = Graph.parse(input_path=args.file_path)
    # folder_name = Path(f"outputs/{test['test_name']}")
    # folder_name.mkdir(parents=True, exist_ok=True)

    for i in range(1, graph.num_nodes + 1):
        if graph.cardinalities[i] < 1:
            graph.cardinalities[i] = 2

    print(dataGen(graph=graph, numSamp=1000))
