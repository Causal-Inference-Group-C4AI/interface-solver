import warnings

import pandas as pd
from bcause.inference.causal.multi import EMCC
from bcause.models.cmodel import StructuralCausalModel

warnings.simplefilter(action='ignore')


def write_output(output, output_path="outputs/bcause_output_NO_NAME.txt", new=False):
    """Write the output to a file.

    Args:
        output (str): The output to write to the file.
        output_path (str, optional): The path to the output file. Defaults to "outputs/autobounds_output.txt".
        new (bool, optional): Whether to write a new file or append to an existing one. Defaults to False.
    """
    mode = "w" if new else "a"
    with open(output_path, mode) as f:
        f.write(output + "\n")


def bcause_solver(test_name: str, uai_path: str, csv_path: str, treatment: str, outcome: str, mapping: dict):
    model = StructuralCausalModel.read(uai_path)
    renamed_model = model.rename_vars(mapping)

    dataset = pd.read_csv(csv_path)
    inf = EMCC(renamed_model, dataset, max_iter=100, num_runs=20)

    p_do0 = inf.causal_query(outcome, do={treatment: 0})
    p_do1 = inf.causal_query(outcome, do={treatment: 1})

    # Extracting bounds
    lower_bound = p_do1.values[1] - p_do0.values[1]
    upper_bound = p_do1.values[3] - p_do0.values[3]
    output_file_path = f"outputs/{test_name}/bcause_{test_name}.txt"
    write_output("==============================================", output_path=output_file_path, new=True)
    write_output(f'P({outcome}=1|do({treatment}=0)) = {[p_do0.values[1], p_do0.values[3]]}', output_path=output_file_path)
    write_output(f'P({outcome}=1|do({treatment}=1)) = {[p_do1.values[1], p_do1.values[3]]}', output_path=output_file_path)
    write_output(f"Causal effect lies in the interval [{lower_bound}, {upper_bound}]", output_path=output_file_path)
    write_output("==============================================", output_path=output_file_path)
