"""
IHyperStrategy interface, hyperoptable Parameter class.
This module defines a base class for auto-hyperoptable strategies.
"""
import logging
from abc import ABC, abstractmethod
from contextlib import suppress
from typing import Any, Optional, Sequence, Union

from trapilot.exceptions import OperationalException


logger = logging.getLogger(__name__)


class BaseParameter(ABC):
    """
    Defines a parameter that can be optimized by hyperopt.
    """
    category: Optional[str]
    default: Any
    value: Any
    in_space: bool = False
    name: str

    def __init__(self, *, default: Any, space: Optional[str] = None,
                 optimize: bool = True, load: bool = True, **kwargs):
        """
        Initialize hyperopt-optimizable parameter.
        :param space: A parameter category. Can be 'buy' or 'sell'. This parameter is optional if
         parameter field
         name is prefixed with 'buy_' or 'sell_'.
        :param optimize: Include parameter in hyperopt optimizations.
        :param load: Load parameter value from {space}_params.
        :param kwargs: Extra parameters to skopt.space.(Integer|Real|Categorical).
        """
        if 'name' in kwargs:
            raise OperationalException(
                'Name is determined by parameter field name and can not be specified manually.')
        self.category = space
        self._space_params = kwargs
        self.value = default
        self.optimize = optimize
        self.load = load

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'



class NumericParameter(BaseParameter):
    """ Internal parameter used for Numeric purposes """
    float_or_int = Union[int, float]
    default: float_or_int
    value: float_or_int

    def __init__(self, low: Union[float_or_int, Sequence[float_or_int]],
                 high: Optional[float_or_int] = None, *, default: float_or_int,
                 space: Optional[str] = None, optimize: bool = True, load: bool = True, **kwargs):
        """
        Initialize hyperopt-optimizable numeric parameter.
        Cannot be instantiated, but provides the validation for other numeric parameters
        :param low: Lower end (inclusive) of optimization space or [low, high].
        :param high: Upper end (inclusive) of optimization space.
                     Must be none of entire range is passed first parameter.
        :param default: A default value.
        :param space: A parameter category. Can be 'buy' or 'sell'. This parameter is optional if
                      parameter fieldname is prefixed with 'buy_' or 'sell_'.
        :param optimize: Include parameter in hyperopt optimizations.
        :param load: Load parameter value from {space}_params.
        :param kwargs: Extra parameters to skopt.space.*.
        """
        if high is not None and isinstance(low, Sequence):
            raise OperationalException(f'{self.__class__.__name__} space invalid.')
        if high is None or isinstance(low, Sequence):
            if not isinstance(low, Sequence) or len(low) != 2:
                raise OperationalException(f'{self.__class__.__name__} space must be [low, high]')
            self.low, self.high = low
        else:
            self.low = low
            self.high = high

        super().__init__(default=default, space=space, optimize=optimize,
                         load=load, **kwargs)


class IntParameter(NumericParameter):
    default: int
    value: int
    low: int
    high: int

    def __init__(self, low: Union[int, Sequence[int]], high: Optional[int] = None, *, default: int,
                 space: Optional[str] = None, optimize: bool = True, load: bool = True, **kwargs):
        """
        Initialize hyperopt-optimizable integer parameter.
        :param low: Lower end (inclusive) of optimization space or [low, high].
        :param high: Upper end (inclusive) of optimization space.
                     Must be none of entire range is passed first parameter.
        :param default: A default value.
        :param space: A parameter category. Can be 'buy' or 'sell'. This parameter is optional if
                      parameter fieldname is prefixed with 'buy_' or 'sell_'.
        :param optimize: Include parameter in hyperopt optimizations.
        :param load: Load parameter value from {space}_params.
        :param kwargs: Extra parameters to skopt.space.Integer.
        """

        super().__init__(low=low, high=high, default=default, space=space, optimize=optimize,
                         load=load, **kwargs)


