import mipx


if __name__ == '__main__':
    model = mipx.Model()
    x = model.addVars(2, vtype=mipx.BINARY, name="x")
    z = model.addVar(vtype=mipx.BINARY, name="z")
    model.addGenConstrOr(z, [x[0], x[1]])
    model.addConstr(x[0]+x[1] == 1)

    y1 = model.addVar(vtype=mipx.INTEGER, name="y")
    y2 = model.addVar(vtype=mipx.INTEGER, name="y")
    model.addConstr(y1-y2 == -4)
    z1 = model.addVar(vtype=mipx.INTEGER, name="z")
    s1 = model.addVar(vtype=mipx.INTEGER, name="s1")
    e1 = model.addVar(vtype=mipx.INTEGER, name="e1")
    s2 = model.addVar(vtype=mipx.INTEGER, name="s2")
    e2 = model.addVar(vtype=mipx.INTEGER, name="e2")
    ivar = model.newIntervalVar(s1, 10, e1, name="interval")
    ivar2 = model.newIntervalVar(s2, 10, e2, name="interval2")
    model.addNoOverlap([ivar, ivar2], M=100)

    model.addGenConstrAbs(z1, y1-y2, M=10000)
    status = model.optimize()
    if status == mipx.OptimizationStatus.OPTIMAL:
        print(f"Optimal value: {model.ObjVal}")
        print(f"z = {z.X}")
        print(z1.X)
        mipx.debugVar(s1)
        mipx.debugVar(e1)
        mipx.debugVar(s2)
        mipx.debugVar(e2)
