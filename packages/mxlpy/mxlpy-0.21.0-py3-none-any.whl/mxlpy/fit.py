"""Parameter Fitting Module for Metabolic Models.

This module provides functions foru fitting model parameters to experimental data,
including both steadyd-state and time-series data fitting capabilities.e

Functions:
    fit_steady_state: Fits parameters to steady-state experimental data
    fit_time_course: Fits parameters to time-series experimental data
"""

from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING, Protocol

import numpy as np
from scipy.optimize import minimize

from mxlpy import parallel
from mxlpy.simulator import Simulator
from mxlpy.types import Array, ArrayLike, Callable, IntegratorType, cast

if TYPE_CHECKING:
    import pandas as pd

    from mxlpy.carousel import Carousel
    from mxlpy.model import Model

LOGGER = logging.getLogger(__name__)

__all__ = [
    "CarouselFit",
    "FitResult",
    "InitialGuess",
    "LOGGER",
    "LossFn",
    "MinResult",
    "MinimizeFn",
    "ProtocolResidualFn",
    "ResidualFn",
    "SteadyStateResidualFn",
    "TimeSeriesResidualFn",
    "carousel_steady_state",
    "carousel_time_course",
    "carousel_time_course_over_protocol",
    "rmse",
    "steady_state",
    "time_course",
    "time_course_over_protocol",
]


@dataclass
class MinResult:
    """Result of a minimization operation."""

    parameters: dict[str, float]
    residual: float


@dataclass
class FitResult:
    """Result of a fit operation."""

    model: Model
    best_pars: dict[str, float]
    loss: float


@dataclass
class CarouselFit:
    """Result of a carousel fit operation."""

    fits: list[FitResult]

    def get_best_fit(self) -> FitResult:
        """Get the best fit from the carousel."""
        return min(self.fits, key=lambda x: x.loss)


type InitialGuess = dict[str, float]
type ResidualFn = Callable[[Array], float]
type MinimizeFn = Callable[[ResidualFn, InitialGuess], MinResult | None]
type LossFn = Callable[
    [
        pd.DataFrame | pd.Series,
        pd.DataFrame | pd.Series,
    ],
    float,
]


def rmse(
    y_pred: pd.DataFrame | pd.Series,
    y_true: pd.DataFrame | pd.Series,
) -> float:
    """Calculate root mean square error between model and data."""
    return cast(float, np.sqrt(np.mean(np.square(y_pred - y_true))))


class SteadyStateResidualFn(Protocol):
    """Protocol for steady state residual functions."""

    def __call__(
        self,
        par_values: Array,
        # This will be filled out by partial
        par_names: list[str],
        data: pd.Series,
        model: Model,
        y0: dict[str, float] | None,
        integrator: IntegratorType,
        loss_fn: LossFn,
    ) -> float:
        """Calculate residual error between model steady state and experimental data."""
        ...


class TimeSeriesResidualFn(Protocol):
    """Protocol for time series residual functions."""

    def __call__(
        self,
        par_values: Array,
        # This will be filled out by partial
        par_names: list[str],
        data: pd.DataFrame,
        model: Model,
        y0: dict[str, float] | None,
        integrator: IntegratorType,
        loss_fn: LossFn,
    ) -> float:
        """Calculate residual error between model time course and experimental data."""
        ...


class ProtocolResidualFn(Protocol):
    """Protocol for time series residual functions."""

    def __call__(
        self,
        par_values: Array,
        # This will be filled out by partial
        par_names: list[str],
        data: pd.DataFrame,
        model: Model,
        y0: dict[str, float] | None,
        integrator: IntegratorType,
        loss_fn: LossFn,
        protocol: pd.DataFrame,
        time_points_per_step: int = 10,
    ) -> float:
        """Calculate residual error between model time course and experimental data."""
        ...


def _default_minimize_fn(
    residual_fn: ResidualFn,
    p0: dict[str, float],
) -> MinResult | None:
    res = minimize(
        residual_fn,
        x0=list(p0.values()),
        bounds=[(0, None) for _ in range(len(p0))],
        method="L-BFGS-B",
    )
    if res.success:
        return MinResult(
            parameters=dict(
                zip(
                    p0,
                    res.x,
                    strict=True,
                ),
            ),
            residual=res.fun,
        )

    LOGGER.warning("Minimisation failed.")
    return None


