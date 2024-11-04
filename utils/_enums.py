from enum import Enum


class Solvers(Enum):
    DOWHY = 'dowhy'
    BCAUSE = 'bcause'
    AUTOBOUNDS = 'autobounds'
    LCN = 'lcn'
