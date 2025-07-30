'''
This is a moudle for python unit calculation
Use this moudle,plese write:
`UnitNum()` or other class in this moudle.
Unit has calculate mode,it can use `+` `-` `*` `/`
It has operter too.
'''

from .units import *
from decimal import Decimal as long
from fractions import Fraction as fraction
from . import shapes

__all__=[
    "shapes","fraction","long",
    "Unit","Line","Area","Volume","Capacity","Duration","Version","datetime","operators"
]