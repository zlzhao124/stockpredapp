import pandas as pd
import tweepy
import os
from dotenv import load_dotenv
load_dotenv()


CONSUMER_API_KEY = os.getenv('CONSUMER_API_KEY')
CONSUMER_API_SECRET_KEY = os.getenv('CONSUMER_API_SECRET_KEY')
ACCESS_API_KEY = os.getenv('ACCESS_API_KEY')
ACCESS_API_SECRET_KEY= os.getenv('ACCESS_API_SECRET_KEY')

auth = tweepy.OAuthHandler(CONSUMER_API_KEY, CONSUMER_API_SECRET_KEY)
auth.set_access_token(ACCESS_API_KEY, ACCESS_API_SECRET_KEY)
api = tweepy.API(auth)

def twitterScraper(searchHashtagWord, numTweetsToPull, dateFrom):
    
    tweet_df = pd.DataFrame(columns=['text', 'date'])

    tweets = tweepy.Cursor(
        api.search_tweets, 
        searchHashtagWord, 
        lang="en",
        since_id=dateFrom,
        tweet_mode='extended').items(numTweetsToPull)
    
    list_tweets = [tweet for tweet in tweets] 
 
    for tweet in list_tweets:
        date = tweet.created_at
        hashtags = tweet.entities['hashtags']
        
        try:
            text = tweet.retweeted_status.full_text
        except AttributeError:
            text = tweet.full_text
        hashtext = list()
        for j in range(0, len(hashtags)):
            hashtext.append(hashtags[j]['text'])
        
        ith_tweet = [text, date]
                             
        tweet_df.loc[len(tweet_df)] = ith_tweet

    return tweet_df
    
  
