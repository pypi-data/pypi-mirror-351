import numpy as np
import pandas as pd

from ..representative_periods import RepresentativePeriods

def kmedoids_method(
    data: pd.DataFrame, N_RP: int, RP_length: int
) -> list[RepresentativePeriods]:
    """Generate representative periods (RPs) using the k-medoids clustering method. Weights are calculated proportionally to the number of representatives in each cluster.

    Args:
        data (DataFrame): A DataFrame containing the data where RP will be found.
        N_RP (int): The number of representative periods to generate.
        RP_length (int): The length of each representative period.

    Returns:
        list: A list of RepresentativePeriods objects, each representing an RP with its weight.

    Raises:
        ImportError: If the scikit-learn-extra package is not installed. Please install it by running: pip install reperiods[kmedoids].
    """
    try:
        from sklearn_extra.cluster import KMedoids
    except ImportError:
        raise ImportError(
            "The kmedoids_method requires the scikit-learn-extra package, which is not installed. "
            "Please install it by running: pip install reperiods[kmedoids]"
        )

    # Get RP candidates (not normalized)
    Number_of_candidate_RP = data.shape[0] // RP_length
    P_candidates = {
        P_id: data.iloc[P_id * RP_length : (P_id + 1) * RP_length]
        for P_id in range(Number_of_candidate_RP)
    }

    # Convert candidate data to a format suitable for k-medoids
    data = np.array(
        [
            P_candidate.to_numpy().reshape((RP_length * data.shape[1]), order="F")
            for P_candidate in P_candidates.values()
        ]
    )

    # Apply k-medoids clustering
    kmedoids = KMedoids(metric="euclidean", n_clusters=N_RP)
    kmedoids.fit(data)

    # Count the number of data points in each cluster (representative period)
    number_by_cluster = {
        P_id: (kmedoids.predict(data) == k).sum()
        for k, P_id in enumerate(kmedoids.medoid_indices_)
    }

    # Calculate weights for each representative period
    weights = [
        number_by_cluster[P_id] / Number_of_candidate_RP
        for P_id in kmedoids.medoid_indices_
    ]

    # Create RepresentativePeriods objects for the medoids with their weights
    representative_periods = [
        RepresentativePeriods(data=P_candidates[P_id], weight=weights[i])
        for i, P_id in enumerate(kmedoids.medoid_indices_)
    ]

    return representative_periods
