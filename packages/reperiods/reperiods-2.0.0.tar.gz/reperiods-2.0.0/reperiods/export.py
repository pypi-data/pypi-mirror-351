import os
import pandas as pd

from .representative_periods import RepresentativePeriods


def save_RP(folder_path: str, RPs: list[RepresentativePeriods], sep: str = ","):
    """Save representative periods (RPs) and their weights to CSV files.

    Args:
        folder_path (str): The path to the folder where the files will be saved.
        temporal_data (TemporalData): A TemporalData object containing RPs and their weights.
        sep (str, optional): The separator used in the CSV files. Defaults to ','.

    Returns:
        None
    """
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save individual RPs and collect weights
    weights = []
    for i, RP in enumerate(RPs):
        RP_filename = f"RP_{str(i).zfill(2)}.csv"
        RP_path = os.path.join(folder_path, RP_filename)
        RP.data.to_csv(RP_path, sep=sep)
        weights.append(RP.weight)

    # Create a DataFrame for weights and save to CSV
    weights_df = pd.DataFrame(
        weights,
        index=[f"RP_{str(i).zfill(2)}" for i in range(len(RPs))],
        columns=["value"],
    )
    weights_df_filename = "weights.csv"
    weights_df_path = os.path.join(folder_path, weights_df_filename)
    weights_df.to_csv(weights_df_path, sep=sep)
