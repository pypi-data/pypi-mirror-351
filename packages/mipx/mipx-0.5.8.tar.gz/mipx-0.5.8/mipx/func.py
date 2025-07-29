# -*- coding: utf-8 -*-
# @Time    : 2023/4/28 23:54
# @Author  : luyi
from math import ceil, floor
from typing import Any

from .constants import Vtype
from .utilx import is_list_or_tuple
from .tupledict import tupledict

INFINITY_CP = 2**31 - 1
INFINITY = float("inf")


def get_update_lub(solver_id, is_cp, lb, ub: Any, vtype: Vtype):
    if is_cp and ub is None:
        ub = INFINITY_CP
    elif is_cp and ub:
        ...
    elif ub is None:
        ub = INFINITY
    if solver_id in ["SAT", "CBC"]:
        ub = INFINITY_CP if ub == INFINITY else ub
    if is_cp:
        if lb:
            lb = ceil(lb)
        if ub:
            ub = floor(ub)
    if vtype == Vtype.BINARY:
        if ub > 0 or ub is None:
            ub = 1
        if lb > 0:
            lb = 1
        if lb < 0 or lb is None:
            lb = 0
    ub = max(ub, 1)
    if lb > ub:
        raise Exception("0-1变量lb>=ub")
    return lb, ub


def abs_(*args):
    pass


def all_(*args):
    pass


def and_(*args):
    pass


def any_(*args):
    pass


def debugVar(vars, no_zero=True):
    """
    调试var的方法

    :param _type_ vars: 可以是变量的集合或者单个变量
    :param bool no_zero: 不输出<=0的值, defaults to True
    """
    is_list = False
    if type(vars) == type(tupledict()):
        vars = vars.values()
        is_list = True
    if is_list_or_tuple(vars):
        is_list = True
    if is_list:
        for var in vars:
            if no_zero:
                if var.X <= 0.01:
                    continue
            print(f"{var.VarName}:{var.X}")
    else:
        print(f"{vars.VarName}:{vars.X}")  # type:ignore
