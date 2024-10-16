import pytest

import bcause as bc
from bcause.factors.imprecise import IntervalProbFactor
from bcause.inference.causal.multi import EMCC
from bcause.inference.causal.elimination import CausalVariableElimination
from bcause.models.cmodel import StructuralCausalModel

from numpy.testing import assert_array_almost_equal

def bcause_solver(uai_path, csv_path):
    pass

def because_solver_old():
    n_tests = int(input('How many tests do you wanna run? '))

    test_filenames = list()
    for _ in range(n_tests):
        filename = input('What is the .uai of your test? ')
        test_filenames.append(filename)

    models, datasets, infobjects, causes, effects = create_models(test_filenames)

    for test in test_filenames:
        inf = infobjects[test]
        X,Y = causes[test], effects[test]

        test_causal_query(inf, X, Y)
    

def create_models(test_filenames: list[str]):
    models, datasets, infobjects, causes, effects = dict(), dict(), dict(), dict(), dict()
    for l in test_filenames:
        models[l] = StructuralCausalModel.read(f"../../tests/{l}.uai")
        bc.randomUtil.seed(1)
        datasets[l] = models[l].sampleEndogenous(1000)
        infobjects[l] = EMCC(models[l], datasets[l], max_iter=100, num_runs=20)
        causes[l], effects[l] = [models[l].endogenous[i] for i in [0, -1]]
        return models, datasets, infobjects, causes, effects


def test_causal_query(inf, X, Y):
    p_do0 = inf.causal_query(Y, do={X:0})
    p_do1 = inf.causal_query(Y, do={X:1})
  
    # The lowest  p(Y = 0 | do(T=0)) = p_do0.values[0]
    # The lowest  p(Y = 1 | do(T=0)) = p_do0.values[1]
    # The highest p(Y = 0 | do(T=0)) = p_do0.values[2]
    # The highest p(Y = 1 | do(T=0)) = p_do0.values[3]

    print(f'P(Y=1|do(X=0)) = {[p_do0.values[1], p_do0.values[3]]}')
    print(f'P(Y=1|do(X=1)) = {[p_do1.values[1], p_do1.values[3]]}')
    print(f'ATE            = {[p_do1.values[1] - p_do0.values[1], p_do1.values[3] - p_do0.values[3]]}')
