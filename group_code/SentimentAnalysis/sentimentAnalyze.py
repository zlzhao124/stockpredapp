import pandas as pd
import os
import sys
import nltk

path = os.getcwd()
parentPath = os.path.dirname(path)
pathToNLTK=parentPath+'/SentimentAnalysis'+'/nltk_data'
nltk.data.path.append(pathToNLTK) #Set path of nltk library to current repository
nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

def analyze(cleansedTweets_df):

    analyzedTweets_df = cleansedTweets_df.copy()
    for index, row in analyzedTweets_df['text'].iteritems():
        score = SentimentIntensityAnalyzer().polarity_scores(row)
        neg = score['neg']
        neu = score['neu']
        pos = score['pos']
        comp = score['compound']
     
        if neg > pos:
            analyzedTweets_df.loc[index, 'sentiment'] = "negative"
        elif pos > neg:
            analyzedTweets_df.loc[index, 'sentiment'] = "positive"
        else:
            analyzedTweets_df.loc[index, 'sentiment'] = "neutral"
            
        analyzedTweets_df.loc[index, 'neg'] = neg
        analyzedTweets_df.loc[index, 'neu'] = neu
        analyzedTweets_df.loc[index, 'pos'] = pos
        analyzedTweets_df.loc[index, 'compound'] = comp
        
    return analyzedTweets_df