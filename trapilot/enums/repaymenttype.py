from enum import Enum


class RepaymentStatus(Enum):
    Pending = 1
    Failed = 2
    Confirmed = 3