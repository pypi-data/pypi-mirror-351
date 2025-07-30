from typing import Final

from dao_treasury import IgnoreSortRule, ignore
from dao_treasury.sorting.factory import SortRuleFactory


swaps: Final[SortRuleFactory[IgnoreSortRule]] = ignore("Swaps")


from .aave import *
from .compound import *
from .uniswap import *
