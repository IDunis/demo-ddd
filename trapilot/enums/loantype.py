from enum import Enum


class LoanStatus(Enum):
    Pending = 1
    Failed = 2
    Confirmed = 3