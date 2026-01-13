from flask import Flask, render_template, jsonify, request
import fan_recomendation as f
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_logic():
    input_data = request.json
    # These MUST match the keys in your JavaScript
    test_flow = input_data.get('flow')
    test_pressure = input_data.get('pressure')

    print(f'Predicting for: Flow={test_flow}, Pressure={test_pressure}')

    # Data Processing
    df1 = f.sql_to_dataframe("[dbo].[FAN_WITH_HOUSING_EXPORT (1)]")
    df2 = f.sql_to_dataframe("[dbo].[FAN_WO_HOUSING_EXPORT (1)]")
    df = f.concat_dataframes(df1, df2)

    df["Actual_flow_volume_air_gas"] = df["Actual_flow_volume_air_gas"].apply(lambda x: f.str_to_float(x, 'm3/h'))
    df["Pressure_static"] = df["Pressure_static"].apply(lambda x: f.str_to_float(x, 'Pa'))
    df["Rated_power"] = df["Rated_power"].apply(lambda x: f.str_to_float(x, 'kW'))

    df = f.preprocess_data(df)
    df = df[["Actual_flow_volume_air_gas", "Pressure_static", "Rated_power", "Manufacturer"]]

    # Model Logic
    my_model = f.build_and_train_model(df)
    
    clean_flow = f.str_to_float(test_flow, 'm3/h')
    clean_press = f.str_to_float(test_pressure, 'Pa')
    
    predicted_p = f.predict_power(my_model, clean_flow, clean_press)
    suggested_vendor = f.recommend_manufacturer(df, predicted_p)

    return jsonify({
        "status": "success",
        "flowVolume":input_data.get('flow'),
        "staticPressure":input_data.get('pressure'),
        "prediction": round(float(predicted_p), 2),
        "recommended_vendor": suggested_vendor
    })

if __name__ == '__main__':
    app.run(debug=True)