import argparse
import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pandas as pd
from bcause.inference.causal.multi import EMCC
from bcause.models.cmodel import StructuralCausalModel
from utils.get_common_data import get_common_data
from utils.output_writer import OutputWriterBcause
from utils.validator import Validator
from utils._enums import DirectoryPaths


def bcause_solver(test_name: str, uai_path: str, csv_path: str, treatment: str, outcome: str, mapping: dict):
    print("Bcause solver running...")
    model = StructuralCausalModel.read(uai_path)
    renamed_model = model.rename_vars(mapping)

    dataset = pd.read_csv(csv_path)
    inf = EMCC(renamed_model, dataset, max_iter=100, num_runs=20)

    p_do0 = inf.causal_query(outcome, do={treatment: 0})
    p_do1 = inf.causal_query(outcome, do={treatment: 1})

    lower_bound = p_do1.values[1] - p_do0.values[1]
    upper_bound = p_do1.values[3] - p_do0.values[3]

    output_file = f"{DirectoryPaths.OUTPUTS.value}/{test_name}/bcause_{test_name}.txt"
    writer = OutputWriterBcause(output_file)
    
    writer("==============================================")
    writer(f'P({outcome}=1|do({treatment}=0)) = {[p_do0.values[1], p_do0.values[3]]}')
    writer(f'P({outcome}=1|do({treatment}=1)) = {[p_do1.values[1], p_do1.values[3]]}')
    writer(f"Causal effect lies in the interval [{lower_bound}, {upper_bound}]")
    writer("==============================================")
    print("Bcause solver Done.")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.CRITICAL)
    parser = argparse.ArgumentParser()
    parser.add_argument("--common_data", required=True, help="Path to common data")
    args = parser.parse_args()
    validator = Validator()
    data = get_common_data(validator.get_valid_path(args.common_data))
    bcause_solver(
        test_name=data['test_name'],
        uai_path=data['uai_path'],
        csv_path=data['csv_path'],
        treatment=data['treatment'],
        outcome=data['outcome'],
        mapping=data['mapping'],
    )
