from typing import List
import pandas as pd
from fiddler.schemas.model_schema import Column, ModelSchema
from fiddler.constants.model import DataType


def create_columns_from_df(df: pd.DataFrame) -> ModelSchema:
    """
    Helper function to create Columns from a pandas DataFrame column dtypes.
    timedelta, period, interval & object dtypes are converted to string.
    Sparse dtypes are not handled.
    Args:
        df: Input pandas DataFrame

    Returns:
        ModelSchema
    """
    columns: List[Column] = []

    # Check if the DataFrame is empty - a dataframe with columns but no rows is valid
    if len(df.columns) == 0:
        raise ValueError("Cannot create columns from an empty DataFrame")

    for col_name, dtype in df.dtypes.items():
        # Map pandas dtypes to Fiddler DataTypes
        if pd.api.types.is_float_dtype(dtype):
            data_type = DataType.FLOAT
            col_min, col_max = float(df[col_name].min()), float(df[col_name].max())
            col = Column(
                name=col_name,
                data_type=data_type,
                min=col_min,
                max=col_max
            )
        elif pd.api.types.is_integer_dtype(dtype):
            data_type = DataType.INTEGER
            col = Column(
                name=col_name,
                data_type=data_type,
                min=df[col_name].min(),
                max=df[col_name].max()
            )
        elif pd.api.types.is_bool_dtype(dtype):
            col = Column(
                name=col_name,
                data_type=DataType.BOOLEAN
            )
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            col = Column(
                name=col_name,
                data_type=DataType.TIMESTAMP
            )
        elif pd.api.types.is_categorical_dtype(dtype):
            col = Column(
                name=col_name,
                data_type=DataType.CATEGORY,
                categories=df[col_name].cat.categories.tolist()
            )
        else:
            # Default to string for other types
            col = Column(
                name=col_name,
                data_type=DataType.STRING
            )

        columns.append(col)

    return ModelSchema(columns=columns)
