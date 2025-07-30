from typing import Final

from dao_treasury import IgnoreSortRule, ignore
from dao_treasury.sorting.factory import SortRuleFactory


swaps: Final[SortRuleFactory[IgnoreSortRule]] = ignore("Swaps")


from yearn_treasury.rules.ignore.swaps.aave import *
from yearn_treasury.rules.ignore.swaps.compound import *
from yearn_treasury.rules.ignore.swaps.uniswap import *
