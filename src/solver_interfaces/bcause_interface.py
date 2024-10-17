from bcause.inference.causal.multi import EMCC
from bcause.models.cmodel import StructuralCausalModel
import pandas as pd
import bcause as bc

def bcause_solver(uai_path, csv_path):
    model = StructuralCausalModel.read(uai_path)
    # TODO: esse UAI com o csv não tá funcionando
    # dataset =  pd.read_csv(csv_path)
    bc.randomUtil.seed(1)
    dataset = model.sampleEndogenous(1000)

    inf = EMCC(model, dataset, max_iter=100, num_runs=20)
    cause, effect = [model.endogenous[i] for i in [0, -1]]

    X, Y = cause, effect
    p_do0 = inf.causal_query(Y, do={X: 0})
    p_do1 = inf.causal_query(Y, do={X: 1})
    # actual = p.values

    # The lowest prob Y = 0 | do(T=0)
    # p.values[0]

    # The lowest prob Y = 1 | do(T=0)
    # p.values[1]

    # The highest prob Y = 0 | do(T=0)
    # p.values[2]

    # The highest prob Y = 1 | do(T=0)
    # p.values[3]
    print(
        f'P(OUTCOME=1|do(Treatment=0)) = {[p_do0.values[1], p_do0.values[3]]}')
    print(
        f'P(OUTCOME=1|do(Treatment=1)) = {[p_do1.values[1], p_do1.values[3]]}')
    print('ATE                          = ',
          [p_do1.values[1] - p_do0.values[1],
           p_do1.values[3] - p_do0.values[3]])
    pass
