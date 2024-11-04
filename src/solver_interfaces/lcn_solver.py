import pandas as pd
import os
import glob
import sys

from lcn.inference.exact.marginal import ExactInferece
from lcn.model import LCN
from utils.output_writer import OutputWriterLCN
from utils.lcn_file_generator import create_lcn
from utils.silent_run import silent_run


sys.path.append(os.path.join(os.path.dirname(__file__), '../../LCN'))

def cleanup_lcn():
    """Remove all LCN files in the current directory."""
    lcn_files = glob.glob("*.lcn")
    for lcn_file in lcn_files:
        try:
            os.remove(lcn_file)
        except Exception as e:
            print(f"Error deleting {lcn_file}: {e}")


def lcn_solver(test_name, edges, unobservables, csv_path, treatment, outcome):
    """Solver for causal inference problem using LCN.

    Args:
        test_name (str): The name of the test case.
        edges (str): A string representing the edges of the causal graph.
        unobservables (str): A string representing the unobservables of the causal graph.
        csv_path (str): The path to the CSV file containing the data.
        treatment (str): The treatment variable.
        outcome (str): The outcome variable.
    """

    # Setting up the file to write the output
    output_file = f"outputs/{test_name}/LCN_{test_name}.txt"
    write = OutputWriterLCN(output_file)

    #Defining the first intervention
    intervention_input = (outcome, treatment, 1)

    #Loading the data
    data = pd.read_csv(csv_path)

    # Extract nodes from CSV
    nodes = data.columns.tolist()

    # Couting each configuration of the variables
    data_counts = data.value_counts().reset_index()
    data_counts.columns = nodes + ['value_counts']

    # Computing probabilities
    data_counts['prob'] = data_counts['value_counts'] / data_counts['value_counts'].sum()

    # Creating the empirical distributions
    empirical_distributions = []
    for index, row in data_counts.iterrows():
        config = row[nodes].values
        prob = row['prob']
        empirical_distributions.append((config, prob))

    # Defining the order of the variables
    var_order = nodes

    # Creating the first LCN file
    output_file_1 = f"{test_name}_{treatment}1.lcn"

    silent_run(lambda:create_lcn(edges, unobservables, intervention_input, empirical_distributions, var_order, output_file_1), output_file=output_file, new=True)
    write("==============================================")

    # Defining the second intervention
    intervention_input = (outcome, treatment, 0)

    # Creating the second LCN file
    output_file_0 = f"{test_name}_{treatment}0.lcn"

    silent_run(lambda:create_lcn(edges, unobservables, intervention_input, empirical_distributions, var_order, output_file_0), output_file=output_file)
    write("==============================================")

    # Creating the first LCN object
    l1 = LCN()
    silent_run(lambda:l1.from_lcn(file_name=output_file_1), output_file=output_file)

    # Defining the first query
    query = f"{outcome}L"
    algo1 = ExactInferece(lcn=l1)

    # Running the first query
    silent_run(lambda: algo1.run(query_formula=query), output_file=output_file)
    write("==============================================")
    write("Bounds for the first intervention")
    write(f"[{algo1.lower_bound}, {algo1.upper_bound}]")
    write("==============================================")

    # Creating the second LCN object
    l0 = LCN()
    silent_run(lambda:l0.from_lcn(file_name=output_file_0), output_file=output_file)

    # Defining the second query
    algo0 = ExactInferece(lcn=l0)

    # Running the second query
    silent_run(lambda: algo0.run(query_formula=query), output_file=output_file)
    write("==============================================")
    write("Bounds for the second intervention")
    write(f"[{algo0.lower_bound}, {algo0.upper_bound}]")
    write("==============================================")

    # Calculating the bounds for the ATE
    ate_lower_bound = algo1.lower_bound - algo0.upper_bound
    ate_upper_bound = algo1.upper_bound - algo0.lower_bound

    write("Bounds for the ATE")
    write(f"[{ate_lower_bound}, {ate_upper_bound}]")
    write("==============================================")

    # Cleaning up the LCN files
    cleanup_lcn()

if __name__ == "__main__":
    # Example usage
    edges = "Z -> X, X -> Y, Uxy -> X, Uxy -> Y"
    unobservables = "U"
    csv_path = 'data/csv/balke_pearl.csv'
    test_name = "balke_pearl"
    treatment = "X"
    outcome = "Y"
    lcn_solver(test_name, edges, unobservables, csv_path, treatment, outcome)
