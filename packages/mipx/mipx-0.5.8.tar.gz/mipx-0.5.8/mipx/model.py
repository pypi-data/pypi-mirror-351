from math import inf
from typing import Dict, Generator, List, Literal, Optional, Tuple, Union
from ortools.sat.python import cp_model

from .func import get_update_lub
from .utilx import pre_condition
from .interface_ import ITupledict, IVar
from .commonsolver import CommonModelSolver
from .constants import CmpType, ObjType, OptimizationStatus, Params, Vtype

INFINITY = float("inf")
INFINITY_CP = cp_model.INT32_MAX
Real = Union[float, int]


class Model:
    """模型接口"""

    def __init__(
        self,
        solver_id: Literal[
            "SCIP", "CBC", "SAT", "CLP", "CPLEX", "GLOP", "BOP", "GLPK"
        ] = "SCIP",
        name="",
    ):
        super().__init__()
        self.solver_id = solver_id
        if solver_id == "CPLEX":
            try:
                from .cplexmpsolver import CplexMpSolver

                self.__model = CplexMpSolver(name=name)
                if not self.__model.has_cplex_env:
                    raise Exception("No CPLEX environment found")
            except ImportError:
                raise Exception("未找到cplex 库，请安装")
            except:
                raise Exception("未知错误")
        else:
            self.__model = CommonModelSolver(solver_id=solver_id, name=name)
        self._is_cp = solver_id in ["CP", "CPLEX_CP"]
        self._allkpis = {}
        self._multi_object_expr = []

    @property
    def Params(self) -> Params:
        return self.__model.Params

    @property
    def name(self) -> str:
        return self.__model.name

    @property
    def Infinity(self) -> float:
        return self.__model.Infinity

    def sum(self, expr_array):
        return self.Sum(expr_array)

    def Sum(self, expr_array):
        return self.__model.Sum(expr_array)

    def setHint(self, start: Dict[IVar, Real]):
        self.__model.setHint(start)  # type: ignore

    def setTimeLimit(self, time_limit_seconds: int):
        """
        设置程序最大运行时间
        :param time_limit_seconds: 秒
        """
        self.__model.setTimeLimit(time_limit_seconds)

    def wall_time(self) -> float:
        """
        求解所花费的时间
        :return: 求解所花费的时间，单位毫秒
        """
        return self.__model.wall_time()

    @property
    def WallTime(self) -> float:
        return self.wall_time()

    def iterations(self):
        """

        :return: 算法迭代的次数
        """
        return self.__model.iterations()

    def nodes(self) -> Real:
        """

        :return: 节点数
        """
        return self.__model.nodes()

    def addVar(
        self, lb=0, ub=None, vtype: Vtype = Vtype.CONTINUOUS, name: str = ""
    ) -> IVar:
        """
        创建变量
        :param lb: 变量下界
        :param ub: 变量上界
        :param vtype: 变量类型： Vtype.CONTINUOUS（连续）,Vtype.BINARY(0-1变量), Vtype.BINARY（整数变量）
        :param name:变量名
        :return:变量实体
        """
        lb, ub = get_update_lub(self.solver_id, self._is_cp, lb, ub, vtype)
        if vtype == Vtype.INTEGER:
            lb = int(lb + 0.5)
            if ub != inf:
                ub = int(ub)
        return self.__model.addVar(lb=lb, ub=ub, vtype=vtype, name=name)

    def addVars(
        self,
        *indices,
        lb: Real = 0,
        ub=None,
        vtype: Vtype = Vtype.CONTINUOUS,
        name: str = "",
    ) -> ITupledict:
        """
        创建多维变量
        :param indices:多维的参数，如addVars(1,2),addVars(mList,nList),addVars([1,2,3],[3,4,5])等。
        :param lb:变量下界
        :param ub:变量上界
        :param vtype:变量类型： Vtype.CONTINUOUS（连续）,Vtype.BINARY(0-1变量), Vtype.BINARY（整数变量）
        :param name:变量名
        :return:tupledict类型
        """
        pre_condition(len(indices) > 0, "addVars中多维参数缺失")
        lb, ub = get_update_lub(self.solver_id, self._is_cp, lb, ub, vtype)
        return self.__model.addVars(*indices, lb=lb, ub=ub, vtype=vtype, name=name)

    def getVars(self) -> List[IVar]:
        """
        获取所有的变量对象
        :return:
        """
        return self.__model.getVars()

    def getVar(self, i) -> IVar:
        """
        获取第i个变量
        :param i:
        :return:
        """
        return self.__model.getVar(i)

    def addConstr(self, lin_expr, name=""):
        """
        向模型添加约束条件，
        :param lin_expr:线性约束表达式
        :param name: 约束名称
        :return:
        """
        return self.__model.addConstr(lin_expr, name=name)

    def addConstrs(self, lin_exprs: Union[List, Generator, Tuple], name=""):
        """
        向模型添加多个约束条件，
        :param lin_exprs: 线性约束表达式集合 可以为列表或者元组。
        :param name:名称
        :return:
        """
        return self.__model.addConstrs(lin_exprs, name=name)

    def setObjective(self, expr):
        """
        设置模型的单一目标
        :param expr: 目标表达式
        优化方向。ObjType.MINIMIZE（最小值），ObjType.MAXIMIZE(最大值)
        :return:
        """
        self.__model.setObjective(expr)

    def setObjectiveN(
        self, expr, index: int, priority: int = 0, weight: float = 1, name: str = ""
    ):
        """
        多目标优化，优化最小值
        :param expr: 表达式
        :param index: 目标函数对应的序号 (默认 0，1，2，…), 以 index=0 作为目标函数的值, 其余值需要另外设置参数
        :param priority: 分层序列法多目标决策优先级(整数值), 值越大优先级越高【未实现】
        :param weight: 线性加权多目标决策权重(在优先级相同时发挥作用)
        :param name: 名称
        :return:
        """
        self._multi_object_expr.append((expr, weight, name))
        self.__model.setObjectiveN(
            expr, index, priority=priority, weight=weight, name=name
        )

    def addGenConstrAnd(self, resvar, varList: List[IVar], name=""):
        """
        and 运算。
        addGenConstrAnd(y, [x1, x2]) 表示y = and(x1,x2)。 所有变量均为0-1变量
        即 x1 x2 都为1时,y = 1
        :param resvar:
        :param varList:
        :param name:
        :return:
        """
        self.__model.addGenConstrAnd(resvar, varList, name=name)

    def addGenConstrOr(self, resvar: IVar, varList: List[IVar], name=""):
        """
        或运算
        addGenConstrOr(y, [x1, x2]) 表示y = or(x1,x2)。 所有变量均为0-1变量
        即 x1,x2 至少有一个为1时,y = 1
        :param resvar:
        :param varList:
        :param name:
        :return:
        """
        self.__model.addGenConstrOr(resvar, varList, name=name)

    def addGenConstrXOr(self, resvar: IVar, varList: List[IVar], name=""):
        """
        异或运算
        addGenConstrXOr(y, [x1, x2])。 所有变量均为0-1变量
        x1 x2 y
        1  1  0
        1  0  1
        0  1  1
        0  0  0
        :param resvar:
        :param varList:
        :param name:
        :return:
        """
        self.__model.addGenConstrXOr(resvar, varList, name=name)

    def addGenConstrPWL(
        self,
        var_y: IVar,
        var_x: IVar,
        x_range: List[float],
        y_value: List[float],
        name="",
    ):
        """
        设置分段约束
        model.addGenConstrPWL(var, [1, 3, 5], [1, 2, 4])
        :param var_y: f(x)
        :param var_x:指定变量的目标函数是分段线性
        :param x:  定义分段线性变量的点的范围边界(非减序列)，要求x的范围大于0
        :param y:定义分段线性变量的范围所对应的目标函数的值
        :return:
        """
        self.__model.addGenConstrPWL(var_y, var_x, x_range, y_value, name=name)

    def addGenConstrIndicator(
        self,
        binvar: IVar,
        binval: bool,
        lhs: IVar,
        sense: CmpType,
        rhs,
        M,
        name: str = "",
    ):
        """
        若 binvar 为binval ,则 lhs 与 rhs 之间有sense 的关系
        若M不指定，则程序会给与默认。但仍推荐给出M。程序自动给出的可能会存在问题。
        :param binvar: 0-1变量
        :param binval: bool 常量
        :param lhs:  左侧变量
        :param sense: 等号，大于等于，小于等于
        :param rhs: 右侧常量
        :param M: 大M
        :return:
        """
        self.__model.addGenConstrIndicator(
            binvar, binval, lhs, sense, rhs, M=M, name=name
        )

    def addIndicator(self, binvar: IVar, binval: bool, expr, name: str = ""):
        self.__model.addIndicator(binvar, binval, expr, name)

    def addGenConstrAbs(self, resvar, var_abs: IVar, M, name=""):
        """
        绝对值 resvar = |var_abs|
        :param resvar:
        :param var_abs:
        :param name:
        :return:
        """
        self.__model.addGenConstrAbs(resvar, var_abs, name=name, M=M)

    def addConstrMultiply(self, z: IVar, l: Tuple[IVar, IVar], name=""):
        """
        满足 z = x * y
        其中 x 为0,1变量
        :param l:
        :param z: 变量
        :param name:
        :return:
        """
        self.__model.addConstrMultiply(z, l, name=name)

    def addRange(
        self, expr, min_value: Union[float, int], max_value: Union[float, int], name=""
    ):
        """
        添加范围约束
        :param expr: 表达式
        :param min_value: 最小值
        :param max_value: 最大值
        :param name:名称
        :return:
        """
        self.__model.addRange(expr, min_value, max_value, name=name)

    def addConstrOr(
        self,
        constrs: List,
        ok_num: int = 1,
        cmpType: CmpType = CmpType.EQUAL,
        name: str = "",
        M=None,
    ):
        """
        约束的满足情况,满足的次数
        :param constr: 所有的约束
        :param ok_num:  需要满足的个数，具体则根据cmpType
        :param cmpType: CmpType.LESS_EQUAL CmpType.EQUAL,CmpType.GREATER_EQUAL
        :param name: 名称
        :param M: M值，推荐指定M值。
        :return:
        """
        self.__model.addConstrOr(
            constrs, ok_num=ok_num, cmpType=cmpType, name=name, M=M
        )

    def addKpi(self, kpi_arg, name: str):
        if name in self._allkpis:
            raise Exception(f"KPI名称 {name} 重复")
        self._allkpis[name] = kpi_arg

    def reportKpis(self):
        """
        输出所有KPI
        :return:
        """
        print("===========all kpis=============")
        for name, kpi_arg in self._allkpis.items():
            value = self.valueExpression(kpi_arg)
            print(f"{name} = {value}")
        print("================================")

    def kpiByName(self, name: str):
        """根据名称获取KPI"""
        kpi = self._allkpis.get(name)
        if kpi is None:
            raise Exception(f"KPI名称 {name} 不存在")
        return kpi

    def kpiValueByName(self, name: str):
        """根据名称获取KPI的值"""
        kpi = self.kpiByName(name)
        return self.valueExpression(kpi)

    def removeKpi(self, name: str):
        """
        移除KPI
        :param name:
        :return:
        """
        if name not in self._allkpis:
            raise Exception(f"KPI名称 {name} 不存在")
        del self._allkpis[name]

    def clearKpis(self):
        """
        清除所有KPI
        :return:
        """
        self._allkpis.clear()

    @property
    def numOfKpis(self):
        return len(self._allkpis)

    def numVars(self, varType: Optional[Vtype] = None) -> int:
        """
        变量个数
        :return:
        """
        return self.__model.numVars(varType)

    def statistics(self):
        """
        统计模型信息
        :return:
        """
        print("statistics：\n========")
        print(f"numConstraints：{self.numConstraints()}")
        print(f"numVars：{self.numVars()}")
        print(
            f"numVars of int：{self.numVars(Vtype.INTEGER)+self.numVars(Vtype.BINARY)}"
        )
        print("========")

    def reportMultiObjValue(self):
        """
        展示多目标优化的目标值
        """
        print("========MultiObjValue===========")
        for expr, weight, name in self._multi_object_expr:
            value = self.valueExpression(expr)
            print(f"{name} : {round(value, 2)}")
        print("================================")

    def numConstraints(self) -> int:
        """
        约束个数
        :return:
        """
        return self.__model.numConstraints()

    def write(self, filename: str, obfuscated=False):
        """
        写入到文件
        :param filename:文件名，支持后缀 .lp .mps .proto(目前有问题)
        :param obfuscated: 是否混淆，默认不混淆
        :return:
        """
        self.__model.write(filename, obfuscated=obfuscated)

    def read(self, path: str):
        self.__model.read(path)

    @property
    def ObjVal(self) -> Real:
        """目标值"""
        return self.__model.ObjVal

    def optimize(self, obj_type: ObjType = ObjType.MINIMIZE) -> OptimizationStatus:
        """
        优化目标
        :param time_limit_milliseconds:最大运行时长
        :param obj_type:优化目标。ObjType.MINIMIZE（最小值），ObjType.MAXIMIZE(最大值)
        :param enable_output: 是否显示gap日志。
        :return:
        """
        return self.__model.optimize(obj_type=obj_type)

    def clear(self):
        self.clearKpis()
        self._multi_object_expr.clear()
        self.__model.clear()

    def close(self):
        self.__model.close()

    def valueExpression(self, expression):
        """
        计算表达式的值。
        :param expression:
        :return:
        """
        if isinstance(expression, (int, float)):
            return expression
        return self.__model.valueExpression(expression)

    def newIntervalVar(self, start, size, end, name=""):
        """
        创建变量： start+size=end

        Args:
            start (_type_): 开始
            size (_type_): 大小
            end (_type_): 结束
            name (str, optional): 名称. Defaults to "".
        """
        return self.__model.newIntervalVar(start, size, end, name=name)

    def addNoOverlap(self, interval_vars: List, M: int):
        """
        互相之间不重复

        Args:
            interval_vars (List): 间隔变量
        """
        self.__model.addNoOverlap(interval_vars, M)

    def setNumThreads(self, num_theads: int):
        """
        设置线程的个数

        Args:
            num_theads (int): 线程个数
        """
        self.__model.setNumThreads(num_theads)
