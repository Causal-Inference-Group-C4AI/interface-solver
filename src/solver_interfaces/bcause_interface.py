from bcause.inference.causal.multi import EMCC
from bcause.models.cmodel import StructuralCausalModel
import pandas as pd
import bcause as bc

def bcause_solver(uai_path: str, csv_path: str, treatment_variable: str, outcome_variable: str):
    # Quando se lê do .UAI as variáveis são nomeadas como Vi, 0 <= i <= n-1, n é o número de nós que tem no grafo.
    model = StructuralCausalModel.read(uai_path)

    mapping = {"V0":"Z", "V1":"X", "V2": "Y"}
    renamed_model = model.rename_vars(mapping)
    
    dataset = pd.read_csv(csv_path)
    inf = EMCC(renamed_model, dataset, max_iter=100, num_runs=20)

    X, Y = treatment_variable, outcome_variable
    p_do0 = inf.causal_query(Y, do={X: 0})
    p_do1 = inf.causal_query(Y, do={X: 1})

    print(
        f'P(OUTCOME=1|do(Treatment=0)) = {[p_do0.values[1], p_do0.values[3]]}')
    print(
        f'P(OUTCOME=1|do(Treatment=1)) = {[p_do1.values[1], p_do1.values[3]]}')
    print('ATE                          = ',
          [p_do1.values[1] - p_do0.values[1],
           p_do1.values[3] - p_do0.values[3]])
    pass
