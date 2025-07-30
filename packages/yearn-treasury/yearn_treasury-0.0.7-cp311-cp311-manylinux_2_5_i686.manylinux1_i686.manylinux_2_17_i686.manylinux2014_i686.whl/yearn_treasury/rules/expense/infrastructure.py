from typing import Final

from dao_treasury import TreasuryTx, expense, ExpenseSortRule


infrastructure: Final = expense("Infrastructure")


# TODO: enable this syntax in dao-treasury
# ExpenseSortRule(
#    txgroup=infrastructure("Tenderly Subscription")
#    symbol="USDT"
#    to_address="0xF6060cE3fC3df2640F72E42441355f50F195D96a",
# )
# TODO: or maybe this one?
# ExpenseSortRule(
#    txgroup=infrastructure + "Tenderly Subscription"
#    symbol="USDT"
#    to_address="0xF6060cE3fC3df2640F72E42441355f50F195D96a",
# )


@infrastructure("Tenderly Subscription")
def is_tenderly(tx: TreasuryTx) -> bool:
    return tx.symbol == "USDT" and tx.to_address == "0xF6060cE3fC3df2640F72E42441355f50F195D96a"


@infrastructure("Wonderland Jobs")
def is_wonderland(tx: TreasuryTx) -> bool:
    return tx.symbol == "DAI" and tx.to_address == "0x8bA72884984f669aBBc9a5a7b441AD8E3D9a4fD3"
