
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import urllib
from sqlalchemy import create_engine

def sql_to_dataframe(table_name, server="localhost", database="NITYA DB", windows_auth=True, username=None, password=None):
    try:
        
        if windows_auth and not username:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"

        quoted_conn = urllib.parse.quote_plus(conn_str)
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quoted_conn}")
        query = f"SELECT * FROM {table_name}"
        return pd.read_sql(query, engine)
    except Exception as e:
        print(f"SQL Error: {e}")
        return None



def concat_dataframes(df1, df2, axis=0, **kwargs):
    
    if not isinstance(df1, pd.DataFrame):
        raise TypeError(f"df1 must be a pandas DataFrame, got {type(df1)}")
    if not isinstance(df2, pd.DataFrame):
        raise TypeError(f"df2 must be a pandas DataFrame, got {type(df2)}")
    
   
    if axis not in [0, 1]:
        raise ValueError(f"axis must be 0 or 1, got {axis}")
    
    
    df1_copy = df1.copy()
    df2_copy = df2.copy()
    

    if axis == 0:
        all_columns = set(df1_copy.columns) | set(df2_copy.columns)
        
        missing_in_df1 = all_columns - set(df1_copy.columns)

        for col in missing_in_df1:
            df1_copy[col] = np.nan
        
        missing_in_df2 = all_columns - set(df2_copy.columns)

        for col in missing_in_df2:
            df2_copy[col] = np.nan
    
        df1_cols = list(df1_copy.columns)
        df2_new_cols = [col for col in df2_copy.columns if col not in df1_cols]
        ordered_columns = df1_cols + df2_new_cols
        
        df1_copy = df1_copy[ordered_columns]
        df2_copy = df2_copy[ordered_columns]
        
        if 'join' not in kwargs:
            kwargs['join'] = 'outer'
    
   
    concatenated_df = pd.concat([df1_copy, df2_copy], axis=axis, **kwargs)
    
    return concatenated_df




def str_to_float(cell,unit):
    if type(cell) is str:
        s=cell.replace(unit,"")
        s = s.replace(',',"")
        s = s.strip()
        return float(s)




def preprocess_data(df):
    
    cleaned_df = df.copy()
    
    
    numeric_columns = cleaned_df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_columns:
        if cleaned_df[col].isnull().any():
            
            mean_value = cleaned_df[col].mean()
            if pd.notna(mean_value):
                cleaned_df[col].fillna(mean_value, inplace=True)
            else:
               
                cleaned_df[col].fillna(0, inplace=True)
    
    
    categorical_columns = cleaned_df.select_dtypes(include=['object', 'category', 'string']).columns
    

    for col in categorical_columns:
        if cleaned_df[col].isnull().any():

            mode_values = cleaned_df[col].mode()
            if len(mode_values) > 0:
                
                mode_value = mode_values[0]
                cleaned_df[col].fillna(mode_value, inplace=True)
            else:
                
                cleaned_df[col].fillna('', inplace=True)
    
    return cleaned_df




def train_model(df, flow_col='Actual_flow_volume_air_gas', pressure_col='Pressure_static', 
                target_col='Rated_power', test_size=0.2):
   
    df_cleaned = preprocess_data(df)
    
   
    X = df_cleaned[[flow_col, pressure_col]] 
    y = df_cleaned[target_col]              
    
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    
    # 4. Train the model
    model.fit(X, y)
    
    return model

def predict_power(model, flow_volume, static_pressure):
    
    input_features = [[flow_volume, static_pressure]]
    
   
    prediction = model.predict(input_features)
    
    
    return prediction[0]

def build_and_train_model(df, **kwargs):
   
    print("Building and training the fan power model...")
    model = train_model(df, **kwargs)
    print("Training complete.")
    
    return model

def recommend_manufacturer(df, predicted_power):
 
    df = preprocess_data(df)
    
    
    df['diff'] = (df['Rated_power'] - predicted_power).abs()
    

    closest_fans = df.nsmallest(5, 'diff')
    
   
    recommended = closest_fans['Manufacturer'].mode()[0]
    
    return recommended

def calculate_model_performance(model, df, flow_col='Actual_flow_volume_air_gas', 
                                 pressure_col='Pressure_static', target_col='Rated_power'):
  
    df = preprocess_data(df)
    X_test = df[[flow_col, pressure_col]]
    y_actual = df[target_col]
    
    
    y_predictions = model.predict(X_test)
    

    r2 = r2_score(y_actual, y_predictions)
    accuracy_pct = r2 * 100
    
    
    mse = mean_squared_error(y_actual, y_predictions)
    
   
    return {
        "accuracy_rate": accuracy_pct,
        "mean_square_error": mse
    }

#calling the data from the database
# df1=sql_to_dataframe("[dbo].[FAN_WITH_HOUSING_EXPORT (1)]")
# df2=sql_to_dataframe("[dbo].[FAN_WO_HOUSING_EXPORT (1)]")

# #concatenating the data from the database
# df=concat_dataframes(df1,df2)

# #converting the data to the correct format
# df["Actual_flow_volume_air_gas"] = df["Actual_flow_volume_air_gas"].apply(lambda x: str_to_float(x,'m3/h'))
# df["Pressure_static"] = df["Pressure_static"].apply(lambda x: str_to_float(x,'Pa'))
# df["Rated_power"] = df["Rated_power"].apply(lambda x: str_to_float(x,'kW'))

# #preprocessing the data (removing the null values)
# df = preprocess_data(df)
# df = df[["Actual_flow_volume_air_gas","Pressure_static","Rated_power","Manufacturer"]]

# #building and training the model
# my_model = build_and_train_model(df)

# #test data for the model
# test_flow = 20000
# test_pressure = 1650


# #predicting the power
# predicted_p = predict_power(my_model, test_flow, test_pressure)

# #recommending the manufacturer
# suggested_vendor = recommend_manufacturer(df, predicted_p)

# #calculating the model performance
# performance = calculate_model_performance(my_model, df)

# package = {
#     'model': 'fan recomendation.py',
#     'sql_to_dataframe': sql_to_dataframe,
#     'concat_dataframes':concat_dataframes,
#     'preprocess_data':preprocess_data,
#     'str_to_float': str_to_float,
#     'build_and_train_model':build_and_train_model,
#     'predict_power':predict_power,
#     'recommend_manufacturer':recommend_manufacturer,
#     'calculate_model_performance':calculate_model_performance

# }

# dump(package, 'fan_power_model.joblib')

# dump(my_model, 'fan_power_model.joblib')

# print("Model saved as fan_power_model.joblib")

#printing the model performance
# print(f"--- Model Performance Report ---")
# print(f"Accuracy Rate: {performance['accuracy_rate']:.2f}%")
# print(f"Mean Square Error: {performance['mean_square_error']:.2f}")



# #printing the test results
# print("\n" + "="*30)
# print("TEST RESULTS")
# print("="*30)
# print(f"Input Flow:     {test_flow}")
# print(f"Input Pressure: {test_pressure}")
# print(f"---")
# print(f"Predicted Power: {predicted_p:.2f} kW")
# print(f"Recommended Brand: {suggested_vendor}")
# print("="*30)