import pandas as pd
import os
import glob
import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from lcn.inference.exact_marginal import ExactInferece
from lcn.model import LCN
from utils.validator import Validator
from utils.get_common_data import get_common_data
from utils.output_writer import OutputWriterLCN
from utils.file_generators.lcn_file_generator import create_lcn


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
    writer = OutputWriterLCN(output_file)

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

    writer.silent_run(lambda:create_lcn(edges, unobservables, intervention_input, empirical_distributions, var_order, output_file_1), new=True)
    writer("==============================================")

    # Defining the second intervention
    intervention_input = (outcome, treatment, 0)

    # Creating the second LCN file
    output_file_0 = f"{test_name}_{treatment}0.lcn"

    writer.silent_run(lambda:create_lcn(edges, unobservables, intervention_input, empirical_distributions, var_order, output_file_0))
    writer("==============================================")

    # Creating the first LCN object
    l1 = LCN()
    writer.silent_run(lambda:l1.from_lcn(file_name=output_file_1))

    # Defining the first query
    query = f"{outcome}L"
    algo1 = ExactInferece(lcn=l1)

    # Running the first query
    writer.silent_run(lambda: algo1.run(query_formula=query))
    writer("==============================================")
    writer("Bounds for the first intervention")
    writer(f"[{algo1.lower_bound}, {algo1.upper_bound}]")
    writer("==============================================")

    # Creating the second LCN object
    l0 = LCN()
    writer.silent_run(lambda:l0.from_lcn(file_name=output_file_0))

    # Defining the second query
    algo0 = ExactInferece(lcn=l0)

    # Running the second query
    writer.silent_run(lambda: algo0.run(query_formula=query))
    writer("==============================================")
    writer("Bounds for the second intervention")
    writer(f"[{algo0.lower_bound}, {algo0.upper_bound}]")
    writer("==============================================")

    # Calculating the bounds for the ATE
    ate_lower_bound = algo1.lower_bound - algo0.upper_bound
    ate_upper_bound = algo1.upper_bound - algo0.lower_bound

    writer("Bounds for the ATE")
    writer(f"[{ate_lower_bound}, {ate_upper_bound}]")
    writer("==============================================")

    # Cleaning up the LCN files
    cleanup_lcn()

    print("LCN solver Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--common_data", required=True, help="Path to common data")
    args = parser.parse_args()
    validator = Validator()
    data = get_common_data(validator.get_valid_path(args.common_data))
    lcn_solver(
        test_name=data['test_name'],
        edges=data['edges']['edges_str'],
        unobservables=data['unobservables'],
        csv_path=data['csv_path'],
        treatment=data['treatment'],
        outcome=data['outcome'],
    )
