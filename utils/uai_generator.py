import pandas as pd


def uai_generator(
    test_name,
    edges_str,
    treatment,
    outcome,
    unobservables_str,
    csv_file
) -> None:
    # Create UAI file and infos
    uai_filename = f"data/uai/{test_name}.uai"
    uai_infos = {
        "mode": "CAUSAL",
        "num_nodes": 0,
        "nodes_cardinality": [],
        "edges_for_node": [],
        "mechanisms": []
    }

    df = pd.read_csv(csv_file)  # Read CSV file

    # Define nodes
    nodes = df.columns.tolist()
    unobsorvables = unobservables_str.split(", ")
    nodes.extend(unobsorvables)

    print(nodes)

    # uai_infos["num_nodes"] = len(nodes)
    # print(uai_infos["num_nodes"])


if __name__ == "__main__":
    uai_generator(
        "balke_pearl",
        "Z -> X, X -> Y, U -> X, U -> Y",
        "X",
        "Y",
        "U",
        "data/csv/balke_pearl.csv"
    )
