# flake8: noqa: F401
# isort: off
from trapilot.resolvers.iresolver import IResolver
from trapilot.resolvers.exchange_resolver import ExchangeResolver
# isort: on
# Don't import HyperoptResolver to avoid loading the whole Optimize tree
# from trapilot.resolvers.hyperopt_resolver import HyperOptResolver
from trapilot.resolvers.pairlist_resolver import PairListResolver
from trapilot.resolvers.protection_resolver import ProtectionResolver
from trapilot.resolvers.strategy_resolver import StrategyResolver
