import collections
import platform
from typing import List, Tuple
from itertools import combinations

import numpy as np
import mipx
from matplotlib import pyplot as plt

Line = collections.namedtuple('Point', 'x1 y1 x2 y2')


def draw(lines: List[Line]):
    if platform.system() == "Windows":
        plt.rcParams['font.sans-serif'] = ['SimHei']
    else:
        plt.rcParams['font.sans-serif'] = ['Heiti TC']  # 防止中文乱码
    plt.rcParams['axes.unicode_minus'] = False
    for line in lines:
        xs = [line.x1, line.x2]
        ys = [line.y1, line.y2]
        plt.plot(xs, ys, marker='o', markersize=5)
        plt.plot(xs, ys, linestyle='solid')
    plt.show()


# points = [(1, 3), (2, 4), (5, 2), (8, 12), (6, 4),
#           (3, 8), (4, 10), (4, 5), (5, 8), (8, 6), (1, 7)]


def generate_random_points(n_points, seed=None, x_range=(0, 100), y_range=(0, 100)):
    """
    生成随机的二维坐标点
    - n_points: 生成的点位数量
    - seed: 随机种子（可选，用于复现结果）
    - x_range: X坐标范围（默认0-100）
    - y_range: Y坐标范围（默认0-100）
    """
    if seed is not None:
        np.random.seed(seed)

    x = np.random.uniform(x_range[0], x_range[1], n_points)
    y = np.random.uniform(y_range[0], y_range[1], n_points)

    return list(zip(x, y))


# 示例：生成10个随机点（种子44保证可复现）
points = generate_random_points(
    n_points=13, seed=45,  x_range=(0, 10), y_range=(0, 15))


def calc_distance_matrix():
    # 旅行地坐标

    return {(i1, i2): (points[i1][0]-points[i2][0])**2 + (points[i1][1]-points[i2][1])**2 for i1 in range(len(points)) for i2 in range(len(points))}


def tsp():
    # 创建模型
    model = mipx.Model(solver_id="SCIP", name="TSP")
    model.Params.MIPGap = 0.01
    num = len(points)
    # model = mipx.CpModel(solver_id="CP", name="TSP")
    # 决策变量: x[i][j] 表示是否从 i 地点到 j 地点, 1 表示选择，0 表示不选择
    # x = model.addVars(len(points), len(points), vtype=mipx.BINARY, name="x")
    x = mipx.tupledict({(i1, i2): model.addVar(vtype=mipx.BINARY, name=mipx.name_str(
        'x', i1, i2)) for i1 in range(num) for i2 in range(num) if i1 != i2})
    # x = mipx.tupledict()
    # for i1 in range(num):
    #     for i2 in range(num):
    #         if i1 != i2:
    #             x[i1, i2] = model.addVar(vtype=mipx.BINARY, name=mipx.name_str(
    #                 'x', i1, i2))
    # 约束
    # 1. 每个城市只有一个入边
    # for i in range(len(points)):
    #     model.addConstr(x.quicksum(i, "*") == 1)
    model.addConstrs(x.quicksum(i, "*") == 1
                     for i in range(num))
    # 2. 每个城市只有一个出边
    for j in range(num):
        model.addConstr(x.quicksum("*", j) == 1)
        model.addKpi(x.quicksum("*", j), name=f"KPI_{j}")
    # 3. 防止生成子回路
    for n in range(2, num-1):
        coms = combinations(range(num), n)
        for com in coms:
            li = [x[i1, i2] for i1 in com for i2 in com if i1 != i2]
            model.addConstr(model.sum(li) <= n - 1)
    # 添加目标
    # 最小化总距离
    dist_matrix = calc_distance_matrix()
    model.setObjective(x.quickprod(dist_matrix, "*", "*"))
    model.statistics()
    status = model.optimize()
    if status == mipx.OptimizationStatus.OPTIMAL:
        print("Optimal solution found")
        # mipx.debugVar(x)
        lines = []
        model.reportKpis()
        for (i1, i2), x_var in x.items():
            if x_var.X == 1:
                p1 = points[i1]
                p2 = points[i2]
                lines.append(Line(p1[0], p1[1], p2[0], p2[1]))
        draw(lines)


if __name__ == '__main__':
    tsp()
