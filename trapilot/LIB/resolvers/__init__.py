# flake8: noqa: F401
# isort: off
from trapilot.LIB.resolvers.iresolver import IResolver
from trapilot.LIB.resolvers.exchange_resolver import ExchangeResolver

# isort: on
# Don't import HyperoptResolver to avoid loading the whole Optimize tree
# from trapilot.LIB.resolvers.hyperopt_resolver import HyperOptResolver
from trapilot.LIB.resolvers.pairlist_resolver import PairListResolver
from trapilot.LIB.resolvers.protection_resolver import ProtectionResolver
from trapilot.LIB.resolvers.strategy_resolver import StrategyResolver
