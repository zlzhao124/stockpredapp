#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, flash, request, redirect, url_for, jsonify, \
    render_template, Response

# hoang's imports

from group_code.TradingStyles.dash_app import get_dash_app
from group_code.NeuralNetwork.Predictor import TrendPredictor

# john's imports
from posixpath import split
from textwrap import indent
from cProfile import label
import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import copy
import matplotlib.pyplot as plt
import json

#andrew and zach's imports
import tweepy
import os
from group_code.SentimentAnalysis import cleanseTweets, sentimentAnalyze, scrapeTweets
import plotly
import plotly.express as px
from dotenv import load_dotenv
load_dotenv()

def scrapeAndCleanse(nameOfStock):#Cleanse repeated tweets and retweets
    searchHashtagWord = '#'+nameOfStock
    numTweetsToPull = 250
    dateFrom = "2021-01-01"

    #Scrape the tweets using the provided hashtag
    twitter_df= scrapeTweets.twitterScraper(searchHashtagWord, numTweetsToPull, dateFrom)
    
    #Cleanse Tweets
    cleansedDataFrame = cleanseTweets.cleanse(twitter_df)
    
    #Run Sentiment Analysis on the Tweets
    sentimentDataFrame = sentimentAnalyze.analyze(cleansedDataFrame) 
    
    return sentimentDataFrame 
    
def adjustSentimentDataFrame(raw_df, company):
    raw_df = raw_df[['date', 'sentiment', 'compound']]
    
    new_df = pd.DataFrame({
        'Company': [],
        'Date': [],
        'Count Type': [],
        'Count': [],
        'Compound Average': []
    })
    dates = raw_df['date'].drop_duplicates().tolist()
    
    for date in dates:
        temp = raw_df[raw_df['date']==date]
        
        entry = {'Company': company, 'Date': date, 'Count Type': 'Positive', 'Count': temp['sentiment'].value_counts()['positive'], 'Compound Average': temp['compound'].mean()}
        new_df = new_df.append(entry, ignore_index = True)
        entry = {'Company': company, 'Date': date, 'Count Type': 'Negative', 'Count': temp['sentiment'].value_counts()['negative'], 'Compound Average': temp['compound'].mean()}
        new_df= new_df.append(entry, ignore_index = True)
    return new_df


app = Flask(__name__)

# initialize trend predictor
trend_predictor = TrendPredictor() 

# intialize dash app
dash_app = get_dash_app(app)

@app.route('/')
def index():
    return render_template('README.html')

@app.route('/trend_prediction', methods=['GET', 'POST'])
def trend_prediction():
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        trend_predictor.set_ticker(ticker)
        (decrease, increase, same) = trend_predictor.predict()
        increase = '{:.2f}'.format(increase * 100)
        decrease = '{:.2f}'.format(decrease * 100)
        same = '{:.2f}'.format(same * 100)
        result = {
            'ticker': ticker,
            'increase_confidence': increase,
            'decrease_confidence': decrease,
            'same_confidence': same,
            }
        return render_template('trend_prediction.html', result=result)

    return render_template('trend_prediction.html', result=False)


@app.route('/Andrew')
def andrew():
    return render_template('andrew.html', graphJSON=positiveNegativeCallBackTest())

@app.route('/positiveNegativeCallBackTest', methods=['POST', 'GET'])
def cb1():
    return positiveNegativeCallBackTest(request.args.get('data'))

def positiveNegativeCallBackTest(company = 'Tesla'):
    if (company == "test"):
        company = 'Game Stop'
        sentiment_df = pd.read_csv('group_code/SentimentAnalysis/sentiment_df.csv')
        sentiment_df = adjustSentimentDataFrame(sentiment_df, company)
        
        sentimentTitle = "Overall Twitter Sentiment for {companyName} by Date".format(companyName = company)
        fig = px.bar(sentiment_df[sentiment_df['Company']==company], x='Date', y='Count', color='Count Type', barmode='group',  title=sentimentTitle)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
    
    else:
        sentiment_df = scrapeAndCleanse(company)
        sentiment_df = adjustSentimentDataFrame(sentiment_df,company)
        
        sentimentTitle = "Overall Twitter Sentiment for {companyName} by Date".format(companyName = company)
        fig = px.bar(sentiment_df[sentiment_df['Company']==company], x='Date', y='Count', color='Count Type', barmode='group',  title=sentimentTitle)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON

@app.route('/Zach')
def zach():
    return render_template('zach.html', graphJSON=compoundSentimentCallBackTest())

@app.route('/compoundSentimentCallBackTest', methods=['POST', 'GET'])
def cb():
    return compoundSentimentCallBackTest(request.args.get('data'))

def compoundSentimentCallBackTest(company = 'Tesla'):
    if (company == "test"):
        company = 'Game Stop'
        sentiment_df = pd.read_csv('group_code/SentimentAnalysis/sentiment_df.csv')
        sentiment_df = adjustSentimentDataFrame(sentiment_df, company)
        sentimentTitle = "Overall Twitter Sentiment for {companyName} by Date.".format(companyName = company)
        fig = px.line(sentiment_df[sentiment_df['Company']==company], x='Date', y='Compound Average', title=sentimentTitle)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON
        
    else:
        sentiment_df = scrapeAndCleanse(company)
        sentiment_df = adjustSentimentDataFrame(sentiment_df, company)
        compavg = sentiment_df.iloc[0]['Compound Average']
        sentimentTitle = "Overall Twitter Sentiment for {companyName} by Date. \n Today's compound average is {avg}".format(companyName = company, avg = compavg)
        fig = px.line(sentiment_df[sentiment_df['Company']==company], x='Date', y='Compound Average', title=sentimentTitle)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON

@app.route('/keith')
def keith():
    return dash_app.index()

@app.route('/john', methods=['GET'])
def john():
    return render_template('john.html')

@app.route('/data', methods=['POST'])
def getData():
    if request.method == 'POST':
        data = request.json
        close_price = pd.DataFrame()
        close_price[data['ticker']] = yf.download(data['ticker'],
                data['startDate'], data['endDate'])['Adj Close']
        stockStats = close_price.describe()
        temp_dict = dict()
        for (i, row) in stockStats.iterrows():
            temp_dict[row.name] = row.values[0]
        theJSON = close_price.to_json(date_format='iso', orient='split')
        temp_json = json.loads(theJSON)
        temp_json.update(temp_dict)

        return temp_json

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
