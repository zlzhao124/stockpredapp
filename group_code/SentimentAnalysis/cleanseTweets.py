import pandas as pd
import tweepy
import datetime 
import re

def cleanseRepeatedTweets(input_df):#Cleanse repeated tweets and retweets
    return (input_df.drop_duplicates(subset='text', keep="first"))
    
def cleanseWebAddresses(inputString):#Removes any video links or hyper links from the tweet text
    return (re.sub('http://\S+|https://\S+', '', inputString))

def cleanseHashtag(inputString): #Removes Hashtags(#) from tweet text.
    return (re.sub("\#[A-Za-z0-9_]+","", inputString))

def cleanseDollarSign(inputString): #Removes company stock ticker ($) from tweet text
    return (re.sub(r"\$[A-Za-z0-9_]+","", inputString))

def cleanseMention(inputString): #Removes @(username) from the tweet text
    return (re.sub("\@[A-Za-z0-9_]+","", inputString))
    
def cleanseNonEnglishChar(inputString): #Removes emoji ASCII, hashtag, and non-English foreign char. Gets string with char between a to z or digits and whitespace characters.
    return(re.sub(r'[^\w\s]', '', inputString))
    
def cleanseLeadingTrailingWhiteSpace(inputString): #Removes different indentation and return new lines in the text  
    return(inputString.strip())

def cleanseDate(inputString): #Removes the time information from the date string
    regexDate = str(re.sub(' \d{2}:\d{2}:\d{2}[\+]\d{2}:\d{2}', '', inputString))
    return(regexDate)
    
def cleanse(raw_df):
    
    cleansed_df = cleanseRepeatedTweets(raw_df)
    
    for index, row in cleansed_df.iterrows():
    
        #Cleanse dataframe 'text' column
        text = row['text']
        cleansedString = cleanseWebAddresses(text)
        cleansedString = cleanseLeadingTrailingWhiteSpace(cleansedString)
        cleansedString = cleanseHashtag(cleansedString)
        cleansedString = cleanseDollarSign(cleansedString)
        cleansedString = cleanseMention(cleansedString)
        cleansedString = cleanseNonEnglishChar(cleansedString)
        cleansed_df.at[index, 'text'] = cleansedString #Reassign cleansed text back into the corresponding 'text' column in the dataframe
        
        #Cleanse dataframe 'date' column
        date = str(row['date'])
        cleansedDate = cleanseDate(date)
        cleansed_df.at[index, 'date'] = cleansedDate
  
    return cleansed_df
    
