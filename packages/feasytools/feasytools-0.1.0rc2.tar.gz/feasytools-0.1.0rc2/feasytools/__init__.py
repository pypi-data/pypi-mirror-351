from .tfunc import FloatLike, quicksum, quickmul, calcFunc, makeFunc
from .tfunc import TimeFunc, OverrideFunc, ConstFunc, TimeImplictFunc, ComFunc, ManualFunc, SegFunc
from .tfunc import PlusFunc, QuickSumFunc, MinusFunc, MulFunc, QuickMulFunc, TrueDivFunc, FloorDivFunc
from .argchk import ArgChecker, KeyNotSpecifiedError, ArgumentWithoutKeyError
from .table import ReadOnlyTable, ArrayTable, Table, DTypeEnum
from .pq import Heap, PQueue, BufferedPQ
from .rangelist import RangeList
from .geo import Point, Seg, KDTree, EdgeFinder
from .pdf import (
    PDModel, PDFunc, PDUniform, PDNormal, PDTriangular, PDExponential, 
    PDLogNormal, PDGamma, PDWeibull, PDLogLogistic, PDDiscrete, CDDiscrete, 
    GetPDFuncFromXMLNode, CreatePDFunc, CreatePDDiscretesFromCSVbyRow
)
from .perf import FEasyTimer

def time2str(tspan:float):
    tspan = round(tspan)
    s = tspan % 60
    m = tspan // 60 % 60
    h = tspan // 3600
    return f"{h:02}:{m:02}:{s:02}"