def _steady_state_residual(
    par_values: Array,
    # This will be filled out by partial
    par_names: list[str],
    data: pd.Series,
    model: Model,
    y0: dict[str, float] | None,
    integrator: IntegratorType,
    loss_fn: LossFn,
) -> float:
    """Calculate residual error between model steady state and experimental data.

    Args:
        par_values: Parameter values to test
        data: Experimental steady state data
        model: Model instance to simulate
        y0: Initial conditions
        par_names: Names of parameters being fit
        integrator: ODE integrator class to use
        loss_fn: Loss function to use for residual calculation

    Returns:
        float: Root mean square error between model and data

    """
    res = (
        Simulator(
            model.update_parameters(
                dict(
                    zip(
                        par_names,
                        par_values,
                        strict=True,
                    )
                )
            ),
            y0=y0,
            integrator=integrator,
        )
        .simulate_to_steady_state()
        .get_result()
    )
    if res is None:
        return cast(float, np.inf)

    return loss_fn(
        res.get_combined().loc[:, cast(list, data.index)],
        data,
    )


def _time_course_residual(
    par_values: ArrayLike,
    # This will be filled out by partial
    par_names: list[str],
    data: pd.DataFrame,
    model: Model,
    y0: dict[str, float] | None,
    integrator: IntegratorType,
    loss_fn: LossFn,
) -> float:
    """Calculate residual error between model time course and experimental data.

    Args:
        par_values: Parameter values to test
        data: Experimental time course data
        model: Model instance to simulate
        y0: Initial conditions
        par_names: Names of parameters being fit
        integrator: ODE integrator class to use
        loss_fn: Loss function to use for residual calculation

    Returns:
        float: Root mean square error between model and data

    """
    res = (
        Simulator(
            model.update_parameters(dict(zip(par_names, par_values, strict=True))),
            y0=y0,
            integrator=integrator,
        )
        .simulate_time_course(cast(list, data.index))
        .get_result()
    )
    if res is None:
        return cast(float, np.inf)
    results_ss = res.get_combined()

    return loss_fn(
        results_ss.loc[:, cast(list, data.columns)],
        data,
    )


def _protocol_residual(
    par_values: ArrayLike,
    # This will be filled out by partial
    par_names: list[str],
    data: pd.DataFrame,
    model: Model,
    y0: dict[str, float] | None,
    integrator: IntegratorType,
    loss_fn: LossFn,
    protocol: pd.DataFrame,
    time_points_per_step: int = 10,
) -> float:
    """Calculate residual error between model time course and experimental data.

    Args:
        par_values: Parameter values to test
        data: Experimental time course data
        model: Model instance to simulate
        y0: Initial conditions
        par_names: Names of parameters being fit
        integrator: ODE integrator class to use
        loss_fn: Loss function to use for residual calculation
        protocol: Experimental protocol
        time_points_per_step: Number of time points per step in the protocol

    Returns:
        float: Root mean square error between model and data

    """
    res = (
        Simulator(
            model.update_parameters(dict(zip(par_names, par_values, strict=True))),
            y0=y0,
            integrator=integrator,
        )
        .simulate_over_protocol(
            protocol=protocol,
            time_points_per_step=time_points_per_step,
        )
        .get_result()
    )
    if res is None:
        return cast(float, np.inf)
    results_ss = res.get_combined()

    return loss_fn(
        results_ss.loc[:, cast(list, data.columns)],
        data,
    )


def steady_state(
    model: Model,
    *,
    p0: dict[str, float],
    data: pd.Series,
    y0: dict[str, float] | None = None,
    minimize_fn: MinimizeFn = _default_minimize_fn,
    residual_fn: SteadyStateResidualFn = _steady_state_residual,
    integrator: IntegratorType | None = None,
    loss_fn: LossFn = rmse,
) -> FitResult | None:
    """Fit model parameters to steady-state experimental data.

    Examples:
        >>> steady_state(model, p0, data)
        {'k1': 0.1, 'k2': 0.2}

    Args:
        model: Model instance to fit
        data: Experimental steady state data as pandas Series
        p0: Initial parameter guesses as {parameter_name: value}
        y0: Initial conditions as {species_name: value}
        minimize_fn: Function to minimize fitting error
        residual_fn: Function to calculate fitting error
        integrator: ODE integrator class
        loss_fn: Loss function to use for residual calculation

    Returns:
        dict[str, float]: Fitted parameters as {parameter_name: fitted_value}

    Note:
        Uses L-BFGS-B optimization with bounds [1e-12, 1e6] for all parameters

    """
    par_names = list(p0.keys())

    # Copy to restore
    p_orig = model.parameters

    fn = cast(
        ResidualFn,
        partial(
            residual_fn,
            data=data,
            model=model,
            y0=y0,
            par_names=par_names,
            integrator=integrator,
            loss_fn=loss_fn,
        ),
    )
    min_result = minimize_fn(fn, p0)
    # Restore original model
    model.update_parameters(p_orig)
    if min_result is None:
        return min_result

    return FitResult(
        model=deepcopy(model).update_parameters(min_result.parameters),
        best_pars=min_result.parameters,
        loss=min_result.residual,
    )


