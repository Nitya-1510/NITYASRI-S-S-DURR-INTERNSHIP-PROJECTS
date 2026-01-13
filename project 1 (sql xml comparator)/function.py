import pandas as pd
import urllib
from sqlalchemy import create_engine
import xml.etree.ElementTree as ET
import os
import uuid
import json
from flask import Flask, render_template, jsonify, request, url_for

app = Flask(__name__)

# Directory to store the large data temporarily on the server
TEMP_DIR = 'temp_data'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


# --- YOUR ORIGINAL FUNCTIONS (UNCHANGED) ---
def process_column(df, source_col='value_key'):
    ts_strings = df[source_col].astype(str).str.zfill(7)
    date_objs = pd.to_datetime(ts_strings, format='%y%j%H', errors='coerce')
    formatted_dates = date_objs.dt.strftime('%d-%m-%Y')
    if 'formatted_date' not in df.columns:
        df.insert(0, 'formatted_date', formatted_dates)
    return df


def sql_to_dataframe(server, database, table_name, windows_auth=True, username=None, password=None):
    try:
        # Use Windows Auth if no username is provided, otherwise SQL Auth
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


def xml_to_dataframe(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        all_rows = []
        for parent in root.findall(".//"):
            row_data = {}
            for node in parent.iter():
                if node.text and node.text.strip() and not list(node):
                    row_data[node.tag] = node.text.strip()
                if node.attrib:
                    row_data.update(node.attrib)
            if row_data:
                all_rows.append(row_data)
        return pd.DataFrame(all_rows).drop_duplicates().reset_index(drop=True)
    except Exception as e:
        print(f"XML Error: {e}")
        return None


def merge_sql_and_xml(df_sql, df_xml):
    try:
        df_sql['value_id'] = df_sql['value_id'].astype(str)
        df_xml['id'] = df_xml['id'].astype(str)
        merged_df = pd.merge(df_sql, df_xml, left_on='value_id', right_on='id', how='inner')
        cols = ['value_key', 'value_id', 'value_number', 'value_summary', 'areakey', 'medium', 'unit']
        return merged_df[cols]
    except Exception as e:
        print(f"Merge Error: {e}")
        return None


# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/connect', methods=['POST'])
def create_df():
    data = request.json

    # Passing all 5 parameters to your original functions
    sql_df = sql_to_dataframe(
        server=data['server_val'],
        database=data['db_name'],
        table_name='dbo.DS_CounterDataValueBlockMain_TAB',
        windows_auth=False if data.get('username') else True,
        username=data.get('username'),
        password=data.get('password')
    )

    xml_df = xml_to_dataframe(data['xml_path'].replace('\\', '/'))

    if sql_df is not None and xml_df is not None:
        result = merge_sql_and_xml(sql_df, xml_df)
        final = process_column(result)

        # Save to temporary file to avoid "Cookie too large" error
        data_id = str(uuid.uuid4())
        file_path = os.path.join(TEMP_DIR, f"{data_id}.json")
        final.to_json(file_path, orient='records')

        return jsonify({"redirect_url": url_for('results_page', data_id=data_id)})

    return jsonify({"error": "Failed to process database or XML"}), 400


@app.route('/results')
def results_page():
    data_id = request.args.get('data_id')
    file_path = os.path.join(TEMP_DIR, f"{data_id}.json")

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            table_data = json.load(f)
        return render_template('results.html', data=table_data)
    return "Data not found or expired.", 404


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)