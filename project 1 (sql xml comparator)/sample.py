import pandas as pd
import urllib
from sqlalchemy import create_engine
import xml.etree.ElementTree as ET

#converts value to date such as "2321800" to "Aug 06,23"
def convert_date(ts_value):

    ts_str = str(ts_value).zfill(7)

    try:
        # %y = 2-digit Year, %j = Day of year (001-366), %H = Hour
        dt = pd.to_datetime(ts_str, format='%y%j%H')

        # %d = Day, %m = Month, %Y = 4-digit Year
        return dt.strftime('%d-%m-%Y')
    except Exception as e:
        return f"Error: {e}"

# print(convert_custom_timestamp("2321800"))


# def process_column(df, source_col='value_key'):
    # date_data = df[source_col].apply(convert_date)

    # if 'formatted_date' not in df.columns:
    #     df.insert(0, 'formatted_date', date_data)
    # return df
def process_column(df, source_col='value_key'):
    # 1. Convert to string and pad with zeros (Vectorized)
    # This is much faster than zfill in a loop
    ts_strings = df[source_col].astype(str).str.zfill(7)

    # 2. Convert the entire series to datetime at once
    # 'coerce' handles errors by returning NaT (Not a Time) instead of crashing
    date_objs = pd.to_datetime(ts_strings, format='%y%j%H', errors='coerce')

    # 3. Format the dates (Vectorized)
    # If it's NaT (an error), it will remain empty or null
    formatted_dates = date_objs.dt.strftime('%d-%m-%Y')

    # 4. Insert into DataFrame
    if 'formatted_date' not in df.columns:
        df.insert(0, 'formatted_date', formatted_dates)

    return df
#comment from here

def sql_to_dataframe(server, database, table_name, windows_auth=True, username=None, password=None):
    try:
        #connection using Windows auth , SQL auth
        if windows_auth:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};"
        # quoting the connection string , preparing the engine to run it
        quoted_conn = urllib.parse.quote_plus(conn_str)
        engine = create_engine(f"mssql+pyodbc:///?odbc_connect={quoted_conn}")
        # writing the query to select the table and making it into the dataframe
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, engine)
        return df #returning the df

    except Exception as e:
        print(f"Error: {e}")
        return None


sql_df = sql_to_dataframe(
  server='localhost',
     database='NITYA DB',
    table_name='dbo.DS_CounterDataValueBlockMain_TAB')

def xml_to_dataframe(file_path):
    try:
        # 1. Load the file
        tree = ET.parse(file_path)
        root = tree.getroot()

        all_rows = []

        # 2. Find every tag that has text but no "children" tags
        # We assume each "branch" of the tree might be a row
        for parent in root.findall(".//"):
            row_data = {}
            # Look at everything inside this parent
            for node in parent.iter():
                # If it's a leaf node (has text and no kids)
                if node.text and node.text.strip() and not list(node):
                    row_data[node.tag] = node.text.strip()

                # ALSO grab attributes (like id="123")
                if node.attrib:
                    row_data.update(node.attrib)

            if row_data:
                all_rows.append(row_data)

        # 3. Create DataFrame and remove exact duplicates
        df = pd.DataFrame(all_rows).drop_duplicates().reset_index(drop=True)

        if df.empty:
            print("Still empty. The XML might be structured in a very unusual way.")
        else:
            print(f"Success! Found {len(df)} potential rows.")

        return df

    except Exception as e:
        print(f"Error: {e}")
        return None

path=r"C:\Users\Delll\OneDrive\Desktop\durr internship project\gapConfig.xml"
xml_df = xml_to_dataframe(path)

def merge_sql_and_xml(df_sql, df_xml):

    try:

        df_sql['value_id'] = df_sql['value_id'].astype(str)
        df_xml['id'] = df_xml['id'].astype(str)

        merged_df = pd.merge(
            df_sql,
            df_xml,
            left_on='value_id',
            right_on='id',
            how='inner'
        )
        specific_columns = [
            'value_key', 'value_id', 'value_number', 'value_summary',
            'areakey', 'medium', 'unit'
        ]

        final_df = merged_df[specific_columns]

        print(f"Match successful! Created a table with {len(final_df)} rows.")
        return final_df

    except KeyError as e:
        print(f"Error: One of the columns was not found: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

result=merge_sql_and_xml(sql_df,xml_df)
final=process_column(result)

def save_to_csv(df, filename="results.csv"):
    """
    Saves the DataFrame to a plain CSV file.
    """
    # index=False ensures you don't get an extra column for row numbers
    df.drop('value_key', axis=1, inplace=True)
    df.to_csv(filename, index=False)
    print(f"Successfully saved to {filename}")

save_to_csv(final, "Internship_Data2.csv")


