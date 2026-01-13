import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def preprocess_data(df):
    # Create a copy to avoid modifying the original DataFrame
    cleaned_df = df.copy()
    
    # Identify numeric columns (int64, float64, etc.)
    numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
    
    # Fill numeric null values with mean
    for col in numeric_columns:
        if cleaned_df[col].isnull().any():
            # Calculate mean, handling cases where all values might be null
            mean_value = cleaned_df[col].mean()
            if pd.notna(mean_value):
                cleaned_df[col].fillna(mean_value, inplace=True)
            else:
                # If all values are null, fill with 0 as fallback
                cleaned_df[col].fillna(0, inplace=True)
    
    # Identify categorical columns (object, category, string, etc.)
    categorical_columns = cleaned_df.select_dtypes(include=['object', 'category', 'string']).columns
    
    # Fill categorical null values with mode
    for col in categorical_columns:
        if cleaned_df[col].isnull().any():
            # Get mode (most frequent value)
            mode_values = cleaned_df[col].mode()
            if len(mode_values) > 0:
                # Use first mode value if multiple modes exist
                mode_value = mode_values[0]
                cleaned_df[col].fillna(mode_value, inplace=True)
            else:
                # If no mode exists (all values are null), fill with empty string
                cleaned_df[col].fillna('', inplace=True)
    
    return cleaned_df


# Sample DataFrame for testing
sample_df = pd.DataFrame({
    'actual_flow_volume': [1000, 1500, None, 2000, 1800, None, 2200, 1600],
    'pressure_static': [50, None, 75, 60, None, 80, 65, 55],
    'rated_power': [10.5, 15.2, 20.0, None, 18.5, 22.3, 16.8, None],
    'fan_type': ['Centrifugal', 'Axial', None, 'Centrifugal', 'Axial', None, 'Centrifugal', 'Axial'],
    'efficiency': [85, 90, None, 88, 92, 87, None, 89],
    'manufacturer': ['Brand A', None, 'Brand B', 'Brand A', 'Brand B', None, 'Brand A', None],
    'rpm': [1500, None, 1800, 1600, 1700, None, 1550, 1650]
})

# print("Original DataFrame:")
# print(sample_df)
# print("\nNull values count:")
# print(sample_df.isnull().sum())
# print("\n" + "="*60)

# # Test the preprocess_data function
# cleaned_sample = preprocess_data(sample_df)

# print("\nCleaned DataFrame:")
# print(cleaned_sample)
# print("\nNull values count after preprocessing:")
# print(cleaned_sample.isnull().sum())

def concat_dataframes(df1, df2, axis=0, **kwargs):
    """
    Concatenates two DataFrames using pandas concat function.
    If DataFrames have different columns (when axis=0), missing columns
    are added as additional columns with NaN/null values.
    
    Parameters:
    -----------
    df1 : pandas.DataFrame
        First DataFrame to concatenate
    df2 : pandas.DataFrame
        Second DataFrame to concatenate
    axis : int, default 0
        Axis along which to concatenate
        - 0: concatenate vertically (stack rows)
          If columns differ, missing columns are added with NaN values
        - 1: concatenate horizontally (stack columns)
    **kwargs : additional keyword arguments
        Additional arguments passed to pd.concat():
        - ignore_index : bool, default False
            If True, the resulting axis will be labeled 0, 1, ..., n-1
        - join : {'inner', 'outer'}, default 'outer'
            How to handle indexes on other axis when axis=1
        - sort : bool, default False
            Sort non-concatenation axis if it is not already aligned
        - keys : sequence, default None
            Keys to associate with the values
        - etc. (all pandas concat parameters)
    
    Returns:
    --------
    pandas.DataFrame
        Concatenated DataFrame with all columns from both DataFrames
    
    Examples:
    ---------
    # Vertical concatenation (default) - different columns will be added
    result = concat_dataframes(df1, df2, axis=0, ignore_index=True)
    
    # Horizontal concatenation
    result = concat_dataframes(df1, df2, axis=1, join='inner')
    """
    # Validate inputs are DataFrames
    if not isinstance(df1, pd.DataFrame):
        raise TypeError(f"df1 must be a pandas DataFrame, got {type(df1)}")
    if not isinstance(df2, pd.DataFrame):
        raise TypeError(f"df2 must be a pandas DataFrame, got {type(df2)}")
    
    # Validate axis parameter
    if axis not in [0, 1]:
        raise ValueError(f"axis must be 0 or 1, got {axis}")
    
    # Create copies to avoid modifying original DataFrames
    df1_copy = df1.copy()
    df2_copy = df2.copy()
    
    # For vertical concatenation (axis=0), ensure both DataFrames have all columns
    if axis == 0:
        # Get all unique columns from both DataFrames
        all_columns = set(df1_copy.columns) | set(df2_copy.columns)
        
        # Add missing columns to df1_copy with NaN values
        missing_in_df1 = all_columns - set(df1_copy.columns)
        for col in missing_in_df1:
            df1_copy[col] = np.nan
        
        # Add missing columns to df2_copy with NaN values
        missing_in_df2 = all_columns - set(df2_copy.columns)
        for col in missing_in_df2:
            df2_copy[col] = np.nan
        
        # Ensure columns are in the same order (sort for consistency)
        # But preserve the order: first df1's columns, then new columns from df2
        df1_cols = list(df1_copy.columns)
        df2_new_cols = [col for col in df2_copy.columns if col not in df1_cols]
        ordered_columns = df1_cols + df2_new_cols
        
        # Reorder columns in both DataFrames
        df1_copy = df1_copy[ordered_columns]
        df2_copy = df2_copy[ordered_columns]
        
        # Set default join='outer' if not specified in kwargs for consistency
        if 'join' not in kwargs:
            kwargs['join'] = 'outer'
    
    # Perform concatenation
    concatenated_df = pd.concat([df1_copy, df2_copy], axis=axis, **kwargs)
    
    return concatenated_df


# Test concat_dataframes function with 2 sample DataFrames

# DataFrame 1 - has columns: actual_flow_volume, pressure_static, rated_power, fan_type
df1 = pd.DataFrame({
    'actual_flow_volume': [1000, 1500, 2000, 1800],
    'pressure_static': [50, 75, 60, 80],
    'rated_power': [10.5, 15.2, 20.0, 18.5],
    'fan_type': ['Centrifugal', 'Axial', 'Centrifugal', 'Axial']
})

# DataFrame 2 - has columns: actual_flow_volume, rated_power, efficiency, manufacturer
# Note: Different columns than df1 (missing pressure_static and fan_type, but has efficiency and manufacturer)
df2 = pd.DataFrame({
    'actual_flow_volume': [2200, 1600, 1900],
    'rated_power': [22.3, 16.8, 19.2],
    'efficiency': [92, 88, 90],
    'manufacturer': ['Brand A', 'Brand B', 'Brand A']
})

print("\n" + "="*70)
print("TESTING concat_dataframes FUNCTION")
print("="*70)

print("\nDATAFRAME 1:")
print(df1)
print(f"Columns: {list(df1.columns)}")

print("\nDATAFRAME 2:")
print(df2)
print(f"Columns: {list(df2.columns)}")

print("\n" + "="*70)
print("CONCATENATED RESULT (Vertical - axis=0):")
print("="*70)
result = concat_dataframes(df1, df2, axis=0, ignore_index=True)
print(result)
print(f"\nResult columns: {list(result.columns)}")
print("\nNote: Missing columns are added with NaN values")