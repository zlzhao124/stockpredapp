

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
from functions import get_target, transform_data_from_ticker

num_tickers = 100
tickers_csv = pd.read_csv('tickers.csv')['Electronic Technology'].values
tickers= tickers_csv[:num_tickers]

EVAL_RANGE = 24
PREDICT_RANGE = 4
START_DATE = '2022-4-1'
END_DATE = '2022-4-22'
RAW_INTERVAL = "15m" # Interval to retrieve data from YFinance (can be 15m, 1h, 1d, etc.)
NO_CHANGE_THRESHOLD = 0.1 # percentage of ticker's price
TRAIN_RATIO = 0.90

train_data = []
train_targets = []
test_data = []
test_targets = []

ticker_no = 1
for ticker in tickers:          
    print('Working on ticker {}/{}'.format(ticker_no, num_tickers))
    ticker_no += 1
    
    transformed_data = transform_data_from_ticker(ticker, START_DATE, END_DATE, RAW_INTERVAL, EVAL_RANGE, PREDICT_RANGE, NO_CHANGE_THRESHOLD)
    if transformed_data != None:
        ticker_data, ticker_targets = transformed_data
        train_test_split_idx = int(ticker_data.shape[0]*TRAIN_RATIO)
        train_ticker_data, train_ticker_targets = ticker_data[:train_test_split_idx], ticker_targets[:train_test_split_idx]
        test_ticker_data, test_ticker_targets = ticker_data[train_test_split_idx:], ticker_targets[train_test_split_idx:]
    else:
        continue     # penny stock or missing stock 
    
    if len(train_data) == 0:
        train_data = train_ticker_data
        train_targets = train_ticker_targets
        test_data = test_ticker_data
        test_targets = test_ticker_targets
    else:
        train_data = np.concatenate((train_data, train_ticker_data), axis=0)
        train_targets = np.concatenate((train_targets, train_ticker_targets), axis=0)
        test_data = np.concatenate((test_data, test_ticker_data), axis=0)
        test_targets = np.concatenate((test_targets, test_ticker_targets), axis=0)

np.save('train_data.npy', train_data)
np.save('train_targets.npy', train_targets)
np.save('test_data.npy', test_data)
np.save('test_targets.npy', test_targets)



        
    

        
        

    
        




