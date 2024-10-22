import warnings

import networkx as nx
import numpy as np
import pandas as pd
from dowhy import CausalModel

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


class Output:
    """
    A utility class for managing output to both the console and a file.

    This class provides a simple mechanism for printing messages to the console
    and simultaneously writing them to a specified output file. The file is
    automatically cleared upon initialization to ensure a fresh output for each
    session.

    **Attributes**:
        output_file (str): The file path to which the output will be written.
            Defaults to "outputs/dowhy_output.txt".

    **Methods**:
        __call__(text: str, end: str):
            Prints a message to the console and appends it to the output file.
        reset():
            Resets the content of the output file by clearing it.
    """

    def __init__(self, output_file: str = "outputs/dowhy_output.txt") -> None:
        """Initializes the Output class and resets the file.

        Args:
            output_file (str, optional): The file to write output to.
                Defaults to "outputs/dowhy_output.txt".
        """
        self.output_file = output_file
        self.reset()

    def __call__(self, text: str = "", end: str = "\n") -> None:
        """Prints a message and writes it to a file.

        Args:
            text (str, optional): Message to be outputted and written to the
                file. Defaults to "".
            end (str, optional): End of the message. Defaults to "\\n".
        """
        print(text, end=end)
        try:
            with open(self.output_file, 'a') as file:
                file.write(text + end)
        except IOError as e:
            print(f"Error writing to file {self.output_file}: {e}")

    def reset(self) -> None:
        """Resets the output file by clearing its content."""
        try:
            with open(self.output_file, 'w') as file:
                file.write("")
        except IOError as e:
            print(f"Error resetting file {self.output_file}: {e}")


def dowhy_solver(
    test_name: str,
    csv_path: str,
    edges_str: str,
    treatment: str,
    outcome: str
) -> None:
    """Solves a causal inference problem using DoWhy.

    Args:
        test_name (str): Name of the test case.
        csv_path (str): Path to the CSV file with the data.
        edges_str (str): String with the edges of the graph.
        treatment (str): Name of the treatment variable.
        outcome (str): Name of the outcome variable.
    """
    # Data and graph
    data = pd.read_csv(csv_path)
    edges = [tuple(edge.split(' -> ')) for edge in edges_str.split(', ')]
    graph = nx.DiGraph(edges)

    # Step 1: Model
    model = CausalModel(
        data=data,
        treatment=treatment,
        outcome=outcome,
        graph=graph
    )

    # Step 2: Identify
    identified_estimand = model.identify_effect()
    estimands = {"backdoor": None, "iv": None, "frontdoor": None}
    output_file = f"outputs/{test_name}/dowhy_{test_name}.txt"
    output = Output(output_file, True)
    output("Estimands found:", end=" ")
    for estimand, value in identified_estimand.estimands.items():
        if estimand in estimands:
            estimands[estimand] = value is not None
            output(f"{estimand} " if estimands[estimand] else "", end="")
    output()

    # Step 3: Estimate with all available methods
    estimation_methods = {
        "backdoor": [
            "linear_regression",
            "propensity_score_matching",
            "propensity_score_stratification",
            "propensity_score_weighting"
        ],
        "iv": [
            "instrumental_variable"
        ],
        "frontdoor": []
    }

    for estimand in estimation_methods.keys():
        if estimands[estimand]:
            for method in estimation_methods[estimand]:
                method_name = f"{estimand}.{method}"
                try:
                    estimate = model.estimate_effect(
                        identified_estimand,
                        method_name=method_name,
                        test_significance=True,
                        confidence_intervals=True
                    )
                    output("-" * 80)
                    output(f"Estimation using {method_name}:")
                    output(f"ATE = {estimate.value}")

                    # output the p-value
                    p_value = estimate.test_stat_significance()["p_value"]
                    output(f"P-value: {p_value}")

                    # output the confidence interval
                    confidence_intervals = estimate.get_confidence_intervals()
                    if isinstance(confidence_intervals, np.ndarray):
                        confidence_intervals = confidence_intervals.flatten()
                        confidence_intervals = confidence_intervals.tolist()
                    else:
                        confidence_intervals = [float(_)
                                                for _ in confidence_intervals]

                    output(f"Confidence interval: {confidence_intervals}")
                    output("-" * 80)
                except Exception as e:
                    output(f"Failed to estimate using {method_name}: {str(e)}")

    # # Step 4: Refute
    # refutation = model.refute_estimate(
    #     identified_estimand,
    #     estimate,
    #     method_name="random_common_cause"
    # )


if __name__ == "__main__":
    dowhy_solver(
        test_name='balke_pearl',
        csv_path='data/csv/balke_pearl.csv',
        edges_str="Z -> X, X -> Y",
        treatment='X',
        outcome='Y'
    )
