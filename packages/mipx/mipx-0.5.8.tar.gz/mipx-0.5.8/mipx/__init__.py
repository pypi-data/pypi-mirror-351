# -*- coding: utf-8 -*-
# @Time    : 2023/3/31 22:18
# @Author  : luyi
from .constants import *
from .lineExpr import LineExpr
from .model import Model
from .cpmodel import CpModel
from .tupledict import tupledict, multidict
from .tuplelist import tuplelist
from .utilx import name_str
from .func import debugVar
from .variable import Var, IntervalVar
from ._version import __version__

BINARY = Vtype.BINARY
CONTINUOUS = Vtype.CONTINUOUS
INTEGER = Vtype.INTEGER
MINIMIZE, MAXIMIZE = ObjType
LESS_EQUAL, EQUAL, GREATER_EQUAL = CmpType
name = "mipx"
