from flask import Flask, jsonify, request
from flask_pymongo import PyMongo, MongoClient
from forecasts import create_arima
import pandas as pd
import numpy as np
import json
import os

app = Flask(__name__)

###### Database pathing
app.config['MONGO_DBNAME'] = 'flaskdb'
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/flaskdb'
app.config['MONGO_URI'] = ('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' +
  os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' +
  os.environ['MONGODB_DATABASE'])
mongo = PyMongo(app)

####### Search Inputs
#route to get frameworks
@app.route('/history', methods=['GET'])
def get_all_history():
    Sample = mongo.db.Sample

    # setting up first GET query
    history = []
    for q in Sample.find():
        history.append({'sample_number': q['sample_number'], "dates": q['dates']})
    return jsonify({'history': history})

#route to get frameworks
@app.route('/history/<sample>', methods=['GET'])
def get_one_history(sample):
    Sample = mongo.db.Sample

    q = Sample.find_one({'sample_number': sample})
    if q:
        output = {'sample_number': q['sample_number'], 'dates': q['dates']}
    else:
        output='No Results Found'
    return jsonify({'singel_sample': output})

######## Search Outputs
@app.route('/forecast', methods=['GET'])
def get_all_forecast():
    Forecast = mongo.db.Forecast
    
    # setting up second GET query
    forecast = []
    for q in Forecast.find():
        forecast.append({'sample_number': q['sample_number'], "dates": q['dates']})
    return jsonify({'forecast': forecast})

@app.route('/forecast/<sample>', methods=['GET'])
def get_one_forecast(sample):
    Forecast = mongo.db.Forecast

    q = Forecast.find_one({'sample_number': sample})
    if q:
        output = {'sample_number': q['sample_number'], 'dates': q['dates']}
    else:
        output = 'No Results Found'

    return jsonify({'singel_sample': output})



##### Forecast Predictions + Add Samples to table
@app.route('/sample', methods=['POST'])
def add_sample():
    Sample = mongo.db.Sample
    Forecast = mongo.db.Forecast

    sample = request.json['sample_number']
    dates = request.json['dates']
    components = request.json['components']

    sample_id = Sample.insert({'sample_number': sample, 'dates':dates, 'components': components})
    new_sample = Sample.find_one({'_id': sample_id})

    output = {'sample_number': new_sample['sample_number'], 
    'dates': new_sample['dates'], 'components' :new_sample['components']}


    ## Try to Calculate Forecast
    try: 
        pred_len = 5   ####  --------- Need to come up with something for this + dates entered as values
        dates_pred = (np.linspace(dates[-1]+1, dates[-1]+pred_len, pred_len))
        
        forecast_comp = []
        forecast_upper = []
        forecast_lower = []
        comp_names = []

        for i in components:
            for conc in i:
                comp_names.append(conc)
                label = conc
                mean, upper, lower = create_arima(i[conc], pred_len, label)
                forecast_comp.append(mean.tolist())
                forecast_upper.append(upper.tolist())
                forecast_lower.append(lower.tolist())
        
        df = pd.DataFrame({
        "components":comp_names,
        "forecast": forecast_comp,
        "forecast_upper": forecast_upper,
        "forecast_lower": forecast_lower
        })

        df_json = df.to_json(orient="records")
        df_parsed = json.loads(df_json)
        #forecast_json = json.dumps(df_parsed, indent=None)
        
        forecast_id = Forecast.insert({
                        "Sample_Table_ID":sample_id,
                        "sample_number": sample,
                        "forecast_dates": dates_pred.tolist(),
                        "forecast": df_parsed
                        })
        new_forecast = Forecast.find_one({'_id': forecast_id})
        pred_out_json = {'sample_number': new_forecast['sample_number'], 
                        'forecast_dates': new_forecast['forecast_dates'], 
                        'forecast' : new_forecast['forecast']}

    except:
        pred_out_json = {"prediction": "A Calculation Error Occured"}


    


    return jsonify({'Sample': output}, {'Forecast': pred_out_json})



if __name__ == '__main__':
#    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
#    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
#    app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
    app.run(host='0.0.0.0', debug=True)