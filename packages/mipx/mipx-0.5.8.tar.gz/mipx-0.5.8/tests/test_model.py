import mipx


def test_model():
    # 创建模型
    # 支持 "SCIP", "CBC", "SAT", "CLP", "CPLEX","GUROBI","CP",....
    model = mipx.Model(solver_id="SAT", name="test_model")
    #! 参数配置
    model.Params.TimeLimit = 1000  # 设置时间限制
    model.Params.MIPGap = 0.01  # 设置MIPGap
    model.Params.EnableOutput = False  # 开启输出
    model.Params.Precision = 1e-6  # 设置精度
    # cpmodel = mipx.CpModel(solver_id="CP", name="test_cpmodel")
    #  添加变量
    # *********************************
    #! 单个变量
    x1 = model.addVar(name="x")  # 单个变量
    # CONTINUOUS（连续）,BINARY(0-1变量),BINARY（整数变量）
    x2 = model.addVar(lb=0, ub=10, vtype=mipx.BINARY, name="x1")
    #! 多维变量
    x3 = model.addVars(2, vtype=mipx.INTEGER, name="x2")  # x3[0],x3[1]
    x4 = model.addVars(2, 3, lb=1, ub=3, name="x4")  # 创建了2行3列的变量
    x5 = model.addVars([1, 2, 3], 3)  # 创建了3h行3列的变量, x5[1,0] x5[1,1] x5[1,2]...
    x6 = model.addVars(2, 2, 3)  # 三维变量
    #! 灵活创建变量
    x = mipx.tupledict({i: model.addVar() for i in range(10)})
    x = mipx.tupledict()  # 也可以使用 x = {}创建,但最好使用tupledict创建变量,
    for i in range(10):
        for j in range(10):
            x[i, j] = model.addVar()
    # *********************************
    # *********************************
    # 添加约束
    #! 单个约束
    model.addConstr(x1+x2 == 1, name="c1")
    # 结合多维变量快速求和
    model.addConstr(x6.quicksum(1, "*", "*") == 1, name="c2")
    # 结合多维变量实现变量与权重的乘积求和:x3[0]*w[0] + x3[1]*w[1]
    model.addConstr(x3.quickprod({0: 1, 1: 2}, "*") >= 2)
    model.addConstr(model.sum([x4[i, j]
                    for i in range(2) for j in range(3)]) >= 0)
    #! 多约束
    model.addConstrs([x1+x2 == 1, x1+x2 >= 1, x1+x2 <= 1], name="c3")
    model.addConstrs(x3.quicksum(i, "*") <= 3 for i in range(2))
    #! 其他约束
    y = model.addVars(3, vtype=mipx.BINARY, name="y")
    model.addGenConstrAnd(y[0], [y[1], y[2]])  # and 运算 y[0] = min(y[1],y[2])
    model.addGenConstrOr(y[0], [y[1], y[2]])  # or 运算 y[0] = max(y[1],y[2])
    model.addGenConstrXOr(y[0], [y[1], y[2]])  # 异或运算
    #! 绝对值约束
    b = model.addVar(ub=10, name="b")
    model.addGenConstrAbs(b, x[3, 2]-x[2, 1]+x[1, 0], M=100)  # 不用目标函数辅助
    #! 乘积
    # b = x1*x2,其中x至少有一个0/1变量
    model.addConstrMultiply(b, (x1, x2))
    #! 条件约束
    z = model.addVar(vtype=mipx.BINARY, name="z")
    model.addGenConstrIndicator(z, False, y[0]+y[1], mipx.EQUAL, 1, M=100)
    # model.addIndicator(z, False, y[0]+y[1] == 1) # 待实现
    #! 约束满足的次数
    model.addConstrOr([x[0, 1]+x[1, 4] == 1, x[0, 3]-x[1, 2]
                       <= 1], ok_num=1, cmpType=mipx.EQUAL)
    #! 范围约束
    model.addRange(x[1, 2]+x[1, 3], 0, 10)

    #! 非重叠约束
    s1 = model.addVar(vtype=mipx.INTEGER, name="s1")
    e1 = model.addVar(vtype=mipx.INTEGER, name="e1")
    s2 = model.addVar(vtype=mipx.INTEGER, name="s2")
    e2 = model.addVar(vtype=mipx.INTEGER, name="e2")
    ivar = model.newIntervalVar(s1, 10, e1, name="interval")
    ivar2 = model.newIntervalVar(s2, 5, e2, name="interval2")
    model.addNoOverlap([ivar, ivar2], M=100)
    # *********************************
    # *********************************
    #! 其他辅助方法
    model.addKpi(x1+x2, "KPI1")
    model.addKpi(x1-x2, "KPI2")
    model.statistics()
    model.setNumThreads(2)  # 设置线程数
    model.setHint({x1: 1, x2: 0})  # 为变量设置初始值
    #! 设置优化目标
    #! 设置单目标
    # model.setObjective(x1+x2)
    #! 设置多目标 (与单目标二选一)
    model.setObjectiveN(x1+x2, index=0, weight=1, name="obj1")
    model.setObjectiveN(x1-x2, index=1, weight=1, name="obj2")
    model.setObjectiveN(x.quicksum(), index=2, weight=1, name="obj3")
    status = model.optimize(mipx.MINIMIZE)  # 优化 ,默认最小化
    # model.write("tst_model.mps")  # 支持后缀 .lp .mps
    if status == mipx.OptimizationStatus.OPTIMAL:
        print("Optimal solution found.")
        print(f"耗时:{model.WallTime}ms")
        print(f"目标值:{model.ObjVal}")
        mipx.debugVar(y, no_zero=False)
        model.reportMultiObjValue()  # 输出多目标值
        # 输出kpi
        model.reportKpis()
        print("Kpi1:", model.kpiValueByName("KPI1"))  # 输出KPI1的值
        # 对应变量
        print("x:", x1.X)
        # 灵活的变量取值
        print("valueExpression:", model.valueExpression(x1+x[1, 2]))


def test_cpmodel():
    model = mipx.CpModel(name="test_cpmodel")
    #! 额外约束
    x = model.addVars(10, name='x')
    y = model.addVar(name='y')
    model.addGenConstrMin(y, [x[1], x[2], x[0]])  # y = min(x[1],x[2],x[0])
    model.addGenConstrMax(y, [x[3], x[4], x[5]])
    model.addGenConstrMultiplication(y, [x[4], x[6]])  # y = x[4]*x[6]
    index = model.addVar(ub=9, vtype=mipx.INTEGER, name='index_var')
    target = model.addVar(vtype=mipx.INTEGER, name='target_var')
    variables = model.addVars(
        10, lb=4, ub=7, vtype=mipx.INTEGER, name='variables')
    model.addElement(
        index=index, variables=variables.quickselect(), target=target)  # variables[index] = target
    m = model.addVar(lb=1, vtype=mipx.BINARY, name='m')
    n = model.addVar(vtype=mipx.BINARY, name='n')
    model.addImplication(m, n)  # 若m为真，则n一定为真。
    # ...
    model.addConstr(y >= 1)
    status = model.optimize()
    if status == mipx.OptimizationStatus.OPTIMAL:
        print("Optimal solution found.")
        print(f"目标值:{model.ObjVal}")
        mipx.debugVar(x, no_zero=False)
        mipx.debugVar(y, no_zero=False)
        mipx.debugVar(index, no_zero=False)
        mipx.debugVar(target, no_zero=False)
        mipx.debugVar(m, no_zero=False)
        mipx.debugVar(n, no_zero=False)


if __name__ == '__main__':
    # test_model()
    test_cpmodel()
