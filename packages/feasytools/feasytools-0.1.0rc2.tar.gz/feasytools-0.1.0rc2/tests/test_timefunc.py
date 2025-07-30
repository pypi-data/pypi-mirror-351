from feasytools import *

def test_timefunc():
    print("TimeFunc test:")
    f1 = ConstFunc(1)
    f2 = TimeImplictFunc(lambda: 1+2+3)
    f3 = ComFunc(lambda t: t)
    f4 = ManualFunc(1)
    f4.setManual(2)
    assert f1(0) == 1
    assert f2(0) == 6
    assert f3(0) == 0
    assert f4(0) == 2
    f5 = quicksum([f1,f2,f3,f4])
    print(f5)
    f6 = quickmul([f1,f2,f3,f4])
    print(f6)
    f7 = f5 + 1
    print(f7)
    f8 = f6 * 2
    print(f8)
    f9 = f5 + f6
    print(f9)
    f10 = f5 * f6
    print(f10)