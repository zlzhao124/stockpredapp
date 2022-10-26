

import yfinance as yf
import numpy as np
import datetime
from tensorflow.keras.models import model_from_json

def get_target(cur_avg, next_avg, threshold=0.05):
    abs_price_change = abs(next_avg-cur_avg)*100/cur_avg
    if abs_price_change <= threshold:
        target = 2   # price change is less than threshold (percent) --> neutral target
    elif next_avg > cur_avg:
        target = 1
    else:
        target = 0 
    return target


def transform_data_from_ticker(ticker, START_DATE, END_DATE, RAW_INTERVAL, EVAL_RANGE, PREDICT_RANGE, NO_CHANGE_THRESHOLD):
    tickerData = yf.Ticker(ticker)
    df = tickerData.history(interval=RAW_INTERVAL,  start=START_DATE, end=END_DATE)
    
    if df.shape[0] > 0:
        first_row = df.iloc[0].values
        if first_row[0] < 10:
            print('Penny Stock. Skip!')
            return None
    else:
        return None
    
    cur_data = []
    cur_targets = []
    # each day corresponds to a time series of EVAL_RANGE elemetns
    first_run = True
    for current_day in range(EVAL_RANGE-1, df.shape[0]-PREDICT_RANGE): # such that past EVAL_RANGE and future PREDICT_RANGE are available 
        if first_run:   # first run for this sub_df
            time_series = [None]*EVAL_RANGE
            time_series_targets = [None]*EVAL_RANGE
            first_run = False
            for past_day in range(0, EVAL_RANGE): # e.g: from 0 -> 9 
                past_day_ix = current_day - (EVAL_RANGE-1) + past_day # Go from the oldest day to the current day 
                past_day_data = df.iloc[past_day_ix][['Open', 'High', 'Low', 'Close', 'Volume']].values
                time_series[past_day] = past_day_data
                
                cur_avg = (df.iloc[past_day_ix]['Open'] + df.iloc[past_day_ix]['Close']) / 2
                next_avg = (df.iloc[past_day_ix+1]['Open'] + df.iloc[past_day_ix+1]['Close']) / 2
                
                target = get_target(cur_avg, next_avg, threshold=NO_CHANGE_THRESHOLD)
                time_series_targets[past_day] = target
                
            time_series = np.array(time_series)
            time_series_targets = np.array(time_series_targets)

        else:   # reuse 9 days from last instance
            cur_data_ix = current_day - (EVAL_RANGE-1)
            time_series = cur_data[cur_data_ix-1][1:]
            time_series_targets = cur_targets[cur_data_ix-1][1:]
            
            cur_day_data = df.iloc[current_day][['Open', 'High', 'Low', 'Close', 'Volume']].values
            cur_avg = (df.iloc[current_day]['Open'] + df.iloc[current_day]['Close']) / 2
            next_avg = (df.iloc[current_day+1]['Open'] + df.iloc[current_day+1]['Close']) / 2
            target = get_target(cur_avg, next_avg, threshold=NO_CHANGE_THRESHOLD)
            
            time_series = np.concatenate((time_series, cur_day_data.reshape(1,len(cur_day_data))))
            time_series_targets = np.append(time_series_targets, target)
            
        cur_data.append(time_series)
        cur_targets.append(time_series_targets)
        
    cur_data = np.array(cur_data)
    cur_targets = np.array(cur_targets)
    
    data_means = cur_data.mean(axis=0)
    data_stds = cur_data.std(axis=0)
    cur_data_scaled = (cur_data - data_means)/data_stds
    # cur_data_scaled = cur_data / np.max(cur_data, axis=0)
    
    return cur_data_scaled, cur_targets

# def extract_last_step_labels(y_pred): # y_pred: output matrix of RNN. Output: 1D matrix of last step predictions
#     return np.array([np.argmax(pred[-1]) for pred in y_pred])

def get_last_step_predictions(model, X): # X: an input Tensor to RNN. Output: 1D matrix of last step predictions
    y_pred = model.predict(X)
    return np.array([np.argmax(pred[-1]) for pred in y_pred])
 

def evaluate(model, X, y_true, binary=False):
    from sklearn.metrics import precision_score, recall_score
    y_pred = get_last_step_predictions(model, X)
    y_true = y_true[:, -1] # last step only
    acc = sum(y_pred==y_true)/y_true.shape[0]
    if not binary:
        for i in range(len(y_true)):
            y_pred[i] = y_pred[i] if y_pred[i] != 2 else 0 
            y_true[i] = y_true[i] if y_true[i] != 2 else 0 
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    print('Accuracy: {}'.format(acc))
    print('Precision: {}'.format(precision))
    print('Recall: {}'.format(recall))
    

def evaluate_on_ticker(model, ticker):
    EVAL_RANGE = 30
    PREDICT_RANGE = 1
    START_DATE = '2020-7-30'
    END_DATE = '2020-8-2'
    RAW_INTERVAL = "15m"
    NO_CHANGE_THRESHOLD = 0.1 # percentage of ticker's price
    transformed_data = transform_data_from_ticker(ticker, START_DATE, END_DATE, EVAL_RANGE, PREDICT_RANGE, NO_CHANGE_THRESHOLD)
    if transformed_data != None:
        cur_data, cur_targets = transformed_data
        print(cur_data.shape)
        y_p = model.predict(cur_data)
        evaluate(model, cur_targets, y_p, binary=False)
    else:
        print('Ticker not available or is penny stock')

    


    
    
    
    