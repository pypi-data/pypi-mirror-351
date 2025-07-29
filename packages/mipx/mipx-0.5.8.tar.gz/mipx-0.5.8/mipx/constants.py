# -*- coding: utf-8 -*-
# @Time    : 2023/3/31 22:21
# @Author  : luyi
from enum import Enum
from typing import Literal, Optional


P1, P2, P3, P4, P5, P6, P7, P8, P9 = (
    1,
    10,
    100,
    1000,
    10000,
    100000,
    1000000,
    10000000,
    100000000,
)


class Vtype(Enum):
    BINARY = "B"
    CONTINUOUS = "C"
    INTEGER = "I"


class ObjType(Enum):
    MINIMIZE = "MIN"
    MAXIMIZE = "MAX"


# optimization status
class OptimizationStatus(Enum):
    """Status of the optimization"""

    ERROR = -1
    """Solver returned an error"""

    OPTIMAL = 0
    """Optimal solution was computed"""

    INFEASIBLE = 1
    """The model is proven infeasible"""

    UNBOUNDED = 2
    """One or more variables that appear in the objective function are not
    included in binding constraints and the optimal objective value is
    infinity."""

    FEASIBLE = 3
    """An integer feasible solution was found during the search but the search
    was interrupted before concluding if this is the optimal solution or
    not."""

    INT_INFEASIBLE = 4
    """A feasible solution exist for the relaxed linear program but not for the
    problem with existing integer variables"""

    NO_SOLUTION_FOUND = 5
    """A truncated search was executed and no integer feasible solution was
    found"""

    LOADED = 6
    """The problem was loaded but no optimization was performed"""

    CUTOFF = 7
    """No feasible solution exists for the current cutoff"""

    OTHER = 10000


class CmpType(Enum):
    LESS_EQUAL = 0
    EQUAL = 1
    GREATER_EQUAL = 2


class Params:
    def __init__(self):
        self.TimeLimit: Optional[int] = None  # 单位秒
        self.MIPGap: Optional[float] = None  # 表示多少的gap,0.10则表示10
        self.EnableOutput = False
        self.Precision: Optional[float] = None  # 精度控制
        self.CpoptimizerPath: Optional[str] = None  # Cplex约束求解器路径
