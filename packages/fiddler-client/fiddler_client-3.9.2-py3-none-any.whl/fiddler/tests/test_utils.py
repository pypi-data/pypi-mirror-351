import os
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from fiddler.constants.model import DataType
from fiddler.schemas.server_info import Version
from fiddler.utils.helpers import group_by, try_series_retype
from fiddler.utils.column_generator import create_columns_from_df
from fiddler.utils.validations import validate_artifact_dir
from fiddler.utils.version import match_semver

MODEL_DATA = [{'Unnamed: 0': 43660,
  'CreditScore': 681,
  'Geography': 'France',
  'Gender': 'Female',
  'Age': 45,
  'Tenure': 4,
  'Balance': 150461.78248572032,
  'NumOfProducts': 1,
  'HasCrCard': True,
  'IsActiveMember': True,
  'EstimatedSalary': 121476.50483532489,
  'Churned': 'Not Churned',
  'probability_churned': 0.2070909278091097},
 {'Unnamed: 0': 87278,
  'CreditScore': 604,
  'Geography': 'Spain',
  'Gender': 'Male',
  'Age': 25,
  'Tenure': 8,
  'Balance': 870.563948633173,
  'NumOfProducts': 2,
  'HasCrCard': False,
  'IsActiveMember': True,
  'EstimatedSalary': 39030.86584360056,
  'Churned': 'Not Churned',
  'probability_churned': 0.0619905773329336},
 {'Unnamed: 0': 14317,
  'CreditScore': 648,
  'Geography': 'France',
  'Gender': 'Female',
  'Age': 50,
  'Tenure': 6,
  'Balance': 127661.4013780268,
  'NumOfProducts': 1,
  'HasCrCard': True,
  'IsActiveMember': True,
  'EstimatedSalary': -8216.031548157727,
  'Churned': 'Churned',
  'probability_churned': 0.1026814066436183},
 {'Unnamed: 0': 81932,
  'CreditScore': 670,
  'Geography': 'France',
  'Gender': 'Male',
  'Age': 49,
  'Tenure': 7,
  'Balance': 95199.48061342211,
  'NumOfProducts': 3,
  'HasCrCard': False,
  'IsActiveMember': True,
  'EstimatedSalary': 47114.97249302002,
  'Churned': 'Not Churned',
  'probability_churned': 0.2134035806234498},
 {'Unnamed: 0': 95321,
  'CreditScore': 616,
  'Geography': 'Germany',
  'Gender': 'Female',
  'Age': 35,
  'Tenure': 1,
  'Balance': 88151.28675933508,
  'NumOfProducts': 1,
  'HasCrCard': True,
  'IsActiveMember': False,
  'EstimatedSalary': 107882.06957422369,
  'Churned': 'Churned',
  'probability_churned': 0.8824657828379177},
 {'Unnamed: 0': 5405,
  'CreditScore': 536,
  'Geography': 'France',
  'Gender': 'Female',
  'Age': 41,
  'Tenure': 4,
  'Balance': 167680.40434914205,
  'NumOfProducts': 1,
  'HasCrCard': True,
  'IsActiveMember': True,
  'EstimatedSalary': 133588.33926550962,
  'Churned': 'Not Churned',
  'probability_churned': 0.1189636863349831},
 {'Unnamed: 0': 33188,
  'CreditScore': 666,
  'Geography': 'Spain',
  'Gender': 'Male',
  'Age': 34,
  'Tenure': 2,
  'Balance': 120370.38776657668,
  'NumOfProducts': 2,
  'HasCrCard': False,
  'IsActiveMember': True,
  'EstimatedSalary': 60070.356958972116,
  'Churned': 'Not Churned',
  'probability_churned': 0.1244325159224678},
 {'Unnamed: 0': 63421,
  'CreditScore': 613,
  'Geography': 'France',
  'Gender': 'Male',
  'Age': 35,
  'Tenure': 2,
  'Balance': 1632.9882268964022,
  'NumOfProducts': 2,
  'HasCrCard': True,
  'IsActiveMember': True,
  'EstimatedSalary': 77206.59807746019,
  'Churned': 'Not Churned',
  'probability_churned': 0.1037151191218035},
 {'Unnamed: 0': 72897,
  'CreditScore': 591,
  'Geography': 'Germany',
  'Gender': 'Male',
  'Age': 85,
  'Tenure': 4,
  'Balance': 115817.11190439922,
  'NumOfProducts': 1,
  'HasCrCard': False,
  'IsActiveMember': False,
  'EstimatedSalary': 23310.677701467852,
  'Churned': 'Not Churned',
  'probability_churned': 0.2658220429852892},
 {'Unnamed: 0': 9507,
  'CreditScore': 488,
  'Geography': 'Spain',
  'Gender': 'Female',
  'Age': 40,
  'Tenure': 8,
  'Balance': 101678.5269411524,
  'NumOfProducts': 1,
  'HasCrCard': True,
  'IsActiveMember': False,
  'EstimatedSalary': 9013.186551877934,
  'Churned': 'Not Churned',
  'probability_churned': 0.1167422545893403}
  ]

