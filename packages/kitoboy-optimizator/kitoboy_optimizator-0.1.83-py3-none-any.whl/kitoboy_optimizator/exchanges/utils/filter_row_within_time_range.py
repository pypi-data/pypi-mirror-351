import numpy as np

def filter_rows_within_time_range(data:np.ndarray, start_timestamp: int, end_timestamp: int) -> np.ndarray:
    """
    Filters rows from an OHLCV ndarray to keep only the data within a specified time range.

    Parameters:
    - data: A NumPy ndarray containing OHLCV data, with time assumed to be in the first column.
    - start_timestamp: The starting time threshold. Rows with time values less than this will be excluded.
    - end_timestamp: The ending time threshold. Rows with time values greater than this will be excluded.

    Returns:
    - A NumPy ndarray with rows within the specified time range.
    """
    # Filter rows where the time is greater than or equal to the start timestamp
    # and less than or equal to the end timestamp
    filtered_data = np.unique(data[(data[:, 0] >= start_timestamp) & (data[:, 0] <= end_timestamp)], axis=0)
    return filtered_data