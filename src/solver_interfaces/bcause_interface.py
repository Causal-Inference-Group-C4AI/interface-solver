import warnings

import pandas as pd
from bcause.inference.causal.multi import EMCC
from bcause.models.cmodel import StructuralCausalModel
from utils.output_writer import OutputWriterBcause

warnings.simplefilter(action='ignore')


def bcause_solver(test_name: str, uai_path: str, csv_path: str, treatment: str, outcome: str, mapping: dict):
    model = StructuralCausalModel.read(uai_path)
    renamed_model = model.rename_vars(mapping)

    dataset = pd.read_csv(csv_path)
    inf = EMCC(renamed_model, dataset, max_iter=100, num_runs=20)

    p_do0 = inf.causal_query(outcome, do={treatment: 0})
    p_do1 = inf.causal_query(outcome, do={treatment: 1})

    lower_bound = p_do1.values[1] - p_do0.values[1]
    upper_bound = p_do1.values[3] - p_do0.values[3]

    output_file = f"outputs/{test_name}/bcause_{test_name}.txt"
    writer = OutputWriterBcause(output_file)
    
    writer("==============================================")
    writer(f'P({outcome}=1|do({treatment}=0)) = {[p_do0.values[1], p_do0.values[3]]}')
    writer(f'P({outcome}=1|do({treatment}=1)) = {[p_do1.values[1], p_do1.values[3]]}')
    writer(f"Causal effect lies in the interval [{lower_bound}, {upper_bound}]")
    writer("==============================================")
