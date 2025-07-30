from typing import Any

import numpy as np
import pandas as pd
import pulp as pl
from sklearn.preprocessing import MinMaxScaler

from ..representative_periods import RepresentativePeriods
from ..utils import duration_function


def poncelet_method(
    data: pd.DataFrame,
    curve_set: pd.Index,
    N_RP: int,
    RP_length: int,
    N_bins: int = 15,
    solver: Any = None,
) -> list[RepresentativePeriods]:
    """Find representative periods (RPs) and their weights using the Poncelet et al. (2017) method.

    Args:
        temporal_data (TemporalData): A TemporalData object containing the input data.
        data (DataFrame): A DataFrame containing the data where RP will be found
        curve_set (Index): The set of curve
        N_RP (int): The number of representative periods to find.
        RP_length (int): The length of each representative period.
        N_bins (int, optional): The number of bins for duration curve discretization. Defaults to 15.
        solver (pulp solver, optional): The solver to use for optimization. Defaults to None. see : https://coin-or.github.io/pulp/guides/how_to_configure_solvers.html and https://coin-or.github.io/pulp/technical/solvers.html#module-pulp.apis

    Returns:
        list: A list of RepresentativePeriods objects, each representing an RP with its weight.
    """
    # Get RP candidates (not normalized)
    Number_of_candidate_RP = data.shape[0] // RP_length
    P_candidates = {
        P_id: data.iloc[P_id * RP_length : (P_id + 1) * RP_length]
        for P_id in range(Number_of_candidate_RP)
    }

    # Set bins
    bins = np.arange(N_bins) / (N_bins - 1)

    # Set scalers
    scalers = {}
    for curve in curve_set:
        scaler = MinMaxScaler()
        scaler.fit(data[curve].to_numpy().reshape(-1, 1))
        scalers[curve] = scaler

    ## Set MILP model
    # Constants
    L = {}
    for curve in curve_set:
        DC = duration_function(
            scalers[curve].transform(data[curve].to_numpy().reshape(-1, 1))
        )
        for bin in bins:
            L[curve, bin] = DC(bin)
    A = {}
    for P_id in P_candidates:
        for curve in curve_set:
            DC = duration_function(
                scalers[curve].transform(
                    P_candidates[P_id][curve].to_numpy().reshape(-1, 1)
                )
            )
            for bin in bins:
                A[curve, bin, P_id] = DC(bin)

    # Variables
    U = {P_id: pl.LpVariable(f"U_{P_id}", cat="Binary") for P_id in P_candidates}
    W = {
        P_id: pl.LpVariable(f"W_{P_id}", cat="Continuous", lowBound=0)
        for P_id in P_candidates
    }
    errors = {
        (curve, bin): pl.LpVariable(f"error_{curve}-{bin}", cat="Continuous")
        for curve in curve_set
        for bin in bins
    }

    # Constraints
    problem = pl.LpProblem("Poncelet_Method", pl.LpMinimize)
    problem += (
        pl.lpSum(U[P_id] for P_id in P_candidates) == N_RP,
        "Number_of_RP",
    )
    problem += (
        pl.lpSum(W[P_id] for P_id in P_candidates) == 1,
        "RP_weights",
    )

    for P_id in P_candidates:
        problem += (
            W[P_id] <= U[P_id],
            f"Weight_{P_id}_is_not_null_if_the_Period_{P_id}_is_selected",
        )

    for curve in curve_set:
        for bin in bins:
            problem += errors[curve, bin] >= L[curve, bin] - pl.lpSum(
                W[P_id] * A[curve, bin, P_id] for P_id in P_candidates
            )
            problem += (
                errors[curve, bin]
                >= pl.lpSum(W[P_id] * A[curve, bin, P_id] for P_id in P_candidates)
                - L[curve, bin]
            )

    # Objective
    problem += (
        pl.lpSum(errors[curve, bin] for curve in curve_set for bin in bins),
        "Minimize global error",
    )

    problem.solve(solver)

    representative_periods = []
    for P_id in P_candidates:
        if U[P_id].varValue == 1:
            representative_periods.append(
                RepresentativePeriods(data=P_candidates[P_id], weight=W[P_id].varValue)
            )
    return representative_periods