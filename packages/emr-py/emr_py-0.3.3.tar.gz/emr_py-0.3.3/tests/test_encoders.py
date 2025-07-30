import pandas as pd
import numpy as np
from emrpy.encoders import encode_cats_pandas


def test_encode_cats_pandas_train_only():
    # Simple training DataFrame
    train_data = {
        "col1": ["A", "B", "C", np.nan],
        "col2": ["X", "Y", "Z", "X"],
    }
    train_df = pd.DataFrame(train_data)

    # Define categorical columns
    cat_cols = ["col1", "col2"]

    # Run the function
    train_encoded, _, encoder = encode_cats_pandas(
        train_df=train_df,
        cat_cols=cat_cols,
    )

    # Check that encoded values are correct
    assert list(train_encoded["col1"]) == [0, 1, 2, -1]  # A, B, C, missing (-1)
    assert list(train_encoded["col2"]) == [0, 1, 2, 0]  # X, Y, Z
