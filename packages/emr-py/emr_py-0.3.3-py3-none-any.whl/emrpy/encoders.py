from sklearn.preprocessing import OrdinalEncoder
import numpy as np
import pandas as pd
from typing import Optional, Tuple, List


def encode_cats_pandas(
    train_df: pd.DataFrame,
    cat_cols: List[str],
    test_df: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], OrdinalEncoder]:
    """
    Encode categorical columns using OrdinalEncoder with handling for unknown and missing values.

    Parameters:
    -----------
    train_df : pandas.DataFrame
        Training DataFrame containing the categorical columns to encode
    cat_cols : list
        List of categorical column names to encode
    test_df : pandas.DataFrame, optional
        Test DataFrame containing the same categorical columns (default=None)
    unknown_value : int, optional
        Value to use for unknown categories (default=-2)
    missing_value : int, optional
        Value to use for missing values (default=-1)

    Returns:
    --------
    Tuple[pd.DataFrame, Optional[pd.DataFrame], OrdinalEncoder]
        Encoded training DataFrame, encoded test DataFrame (or None),
        and the fitted OrdinalEncoder instance for future use.
    """
    train_df = train_df.copy()
    test_df = test_df.copy() if test_df is not None else None

    encoder = OrdinalEncoder(
        categories="auto",
        dtype=np.int16,
        handle_unknown="use_encoded_value",
        unknown_value=-2,
        encoded_missing_value=-1,
    )

    train_encoded = encoder.fit_transform(train_df[cat_cols])
    for idx, col in enumerate(cat_cols):
        train_df[col] = train_encoded[:, idx]

    if test_df is not None:
        test_encoded = encoder.transform(test_df[cat_cols])
        for idx, col in enumerate(cat_cols):
            test_df[col] = test_encoded[:, idx]

    return train_df, test_df, encoder