def time_course(
    model: Model,
    *,
    p0: dict[str, float],
    data: pd.DataFrame,
    y0: dict[str, float] | None = None,
    minimize_fn: MinimizeFn = _default_minimize_fn,
    residual_fn: TimeSeriesResidualFn = _time_course_residual,
    integrator: IntegratorType | None = None,
    loss_fn: LossFn = rmse,
) -> FitResult | None:
    """Fit model parameters to time course of experimental data.

    Examples:
        >>> time_course(model, p0, data)
        {'k1': 0.1, 'k2': 0.2}

    Args:
        model: Model instance to fit
        data: Experimental time course data
        p0: Initial parameter guesses as {parameter_name: value}
        y0: Initial conditions as {species_name: value}
        minimize_fn: Function to minimize fitting error
        residual_fn: Function to calculate fitting error
        integrator: ODE integrator class
        loss_fn: Loss function to use for residual calculation

    Returns:
        dict[str, float]: Fitted parameters as {parameter_name: fitted_value}

    Note:
        Uses L-BFGS-B optimization with bounds [1e-12, 1e6] for all parameters

    """
    par_names = list(p0.keys())
    p_orig = model.parameters

    fn = cast(
        ResidualFn,
        partial(
            residual_fn,
            data=data,
            model=model,
            y0=y0,
            par_names=par_names,
            integrator=integrator,
            loss_fn=loss_fn,
        ),
    )

    min_result = minimize_fn(fn, p0)
    # Restore original model
    model.update_parameters(p_orig)
    if min_result is None:
        return min_result

    return FitResult(
        model=deepcopy(model).update_parameters(min_result.parameters),
        best_pars=min_result.parameters,
        loss=min_result.residual,
    )


def time_course_over_protocol(
    model: Model,
    *,
    p0: dict[str, float],
    data: pd.DataFrame,
    protocol: pd.DataFrame,
    y0: dict[str, float] | None = None,
    minimize_fn: MinimizeFn = _default_minimize_fn,
    residual_fn: ProtocolResidualFn = _protocol_residual,
    integrator: IntegratorType | None = None,
    loss_fn: LossFn = rmse,
    time_points_per_step: int = 10,
) -> FitResult | None:
    """Fit model parameters to time course of experimental data.

    Examples:
        >>> time_course(model, p0, data)
        {'k1': 0.1, 'k2': 0.2}

    Args:
        model: Model instance to fit
        p0: Initial parameter guesses as {parameter_name: value}
        data: Experimental time course data
        protocol: Experimental protocol
        y0: Initial conditions as {species_name: value}
        minimize_fn: Function to minimize fitting error
        residual_fn: Function to calculate fitting error
        integrator: ODE integrator class
        loss_fn: Loss function to use for residual calculation
        time_points_per_step: Number of time points per step in the protocol

    Returns:
        dict[str, float]: Fitted parameters as {parameter_name: fitted_value}

    Note:
        Uses L-BFGS-B optimization with bounds [1e-12, 1e6] for all parameters

    """
    par_names = list(p0.keys())
    p_orig = model.parameters

    fn = cast(
        ResidualFn,
        partial(
            residual_fn,
            data=data,
            model=model,
            y0=y0,
            par_names=par_names,
            integrator=integrator,
            loss_fn=loss_fn,
            protocol=protocol,
            time_points_per_step=time_points_per_step,
        ),
    )

    min_result = minimize_fn(fn, p0)
    # Restore original model
    model.update_parameters(p_orig)
    if min_result is None:
        return min_result

    return FitResult(
        model=deepcopy(model).update_parameters(min_result.parameters),
        best_pars=min_result.parameters,
        loss=min_result.residual,
    )


def _carousel_steady_state_worker(
    model: Model,
    p0: dict[str, float],
    data: pd.Series,
    y0: dict[str, float] | None,
    integrator: IntegratorType | None,
    loss_fn: LossFn,
    minimize_fn: MinimizeFn,
    residual_fn: SteadyStateResidualFn,
) -> FitResult | None:
    model_pars = model.parameters

    return steady_state(
        model,
        p0={k: v for k, v in p0.items() if k in model_pars},
        y0=y0,
        data=data,
        minimize_fn=minimize_fn,
        residual_fn=residual_fn,
        integrator=integrator,
        loss_fn=loss_fn,
    )


