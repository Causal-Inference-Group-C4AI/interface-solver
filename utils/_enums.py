from enum import Enum


class Solvers(Enum):
    DOWHY = 'dowhy'
    BCAUSE = 'bcause'
    AUTOBOUNDS = 'autobounds'
    LCN = 'lcn'


class DirectoryPaths(Enum):
    OUTPUTS = 'data/outputs'
    INPUTS = 'data/inputs'
    CSV = 'data/inputs/csv'
    LCN = 'data/inputs/lcn'
    UAI = 'data/inputs/uai'


class FilePaths(Enum):
    SHARED_DATA = "data/shared/common_data.json"
    INPUT_PROCESSOR_SCRIPT = "src/input_processor.py"
    DOWHY_SOLVER = "src/solvers/dowhy_solver.py"
    BCAUSE_SOLVER = "src/solvers/bcause_solver.py"
    LCN_SOLVER = "src/solvers/lcn_solver.py"
    AUTOBOUNDS_SOLVER = "src/solvers/autobounds_solver.py"
    DOWHY_VENV = "venv_dowhy"
    BCAUSE_VENV = "venv_bcause"
    LCN_VENV = "venv_lcn"
    AUTOBOUNDS_VENV = "venv_autobounds"
    # TODO: REVER O ENV DAQUI 
    INPUT_PROCESSOR_VENV = "venv_dowhy"


class EmptyValues(Enum):
    DICT_ATE = {"NONE":0.0}
    TUPLE_ATE = (-1.0, -1.0)