def test_match_semvar_version() -> None:
    assert match_semver(None, '>=22.9.0') is False
    assert match_semver(Version.parse('22.9.0'), '>=22.10.0') is False
    assert match_semver(Version.parse('22.10.0'), '>=22.10.0') is True
    assert match_semver(Version.parse('22.10.0'), '>22.10.0') is False
    assert match_semver(Version.parse('22.11.0'), '>=22.10.0') is True
    assert match_semver(Version.parse('22.11.0'), '>22.10.0') is True
    assert match_semver(Version.parse('22.10.0'), '<=22.10.0') is True
    assert match_semver(Version.parse('22.10.0'), '<22.10.0') is False
    assert match_semver(Version.parse('22.9.0'), '<22.10.0') is True
    assert match_semver(Version.parse('22.11.0-RC1'), '>=22.11.0') is True


def test_validate_artifact_dir(tmp_path) -> None:
    artifact_dir = os.path.join(Path(__file__).resolve().parent, 'artifact_test_dir')
    assert validate_artifact_dir(Path(artifact_dir)) is None
    # Test for artifact_dir not valid directory
    with pytest.raises(ValueError):
        validate_artifact_dir(Path('test'))
    # Test for package.py file not found
    mock_dir = tmp_path / 'test'
    mock_dir.mkdir()
    with pytest.raises(ValueError):
        validate_artifact_dir(Path(mock_dir))


def test_group_by_helper() -> None:
    df = pd.DataFrame(
        [
            {'col1': 1, 'col2': 'foo'},
            {'col1': 2, 'col2': 'bar'},
            {'col1': 3, 'col2': 'baz'},
            {'col1': 3, 'col2': 'foo'},
        ]
    )

    # with output_path
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / 'data.csv'

        assert file_path.exists() is False
        group_by(df=df, group_by_col='col2', output_path=file_path)
        assert file_path.exists() is True

    # without output path
    grouped_df = group_by(df=df, group_by_col='col2')
    assert grouped_df.equals(
        pd.DataFrame(
            [
                {'col2': 'foo', 'col1': [1, 3]},
                {'col2': 'bar', 'col1': [2]},
                {'col2': 'baz', 'col1': [3]},
            ]
        )
    )


def test_try_series_retype() -> None:
    series = pd.Series([1, 2, 3], dtype='float')
    series = try_series_retype(series, 'int')
    assert series.dtype == 'int'

    series = pd.Series([1, 2, None])
    series = try_series_retype(series, 'int')
    assert series.dtype == 'float'


def test_try_series_retype_str_or_unkown() -> None:
    series = pd.Series(['HIGH', 'MEDIUM', '', None], dtype='str')
    series = try_series_retype(series, 'str')
    assert series.dtype == 'object'


def test_try_series_retype_timestamp() -> None:
    series = pd.Series(
        ['2023-11-12 09:15:32.23', '2023-12-11 09:15:32.45'], dtype='str'
    )
    series = try_series_retype(series, 'timestamp')
    assert series.dtype == 'datetime64[ns]'


