# -*- coding: utf-8 -*-
# @Time    : 2023/4/12 9:12
# @Author  : luyi
"""
约束规划
"""

from typing import Optional, Union, List, Dict, Tuple

from docplex.cp.model import true
from ortools.sat.python import cp_model
from ortools.util.python.sorted_interval_list import Domain

from .constants import Vtype, ObjType, OptimizationStatus, CmpType
from .interface_ import IVar, ICpModel
from .tupledict import tupledict
from .utilx import (
    is_list_or_tuple,
    get_combinations,
    name_str,
    is_generator,
    check_bool_var,
    is_bool_var,
)
from .variable import CpVar

INFINITY = cp_model.INT32_MAX

Real = Union[float, int]


class CpModelSolver(ICpModel):

    def __init__(self, name=""):
        super().__init__("CP")
        self.name = name
        self.__model = cp_model.CpModel()
        self.__solver: cp_model.CpSolver = cp_model.CpSolver()
        self.__line_expr_object: Optional[cp_model.LinearExpr] = None
        self.__all_vars = []
        self.__all_constr = []
        self._flag_objective_n = False
        self._flag_objective = False

    @property
    def Infinity(self) -> int:
        return INFINITY

    @staticmethod
    def Sum(expr_array):
        return cp_model.LinearExpr.Sum(expr_array)

    def setHint(self, start: Dict[IVar, Real]):
        for var, num in start.items():
            self.__model.AddHint(var, num)  # type: ignore

    def setTimeLimit(self, time_limit_seconds: int):
        self.__solver.parameters.max_time_in_seconds = int(time_limit_seconds)

    def wall_time(self) -> int:
        return int(self.__solver.WallTime()) * 1000

    def iterations(self) -> Real:
        return 0

    def nodes(self) -> Real:
        return self.__solver.NumBranches()

    def addVar(
        self,
        lb: int = 0,
        ub: int = INFINITY,
        vtype: Vtype = Vtype.BINARY,
        name: str = "",
    ) -> IVar:
        """
            Add a decision variable to a model.
        :param lb: Lower bound for new variable.
        :param ub: Upper bound for new variable.
        :param vtype: variable type for new variable(Vtype.CONTINUOUS, Vtype.BINARY, Vtype.INTEGER).
        :param name: Name for new variable.
        :return: variable.
        """
        tempModel = self.__model._CpModel__model  # type: ignore
        var1: Optional[CpVar] = None
        if vtype == Vtype.CONTINUOUS or vtype == Vtype.INTEGER:
            var1 = CpVar(tempModel, Domain(lb, ub), False, name, self)
        elif vtype == Vtype.BINARY:
            var1 = CpVar(tempModel, Domain(lb, ub), True, name, self)
        self.__all_vars.append(var1)
        return var1

    def addVars(
        self,
        *indices,
        lb: int = 0,
        ub: int = INFINITY,
        vtype: Vtype = Vtype.INTEGER,
        name: str = "",
    ) -> tupledict:
        li = []
        for ind in indices:
            if isinstance(ind, int):
                ind = [i for i in range(ind)]
            elif is_list_or_tuple(ind):
                pass
            elif isinstance(ind, str):
                ind = [ind]
            else:
                raise ValueError("error input")
            li.append(ind)
        all_keys_tuple = get_combinations(li)
        tu_dict = tupledict(
            [
                [key, self.addVar(lb, ub, vtype, name_str(name, key))]
                for key in all_keys_tuple
            ]
        )
        return tu_dict

    def getVars(self) -> List[IVar]:
        return self.__all_vars

    def getVar(self, i) -> IVar:
        return self.__all_vars[i]

    def addConstr(self, lin_expr, name=""):
        self.__all_constr.append(lin_expr)
        self.__model.Add(lin_expr)

    def addConstrs(self, lin_exprs, name=""):
        # 检查下是否可以迭代。
        if not is_list_or_tuple(lin_exprs) and not is_generator(lin_exprs):
            raise RuntimeError("constraint conditions are not a set or list")
        for i, lin_expr in enumerate(lin_exprs):
            self.addConstr(lin_expr)

    def setObjective(self, expr):
        self._flag_objective = True
        if self._flag_objective_n:
            raise RuntimeError(
                "setObjective and setObjectiveN can only be used for one of them"
            )
        self.__model.Minimize(expr)
        self.__line_expr_object = expr

    def setObjectiveN(
        self, expr, index: int, priority: int = 0, weight: float = 1, name: str = ""
    ):
        """

        :param expr:
        :param index:
        :param priority:
        :param weight:
        :param name:
        :return:
        """
        self._flag_objective_n = True
        if self._flag_objective:
            raise RuntimeError(
                "setObjective and setObjectiveN can only be used for one of them"
            )
        if self.__line_expr_object is None:
            self.__line_expr_object = expr * weight
            return
        self.__line_expr_object = self.__line_expr_object + expr * weight

    def addGenConstrAnd(self, resvar, varList: List[IVar], name=""):
        """
        和 addGenConstrAnd(y, [x1,x2])
        :param resvar:
        :param varList:
        :param name:
        :return:
        """
        check_bool_var(resvar, varList)
        for var in varList:
            self.addConstr(resvar <= var)
        self.addConstr(resvar >= self.Sum(varList) -
                       len(varList) + 1)  # type: ignore

    def addGenConstrOr(self, resvar: IVar, varList: List[IVar], name=""):
        check_bool_var(resvar, varList)
        for var in varList:
            self.addConstr(resvar >= var)
        self.addConstr(resvar <= self.Sum(varList))

    def addGenConstrMin(self, target: IVar, varList: List[IVar]):
        self.__model.add_min_equality(target, varList)  # type: ignore

    def addGenConstrMax(self, target: IVar, varList: List[IVar]):
        """
        最小值约束
        """
        self.__model.add_max_equality(target, varList)  # type: ignore

    def addGenConstrDivision(self, target, num, denom):
        """Adds `target == num // denom` (integer division rounded towards 0)."""
        self.__model.add_division_equality(target, num, denom)

    def addGenConstrModulo(self, target, num, denom):
        """Adds `target = expr % mod`."""
        self.__model.add_modulo_equality(target, num, denom)

    def addGenConstrMultiplication(
        self,
        target,
        *expressions,
    ):
        """Adds `target == expressions[0] * .. * expressions[n]`."""
        self.__model.add_multiplication_equality(target, *expressions)

    def addGenConstrXOr(self, resvar: IVar, varList: List[IVar], name=""):

        if len(varList) != 2:
            raise ValueError("length of vars must be 2")
        check_bool_var(resvar, varList)
        self.addConstr(resvar >= varList[0] - varList[1])
        self.addConstr(resvar >= varList[1] - varList[0])
        self.addConstr(resvar <= varList[0] + varList[1])
        self.addConstr(resvar <= 2 - varList[0] - varList[1])

    def addGenConstrPWL(
        self,
        var_y: IVar,
        var_x: IVar,
        x_range: List[int],
        y_value: List[int],
        name="",
    ):
        raise NotImplementedError()

    def addGenConstrIndicator(
        self,
        binvar: IVar,
        binval: bool,
        lhs: IVar,
        sense: CmpType,
        rhs: int,
        M,
        name: str = "",
    ):
        # var = binvar if binval is True else binvar.Not()
        # if sense == CmpType.GREATER_EQUAL:  # 大于等于
        #     self.__model.Add(lhs - rhs >= 0).OnlyEnforceIf(var)
        # elif sense == CmpType.EQUAL:
        #     self.__model.Add(lhs - rhs == 0).OnlyEnforceIf(var)
        # else:
        #     self.__model.Add(lhs - rhs <= 0).OnlyEnforceIf(var)
        #  根据不完全的测试，下面的代码优于上面的代码
        if M is None:
            M = abs(rhs) + 100  # TODO:待优化
        if binval is True:
            z = 1 - binvar
        else:
            z = binvar
        if sense == CmpType.GREATER_EQUAL:
            self.addConstr(lhs + M * z >= rhs)
        elif sense == CmpType.EQUAL:
            self.addConstr(lhs + M * z >= rhs)
            self.addConstr(lhs - M * z <= rhs)
        else:
            self.addConstr(lhs - M * z <= rhs)

    def addIndicator(self, binvar: IVar, binval: bool, expr, name: str = ""):
        raise RuntimeError("not implemented")

    def addGenConstrAbs(self, resvar, var_abs: IVar):
        self.__model.AddAbsEquality(resvar, var_abs)  # type: ignore

    def addConstrMultiply(self, z: IVar, l: Tuple[IVar, IVar], name=""):
        """x * y = z"""
        super().addConstrMultiply(z, l)
        x = l[0]
        y = l[1]
        if not is_bool_var(x) and not is_bool_var(y):
            raise RuntimeError("At least one binary variable is required.")
        if is_bool_var(y):
            x, y = y, x
        M = y.Ub
        self.addConstr(z <= y)
        self.addConstr(z <= x * M)
        self.addConstr(z >= y + (x - 1) * M)

    def addRange(
        self, expr, min_value: Union[float, int], max_value: Union[float, int], name=""
    ):
        self.__model.AddLinearConstraint(
            expr, min_value, max_value)  # type: ignore

    def addConstrOr(
        self,
        constrs: List[cp_model.BoundedLinearExpression],
        ok_num: int = 1,
        cmpType: CmpType = CmpType.EQUAL,
        name: str = "",
        M=None,
    ):
        """
        约束的满足情况

        :param constr: 所有的约束
        :param ok_num: 需要满足的个数，具体则根据cmpType
        :param cmpType: CmpType.LESS_EQUAL CmpType.EQUAL,CmpType.GREATER_EQUAL
        :param name: 名称
        :return:
        """
        constr_num = len(constrs)
        x = []
        for i in range(constr_num):
            x.append(self.addVar(vtype=Vtype.BINARY))
            constr = constrs[i]
            try:
                lb, ub = constr.Bounds()  # type: ignore
                expr = constr.Expression()  # type: ignore
            except:
                lb, ub = constr.bounds()
                expr = constr.expression()
            tempM = 100000000
            if M is not None:
                tempM = M
            if lb > -INFINITY:  # 若大于
                self.addConstr(expr + tempM * (1 - x[i]) >= lb)
            if ub < INFINITY:

                self.addConstr(expr - tempM * (1 - x[i]) <= ub)
        if cmpType == CmpType.EQUAL:
            self.addConstr(self.Sum(x) == ok_num)
        elif cmpType == CmpType.GREATER_EQUAL:
            self.addConstr(self.Sum(x) >= ok_num)  # type: ignore
        elif cmpType == CmpType.LESS_EQUAL:
            self.addConstr(self.Sum(x) <= ok_num)  # type: ignore
        else:
            raise Exception("error value of cmpType")

    def numVars(self, vtype: Optional[Vtype] = None) -> int:
        if vtype is Vtype.CONTINUOUS:
            return 0
        return len(self.__all_vars)

    def numConstraints(self) -> int:
        return len(self.__all_constr)

    def write(self, filename: str, obfuscated=False):
        self.__model.ExportToFile(filename)

    def read(self, path: str):
        raise RuntimeError("not implemented")

    @property
    def ObjVal(self) -> Real:
        return self.__solver.ObjectiveValue()

    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        solver = self.__solver
        self._set_objective(obj_type)
        self._set_params()
        status = solver.Solve(self.__model)
        if status == cp_model.OPTIMAL:
            result = OptimizationStatus.OPTIMAL
        elif status == cp_model.INFEASIBLE:
            result = OptimizationStatus.INFEASIBLE
        elif status == cp_model.UNKNOWN:
            result = OptimizationStatus.UNBOUNDED
        elif status == cp_model.FEASIBLE:
            result = OptimizationStatus.FEASIBLE
        else:
            result = OptimizationStatus.ERROR
        return result

    def clear(self):
        self.__line_expr_object = None
        self.__all_vars.clear()
        self.__all_constr.clear()
        self._flag_objective = False
        self._flag_objective_n = False
        self.__model.ClearObjective()
        self.__model.ClearHints()
        self.__model.ClearAssumptions()

    def close(self):
        self.clear()
        self.__solver = None  # type: ignore

    def _set_objective(self, obj_type: ObjType):
        if self.__line_expr_object is not None:
            if obj_type == ObjType.MINIMIZE:
                self.__model.Minimize(self.__line_expr_object)
            else:
                self.__model.Maximize(self.__line_expr_object)

    def _set_params(self):
        if self.Params.TimeLimit:
            self.setTimeLimit(self.Params.TimeLimit)
        if self.Params.EnableOutput:
            self.__solver.parameters.log_search_progress = True
        if self.Params.MIPGap:
            self.__solver.parameters.absolute_gap_limit = self.Params.MIPGap

    # 独有。其他方法待添加

    def addNoOverlap(self, interval_vars, M):
        """
        相邻不重复。

        :param interval_vars:
        :return:
        """
        self.__model.AddNoOverlap(interval_vars)

    def newIntervalVar(self, start, size, end, name=""):
        if type(start) == type(0.1):
            start = int(start)
        if type(end) == type(0.1):
            end = int(end)
        if type(size) == type(0.1):
            size = int(size)
        return self.__model.NewIntervalVar(start, size, end, name)

    def valueExpression(self, expression):
        return self.__solver.Value(expression)

    def setNumThreads(self, num_theads: int):
        self.__solver.parameters.num_workers = num_theads

    def addElement(self, index, variables, target):
        self.__model.add_element(index, variables, target)

    def addCircuit(self, arcs):
        self.__model.add_circuit(arcs)

    def addAllowedAssignments(self, variables, tuples_list):
        self.__model.add_allowed_assignments(variables, tuples_list)

    def addForbiddenAssignments(self, variables, tuples_list):
        self.__model.add_forbidden_assignments(variables, tuples_list)

    def addInverse(self, variables, inverse_variables):
        self.__model.add_inverse(variables, inverse_variables)

    def addMapDomain(self, var, bool_var_array, offset):
        self.__model.add_map_domain(var, bool_var_array, offset)

    def addImplication(self, a, b):
        self.__model.add_implication(a, b)

    def addBoolTrueOr(self, literals):
        self.__model.add_bool_or(literals)

    def addAtLeastOneIsTrue(self, literals):
        self.__model.add_at_least_one(literals)

    def addAtMostOneIsTrue(self, literals):
        self.__model.add_at_most_one(literals)

    def addExactlyNumIsTrue(self, literals, num: int = 1):
        if num == 1:
            self.__model.AddExactlyOne(literals)
        else:
            self.addConstr(self.Sum(literals) == num)

    def addBoolTrueAnd(self, literals):
        self.__model.add_bool_and(literals)
