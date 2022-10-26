# -*- coding: utf-8 -*-
import yfinance as yf
import numpy as np
import datetime
from tensorflow.keras.models import model_from_json

'''
 TrendPredictor is a class which makes it easy to make trend predictions on stocks
 in real time.
'''


class TrendPredictor():
    def __init__(self, ticker=None):
        self.model = self.load_model()
        self.ticker = ticker
        self.EVAL_RANGE = 24     # has to match trained model
        self.PREDICT_RANGE = 4   # has to match trained model 
    
    def set_ticker(self, ticker):
        self.ticker = ticker
        
    def load_model(self):
        '''
        Load model structure from json file, and weights from h5 file
        Return TensorFlow model ready to be used
        '''
        model_file = open('group_code/NeuralNetwork/trained_model/model.json', 'r')
        model_json = model_file.read()
        model_file.close()
        loaded_model = model_from_json(model_json)
        loaded_model.load_weights("group_code/NeuralNetwork/trained_model/weights.h5")
        return loaded_model
    
    
    def getTickerData(self):
        '''
        Get the [Open,Close,High,Low,Volume] data of the chosen ticker from the past 
        EVAL_RANGE time units --> scale the data, then return it
        '''
        # check if ticker was chosen
        if self.ticker == None:
            print("A ticker must be selected first!")
            return
        # get current time and date
        today = datetime.date.today()
        last_past_day = today - datetime.timedelta(days=self.EVAL_RANGE)
        furthest_past_day = today - datetime.timedelta(days=59) # YFinance only offers 15m data for the past 60 days
        
        # get 15m data in the last 2 months to calculate mean & std for normalization
        all_past_data = yf.Ticker(self.ticker).history(interval='15m', start=furthest_past_day, end=today)
        all_past_data = all_past_data[all_past_data.columns[:-2]].values # only care about Open,Close,High,Low,Volume data
        means = all_past_data.mean(axis=0)
        stds = all_past_data.std(axis=0)
        
        # get past data from EVAL_RANGE time units from the past to current time
        df = yf.Ticker(self.ticker).history(interval='15m', start=last_past_day, end=today)
        df = df[df.columns[:-2]] # don't need dividend and stock split columns (these are mainly just 0s)
        num_rows = df.shape[0]
        data = df.iloc[num_rows-self.EVAL_RANGE:num_rows].values # we only want data of the last EVAL_RANGE time units (until the current time)
        scaled_data = (data-means)/stds
        
        return scaled_data
    
    
    def predict(self):
        '''
        Use trained model to predict the trend of a stock in the next PREDICT_RANGE time units
        in the future (using data of the current time and EVAL_RANGE time units in the past)
        Output: Predictions on whether the price will increase/decrease/stay the same with confidence percentages. 
        '''
        data = self.getTickerData()
        data = np.expand_dims(data, axis=0) # this is a single sample, so must extend dimension before passing to the RNN model
        pred = self.model.predict(data)[0][-1] # only last time step matters
        
        print("In the next 2 trading hours, the price of {} is expected to:".format(self.ticker))
        print("\t - Increase with: {:.2f}% confidence".format(pred[1]*100))
        print("\t - Decrease with: {:.2f}% confidence".format(pred[0]*100))
        print("\t - Stay the same with: {:.2f}% confidence".format(pred[2]*100))
        print("\t   (Note: stay the same means the change is < 0.1% of the last price)")
        
        return pred
        
        
    