def test_try_series_retype_timestamp_error() -> None:
    series = pd.Series(['2023-11-12 09:15:32.23', None], dtype='str')

    with pytest.raises(TypeError):
        try_series_retype(series, 'timestamp')


def test_create_columns_from_df() -> None:
    # test with an empty dataframe
    df = pd.DataFrame()
    with pytest.raises(ValueError):
        create_columns_from_df(df)

    # test with a dataframe from dictionary
    df = pd.DataFrame(MODEL_DATA)

    df['Gender'] = df['Gender'].astype('category')
    df['Churned'] = df['Churned'].astype('category')

    model_schema = create_columns_from_df(df)
    columns = model_schema.columns
    assert len(columns) == 13
    assert columns[0].name == 'Unnamed: 0'
    assert columns[0].data_type == DataType.INTEGER

    assert columns[1].name == 'CreditScore'
    assert columns[1].data_type == DataType.INTEGER

    assert columns[2].name == 'Geography'
    assert columns[2].data_type == DataType.STRING

    assert columns[3].name == 'Gender'
    assert columns[3].data_type == DataType.CATEGORY

    assert columns[4].name == 'Age'
    assert columns[4].data_type == DataType.INTEGER

    assert columns[5].name == 'Tenure'
    assert columns[5].data_type == DataType.INTEGER

    assert columns[6].name == 'Balance'
    assert columns[6].data_type == DataType.FLOAT

    assert columns[7].name == 'NumOfProducts'
    assert columns[7].data_type == DataType.INTEGER

    assert columns[8].name == 'HasCrCard'
    assert columns[8].data_type == DataType.BOOLEAN

    assert columns[9].name == 'IsActiveMember'
    assert columns[9].data_type == DataType.BOOLEAN

    assert columns[10].name == 'EstimatedSalary'
    assert columns[10].data_type == DataType.FLOAT

    assert columns[11].name == 'Churned'
    assert columns[11].data_type == DataType.CATEGORY

    assert columns[12].name == 'probability_churned'
    assert columns[12].data_type == DataType.FLOAT

def test_numeric_type_casting():
    # Create a DataFrame with various integer types
    df = pd.DataFrame({
        'int8_col': pd.Series([1, 2, 3], dtype='int8'),
        'int16_col': pd.Series([1000, 2000, 3000], dtype='int16'),
        'int32_col': pd.Series([100000, 200000, 300000], dtype='int32'),
        'int64_col': pd.Series([10000000000, 20000000000, 30000000000], dtype='int64'),
        'uint8_col': pd.Series([1, 2, 3], dtype='uint8'),
        'uint16_col': pd.Series([1000, 2000, 3000], dtype='uint16'),
        'uint32_col': pd.Series([100000, 200000, 300000], dtype='uint32'),
        'uint64_col': pd.Series([10000000000, 20000000000, 30000000000], dtype='uint64'),

        # Float types
        'float16_col': pd.Series([1.0, 2.0, 3.0], dtype='float16'),
        'float32_col': pd.Series([1.234, 2.345, 3.456], dtype='float32'),
        'float64_col': pd.Series([1.23456789, 2.34567890, 3.45678901], dtype='float64'),

        # Control columns
        'string_col': pd.Series(['1', '2', '3'], dtype='string'),
        'bool_col': pd.Series([True, False, True], dtype='bool')
    })

    # Generate columns from DataFrame
    columns = create_columns_from_df(df).columns

    # Create a mapping of column names to their expected data types
    expected_types = {
        'int8_col': DataType.INTEGER,
        'int16_col': DataType.INTEGER,
        'int32_col': DataType.INTEGER,
        'int64_col': DataType.INTEGER,
        'uint8_col': DataType.INTEGER,
        'uint16_col': DataType.INTEGER,
        'uint32_col': DataType.INTEGER,
        'uint64_col': DataType.INTEGER,

        # Float columns
        'float16_col': DataType.FLOAT,
        'float32_col': DataType.FLOAT,
        'float64_col': DataType.FLOAT,

        # control columns
        'string_col': DataType.STRING,
        'bool_col': DataType.BOOLEAN
    }

    # Verify each column's data type
    for column in columns:
        assert column.data_type == expected_types[column.name], \
            f"Column {column.name} should be {expected_types[column.name]}, but got {column.data_type}"

    # Verify min and max values for numeric columns
    for col_name in df.select_dtypes(include=['int', 'float']).columns:
        col = next(c for c in columns if c.name == col_name)
        assert col.min == df[col_name].min(), \
            f"Min value mismatch for {col_name}: expected {df[col_name].min()}, got {col.min}"
        assert col.max == df[col_name].max(), \
            f"Max value mismatch for {col_name}: expected {df[col_name].max()}, got {col.max}"

