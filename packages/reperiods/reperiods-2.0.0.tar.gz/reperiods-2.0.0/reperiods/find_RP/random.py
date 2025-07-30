import numpy as np
import pandas as pd

from ..representative_periods import RepresentativePeriods


def random_method(
    data: pd.DataFrame, N_RP: int, RP_length: int
) -> list[RepresentativePeriods]:
    """Generate representative periods (RPs) and their weights using random selection.

    Args:
        data (DataFrame): A DataFrame containing the data where RP will be found
        N_RP (int): The number of representative periods to generate.
        RP_length (int): The length of each representative period.

    Returns:
        list: A list of RepresentativePeriods objects, each representing an RP with its weight.
    """
    # Get RP candidates (not normalized)
    Number_of_candidate_RP = data.shape[0] // RP_length
    P_candidates = {
        P_id: data.iloc[P_id * RP_length : (P_id + 1) * RP_length]
        for P_id in range(Number_of_candidate_RP)
    }

    # Randomly choose N_RP candidate periods
    P_id_choosen = np.random.choice(
        np.arange(Number_of_candidate_RP), size=N_RP, replace=False
    )

    # Generate random weights and normalize them
    weights = np.random.random(N_RP)
    weights = weights / weights.sum()

    # Create RepresentativePeriods objects for the chosen periods with their weights
    representative_periods = [
        RepresentativePeriods(data=P_candidates[P_id], weight=weights[i])
        for i, P_id in enumerate(P_id_choosen)
    ]

    return representative_periods