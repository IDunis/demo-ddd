from enum import Enum


class OrderValue(str, Enum):
    Limit = 'limit'
    Market = 'market'


class OrderSide(Enum):
    Buy = 0
    Sell = 1


class OrderStatus(Enum):
    Created = 1
    Pending = 2
    PartiallyFilled = 3
    Filled = 4
    Canceled = 5
    Rejected = 6
    Expired = 7
    Error = 8
    BarrierTouched = 9
    StopTriggered = 10
    ForeignFilled = 11
    Unknown = 999


class OrderMarginSideEffect(Enum):
    NoSideEffect = 1
    Borrow = 2
    Repay = 3
    AutoDetermine = 4