def test_integer_edge_cases():
    # Test with empty DataFrame
    empty_df = pd.DataFrame({
        'int_col': pd.Series([], dtype='int64')
    })
    columns = create_columns_from_df(empty_df).columns
    assert len(columns) == 1
    assert columns[0].data_type == DataType.INTEGER

    # Test with NaN values
    df_with_nan = pd.DataFrame({
        'int_col': pd.Series([1, 2, np.nan], dtype='float64')  # NaN forces float dtype
    })
    columns = create_columns_from_df(df_with_nan).columns
    assert len(columns) == 1
    assert columns[0].data_type == DataType.FLOAT  # Should be float due to NaN

    # Test with mixed types
    df_mixed = pd.DataFrame({
        'mixed_col': pd.Series([1, '2', 3], dtype='object')
    })
    columns = create_columns_from_df(df_mixed).columns
    assert len(columns) == 1
    assert columns[0].data_type == DataType.STRING  # Should be string due to mixed types

def test_float_edge_cases():
    # Test with NaN values
    df_nan = pd.DataFrame({
        'float_nan': pd.Series([1.0, np.nan, 3.0], dtype='float64')
    })
    columns = create_columns_from_df(df_nan).columns
    assert len(columns) == 1
    assert columns[0].data_type == DataType.FLOAT
    assert columns[0].min == 1.0
    assert columns[0].max == 3.0

    # Test with infinity
    df_inf = pd.DataFrame({
        'float_inf': pd.Series([1.0, np.inf, -np.inf], dtype='float64')
    })
    columns = create_columns_from_df(df_inf).columns
    assert len(columns) == 1
    assert columns[0].data_type == DataType.FLOAT
    assert columns[0].min == -np.inf
    assert columns[0].max == np.inf

    # Test with very small numbers
    df_small = pd.DataFrame({
        'float_small': pd.Series([1e-10, 1e-20, 1e-30], dtype='float64')
    })
    columns = create_columns_from_df(df_small).columns
    assert len(columns) == 1
    assert columns[0].data_type == DataType.FLOAT
    assert columns[0].min == 1e-30
    assert columns[0].max == 1e-10

    # Test with very large numbers
    df_large = pd.DataFrame({
        'float_large': pd.Series([1e10, 1e20, 1e30], dtype='float64')
    })
    columns = create_columns_from_df(df_large).columns
    assert len(columns) == 1
    assert columns[0].data_type == DataType.FLOAT
    assert columns[0].min == 1e10
    assert columns[0].max == 1e30

def test_mixed_numeric_types():
    # Test with mixed integer and float values
    df_mixed = pd.DataFrame({
        'mixed_numeric': pd.Series([1, 2.0, 3], dtype='float64')
    })
    columns = create_columns_from_df(df_mixed).columns
    assert len(columns) == 1
    assert columns[0].data_type == DataType.FLOAT
    assert columns[0].min == 1.0
    assert columns[0].max == 3.0

    # Test with mixed numeric and string values
    df_mixed_str = pd.DataFrame({
        'mixed_str': pd.Series([1, '2.0', 3], dtype='object')
    })
    columns = create_columns_from_df(df_mixed_str).columns
    assert len(columns) == 1
    assert columns[0].data_type == DataType.STRING  # Should be string due to mixed types