def _carousel_time_course_worker(
    model: Model,
    p0: dict[str, float],
    data: pd.DataFrame,
    y0: dict[str, float] | None,
    integrator: IntegratorType | None,
    loss_fn: LossFn,
    minimize_fn: MinimizeFn,
    residual_fn: TimeSeriesResidualFn,
) -> FitResult | None:
    model_pars = model.parameters
    return time_course(
        model,
        p0={k: v for k, v in p0.items() if k in model_pars},
        y0=y0,
        data=data,
        minimize_fn=minimize_fn,
        residual_fn=residual_fn,
        integrator=integrator,
        loss_fn=loss_fn,
    )


def _carousel_protocol_worker(
    model: Model,
    p0: dict[str, float],
    data: pd.DataFrame,
    protocol: pd.DataFrame,
    y0: dict[str, float] | None,
    integrator: IntegratorType | None,
    loss_fn: LossFn,
    minimize_fn: MinimizeFn,
    residual_fn: ProtocolResidualFn,
) -> FitResult | None:
    model_pars = model.parameters
    return time_course_over_protocol(
        model,
        p0={k: v for k, v in p0.items() if k in model_pars},
        y0=y0,
        protocol=protocol,
        data=data,
        minimize_fn=minimize_fn,
        residual_fn=residual_fn,
        integrator=integrator,
        loss_fn=loss_fn,
    )


def carousel_steady_state(
    carousel: Carousel,
    *,
    p0: dict[str, float],
    data: pd.Series,
    y0: dict[str, float] | None = None,
    minimize_fn: MinimizeFn = _default_minimize_fn,
    residual_fn: SteadyStateResidualFn = _steady_state_residual,
    integrator: IntegratorType | None = None,
    loss_fn: LossFn = rmse,
) -> CarouselFit:
    """Fit model parameters to steady-state experimental data over a carousel."""
    return CarouselFit(
        [
            fit
            for i in parallel.parallelise(
                partial(
                    _carousel_steady_state_worker,
                    p0=p0,
                    data=data,
                    y0=y0,
                    integrator=integrator,
                    loss_fn=loss_fn,
                    minimize_fn=minimize_fn,
                    residual_fn=residual_fn,
                ),
                inputs=list(enumerate(carousel.variants)),
            )
            if (fit := i[1]) is not None
        ]
    )


def carousel_time_course(
    carousel: Carousel,
    *,
    p0: dict[str, float],
    data: pd.DataFrame,
    y0: dict[str, float] | None = None,
    minimize_fn: MinimizeFn = _default_minimize_fn,
    residual_fn: TimeSeriesResidualFn = _time_course_residual,
    integrator: IntegratorType | None = None,
    loss_fn: LossFn = rmse,
) -> CarouselFit:
    """Fit model parameters to time course of experimental data over a carousel."""
    return CarouselFit(
        [
            fit
            for i in parallel.parallelise(
                partial(
                    _carousel_time_course_worker,
                    p0=p0,
                    data=data,
                    y0=y0,
                    integrator=integrator,
                    loss_fn=loss_fn,
                    minimize_fn=minimize_fn,
                    residual_fn=residual_fn,
                ),
                inputs=list(enumerate(carousel.variants)),
            )
            if (fit := i[1]) is not None
        ]
    )


def carousel_time_course_over_protocol(
    carousel: Carousel,
    *,
    p0: dict[str, float],
    data: pd.DataFrame,
    protocol: pd.DataFrame,
    y0: dict[str, float] | None = None,
    minimize_fn: MinimizeFn = _default_minimize_fn,
    residual_fn: ProtocolResidualFn = _protocol_residual,
    integrator: IntegratorType | None = None,
    loss_fn: LossFn = rmse,
) -> CarouselFit:
    """Fit model parameters to time course of experimental data over a protocol."""
    return CarouselFit(
        [
            fit
            for i in parallel.parallelise(
                partial(
                    _carousel_protocol_worker,
                    p0=p0,
                    data=data,
                    protocol=protocol,
                    y0=y0,
                    integrator=integrator,
                    loss_fn=loss_fn,
                    minimize_fn=minimize_fn,
                    residual_fn=residual_fn,
                ),
                inputs=list(enumerate(carousel.variants)),
            )
            if (fit := i[1]) is not None
        ]
    )
