# 生成测试
import unittest
import mipx


class TestUtils(unittest.TestCase):

    def test_debug_var(self):
        model = mipx.Model(solver_id="CBC")
        x = model.addVars(1, 3, name="x")
        y = model.addVar(name="y")
        status = model.optimize()
        if status == mipx.OptimizationStatus.OPTIMAL:
            mipx.debugVar(x.select("*", 2), False)
            mipx.debugVar(y, False)
            mipx.debugVar(x, False)
            mipx.debugVar([y], False)

    def test_tuple_list(self):
        a = mipx.tuplelist([1, 2, 3])
        print(a.quickselect(1))

    def test_cp_model(self):
        pass


if __name__ == "__main__":
    unittest.main()
