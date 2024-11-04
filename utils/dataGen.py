import numpy as np
import pandas as pd
import argparse

from generator import generateMechanisms
from graph import Graph
from probabilityGen import distribution


def teste_itau_simples_data_generation():
    # Set a random seed for reproducibility
    np.random.seed(42)

    # Define the number of samples
    n = 1000

    # Step 1: Generate exogenous variables U and E

    # U is an exogenous binary variable (e.g., representing an unobserved confounder)
    # We can assume P(U=1) = 0.5
    p_U = 0.5
    U = np.random.choice([0, 1], size=n, p=[1 - p_U, p_U])

    # E is another exogenous binary variable
    # We can assume P(E=1) = 0.5
    p_E = 0.5
    E = np.random.choice([0, 1], size=n, p=[1 - p_E, p_E])

    # Step 2: Generate T given U
    # T depends on U: U -> T
    # Define P(T=1 | U)
    P_T_given_U = {
        0: 0.3,  # P(T=1 | U=0)
        1: 0.7   # P(T=1 | U=1)
    }

    T = np.zeros(n, dtype=int)
    for i in range(n):
        U_i = U[i]
        p_T = P_T_given_U[U_i]
        T[i] = np.random.choice([0, 1], p=[1 - p_T, p_T])

    # Step 3: Generate D given T and E
    # D depends on T and E: T -> D, E -> D
    # Define P(D=1 | T, E)
    P_D_given_T_E = {
        (0, 0): 0.1,  # P(D=1 | T=0, E=0)
        (0, 1): 0.4,  # P(D=1 | T=0, E=1)
        (1, 0): 0.6,  # P(D=1 | T=1, E=0)
        (1, 1): 0.9   # P(D=1 | T=1, E=1)
    }

    D = np.zeros(n, dtype=int)
    for i in range(n):
        T_i = T[i]
        E_i = E[i]
        p_D = P_D_given_T_E[(T_i, E_i)]
        D[i] = np.random.choice([0, 1], p=[1 - p_D, p_D])

    # Step 4: Generate Y given T, U, and D
    # Y depends on T, U, and D: T -> Y, U -> Y, D -> Y
    # Define P(Y=1 | T, U, D)
    P_Y_given_T_U_D = {
        (0, 0, 0): 0.1,  # P(Y=1 | T=0, U=0, D=0)
        (0, 0, 1): 0.3,  # P(Y=1 | T=0, U=0, D=1)
        (0, 1, 0): 0.2,  # P(Y=1 | T=0, U=1, D=0)
        (0, 1, 1): 0.4,  # P(Y=1 | T=0, U=1, D=1)
        (1, 0, 0): 0.5,  # P(Y=1 | T=1, U=0, D=0)
        (1, 0, 1): 0.7,  # P(Y=1 | T=1, U=0, D=1)
        (1, 1, 0): 0.6,  # P(Y=1 | T=1, U=1, D=0)
        (1, 1, 1): 0.8   # P(Y=1 | T=1, U=1, D=1)
    }

    Y = np.zeros(n, dtype=int)
    for i in range(n):
        T_i = T[i]
        U_i = U[i]
        D_i = D[i]
        p_Y = P_Y_given_T_U_D[(T_i, U_i, D_i)]
        Y[i] = np.random.choice([0, 1], p=[1 - p_Y, p_Y])

    # Create a DataFrame to store the generated data
    labels = []

    data = pd.DataFrame({
        'E': E,
        'T': T,
        'D': D,
        'Y': Y,
        'U': U
    })

    data.to_csv("itau_teste.csv", index=False)
    
    data = data.drop(columns=['U'])
    data.to_csv("unob_itau_teste.csv", index=False)
    

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

    df.to_csv(csv_path, index=False)

    return experiment


if __name__ == "__main__":
    teste_simples_data_generation()
    # parser = argparse.ArgumentParser(
    #     description="Generates csv from a giving DAG.")
    # parser.add_argument('file_path',
    #                     help='The path to the file you want to read')
    # args = parser.parse_args()

    # graph: Graph = Graph.parse(input_path=args.file_path)
    # # folder_name = Path(f"outputs/{test['test_name']}")
    # # folder_name.mkdir(parents=True, exist_ok=True)

    # for i in range(1, graph.num_nodes + 1):
    #     if graph.cardinalities[i] < 1:
    #         graph.cardinalities[i] = 2

    # print(dataGen(graph=graph, numSamp=1000))
