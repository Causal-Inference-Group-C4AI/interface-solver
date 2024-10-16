import pytest

import bcause as bc
from bcause.factors.imprecise import IntervalProbFactor
from bcause.inference.causal.multi import EMCC
from bcause.inference.causal.elimination import CausalVariableElimination
from bcause.models.cmodel import StructuralCausalModel

from numpy.testing import assert_array_almost_equal

def bcause_solver(uai_path, csv_path):
    pass
