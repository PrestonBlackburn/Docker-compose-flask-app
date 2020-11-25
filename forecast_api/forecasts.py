import pmdarima as pm
import pandas as pd
import numpy as np
from datetime import datetime



def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

def create_arima(data, pred_period, label):
    model = pm.auto_arima(data, start_p=1, start_q=1,
                      test='adf',       # use adftest to find optimal 'd'
                      max_p=1, max_q=1, # maximum p and q
                      m=1,              # frequency of series
                      d = 0,            # Assume data is stationary - It should be in most cases
                      #d=None,           # let model determine 'd'
                      seasonal=False,   # No Seasonality
                      start_P=0, 
                      D=0, 
                      trace=False,    # turn trace on to see itterations
                      error_action='ignore',  
                      suppress_warnings=True, 
                      stepwise=True)
    # Forecast
    fc, confint = model.predict(n_periods=pred_period, return_conf_int=True)
    index_of_fc = np.arange(len(data), len(data)+pred_period)

    # make series for plotting purpose
    fc_series = pd.Series(fc, index=index_of_fc)
    lower_series = pd.Series(confint[:, 0], index=index_of_fc)
    upper_series = pd.Series(confint[:, 1], index=index_of_fc)

    # Plot

#    plt.plot(data)
#    plt.plot(fc_series, color='#0277BD', linestyle='--')
#    plt.fill_between(lower_series.index, 
#                     lower_series, 
#                     upper_series, 
#                     color="#33a6cc", alpha=.15)

#    plt.title(f"Prediction for {label}")
#    plt.show()
    
    return fc_series.values, upper_series.values, lower_series.values