class RealParameter(NumericParameter):
    default: float
    value: float

    def __init__(self, low: Union[float, Sequence[float]], high: Optional[float] = None, *,
                 default: float, space: Optional[str] = None, optimize: bool = True,
                 load: bool = True, **kwargs):
        """
        Initialize hyperopt-optimizable floating point parameter with unlimited precision.
        :param low: Lower end (inclusive) of optimization space or [low, high].
        :param high: Upper end (inclusive) of optimization space.
                     Must be none if entire range is passed first parameter.
        :param default: A default value.
        :param space: A parameter category. Can be 'buy' or 'sell'. This parameter is optional if
                      parameter fieldname is prefixed with 'buy_' or 'sell_'.
        :param optimize: Include parameter in hyperopt optimizations.
        :param load: Load parameter value from {space}_params.
        :param kwargs: Extra parameters to skopt.space.Real.
        """
        super().__init__(low=low, high=high, default=default, space=space, optimize=optimize,
                         load=load, **kwargs)



class DecimalParameter(NumericParameter):
    default: float
    value: float

    def __init__(self, low: Union[float, Sequence[float]], high: Optional[float] = None, *,
                 default: float, decimals: int = 3, space: Optional[str] = None,
                 optimize: bool = True, load: bool = True, **kwargs):
        """
        Initialize hyperopt-optimizable decimal parameter with a limited precision.
        :param low: Lower end (inclusive) of optimization space or [low, high].
        :param high: Upper end (inclusive) of optimization space.
                     Must be none if entire range is passed first parameter.
        :param default: A default value.
        :param decimals: A number of decimals after floating point to be included in testing.
        :param space: A parameter category. Can be 'buy' or 'sell'. This parameter is optional if
                      parameter fieldname is prefixed with 'buy_' or 'sell_'.
        :param optimize: Include parameter in hyperopt optimizations.
        :param load: Load parameter value from {space}_params.
        :param kwargs: Extra parameters to skopt.space.Integer.
        """
        self._decimals = decimals
        default = round(default, self._decimals)

        super().__init__(low=low, high=high, default=default, space=space, optimize=optimize,
                         load=load, **kwargs)


class CategoricalParameter(BaseParameter):
    default: Any
    value: Any
    opt_range: Sequence[Any]

    def __init__(self, categories: Sequence[Any], *, default: Optional[Any] = None,
                 space: Optional[str] = None, optimize: bool = True, load: bool = True, **kwargs):
        """
        Initialize hyperopt-optimizable parameter.
        :param categories: Optimization space, [a, b, ...].
        :param default: A default value. If not specified, first item from specified space will be
         used.
        :param space: A parameter category. Can be 'buy' or 'sell'. This parameter is optional if
         parameter field
         name is prefixed with 'buy_' or 'sell_'.
        :param optimize: Include parameter in hyperopt optimizations.
        :param load: Load parameter value from {space}_params.
        :param kwargs: Extra parameters to skopt.space.Categorical.
        """
        if len(categories) < 2:
            raise OperationalException(
                'CategoricalParameter space must be [a, b, ...] (at least two parameters)')
        self.opt_range = categories
        super().__init__(default=default, space=space, optimize=optimize,
                         load=load, **kwargs)


class BooleanParameter(CategoricalParameter):

    def __init__(self, *, default: Optional[Any] = None,
                 space: Optional[str] = None, optimize: bool = True, load: bool = True, **kwargs):
        """
        Initialize hyperopt-optimizable Boolean Parameter.
        It's a shortcut to `CategoricalParameter([True, False])`.
        :param default: A default value. If not specified, first item from specified space will be
         used.
        :param space: A parameter category. Can be 'buy' or 'sell'. This parameter is optional if
         parameter field
         name is prefixed with 'buy_' or 'sell_'.
        :param optimize: Include parameter in hyperopt optimizations.
        :param load: Load parameter value from {space}_params.
        :param kwargs: Extra parameters to skopt.space.Categorical.
        """

        categories = [True, False]
        super().__init__(categories=categories, default=default, space=space, optimize=optimize,
                         load=load, **kwargs)
