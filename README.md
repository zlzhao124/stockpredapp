# Project overview
This project aims to provide stock traders meaningful insights which they can consult before making any trading decisions. The project consists of four main components:
* Predicting stock trend with Recurrent Neural Network (Hoang)
* Stock Sentimental Analysis (Zach & Andrew)
* Summary Statistics & Performance Indicator (John)
* Stock visualization and Price Prediction (Keith)

All of the components above can be tested via our central Flask application. Details are below.

# Getting started

## Installing dependencies
To get started, simply activate your favorite virtual environment, navigate to this project root folder, and run:
    `pip install -r requirements.txt`
    Note that the installation process may take a while since we have some fairly heavy packages such as TensorFlow.
## Run the flask app
In the same folder, open a terminal and run:
    `python flask_app.py`
Our flask application can then be accessed at http://localhost:5000/. From here you can navigate to different components of the project via the links in the navigation bar. 

# Details of each component

## 1. Stock trend prediction with RNN

### Making a prediction
Included in this project is a pretrained RNN model which analyzes the last 6 trading-hour price data (*Open, Close, High, Low, Volume*) and predicts whether the average price of that stock will increase, decrease, or stay (approximately) the same with confidence percentages. 
To make a prediction, simply navigate to "Trend Prediction" tab in our Flask app, enter a ticker (e.g. TSLA, FB), and hit submit. 

![](https://i.imgur.com/dA6ziW6.png)



---
### Train a new model
**1. Download and format data**
Navigate to `FinalProject/code/NeuralNetwork` and open  `get_data.py` in a text editor. From here you can find a set of variables which you can edit to suit your needs:
* **EVAL_RANGE:** range of time units in the past to consider (default: 24)
* **PREDICT_RANGE:** range of time units the future to generate labels (default: 4)
* **START_DATE:** Data will start from this date
* **END_DATE** = Data will be up to this date
* **RAW_INTERVAL:** Interval to retrieve data from YFinance. For example, "15m", "1h", "1d". (default: "15m")
* **NO_CHANGE_THRESHOLD:** percentage of last price for a "stay the same" target to be created (default: 0.1%)
* **TRAIN_RATIO:** Formatted data will be split into train and test set right away to ensure equal proporiton of each stock's data to the train set and test set. (default: 0.9)

**Note:** Data will be download for the *100 tickers* in the *Electronic Technology* section listed in `FinalProject/group_code/NeuralNetwork/tickers.csv`. You can also change this file if you see fits. 

After changing those variables, simply run `get_data.py`, the train and test data can then be found under `FinalProject/group_code/NeuralNetwork/data` in `.npy` format. 

**2. Train the RNN using newly obtained data**
Navigate to `FinalProject/group_code/NeuralNetwork` and run `model_training.py`. The trained RNN structure and weights can then be found under `FinalProject/group_code/NeuralNetwork/trained_model` in `.json` and `.h5` formats.

**Note:** You don't need to manually load and use these files. 
The file `Predictor.py` contains the `TrendPredictor` class which automatically loads the RNN in `/trained_model` upon initialization, and you can use this class to make predictions right away with the following 2 functions of the class:
* **set_ticker(ticker):** The input `ticker` is the ticker for which you want to make a prediction.  
* **predict()**: Returns the predictions as shown in the screnshot above. 
Note that you need to change the EVAL_RANGE and PREDICT_RANGE variables in this class's constructor match the trained RNN model. ![](https://i.imgur.com/026iPeY.png)


Details about the class and the functions it offers can be found by opening `Predictor.py` in a text editor and read the comments. 



---


## 2. Sentiment Analysis
We scraped tweets using a company's hashtag and we used sentiment analysis to gauge Twitter users' sentiment about different comapnies

The data displayed in both deliverables can be changed through a textbox that allows you to type any company in. After a company is inputted, callback methods for the app trigger, calling `scrapeAndCleanse` and `adjustSentimentDataFrame`. 

`scrapeAndCleanse` uses the Tweepy API to scrape Twitter with the company as a hashtag, and outputs a sample of recent tweets with that company into a dataframe. Most of this is done directly using Tweepy's documentation. Then the data is cleansed by eliminating any retweets and faulty symbols (see comments in `group_code/SentimentAnalysis/cleanseTweets.py` for full details on what gets cleansed), and analyzed using the VADER Sentiment Analysis model from the Natural Language Toolkit (NLTK) (see comments in `group_code/SentimentAnalysis/sentimentAnalyze.py` to see what the Analyzer outputs for us). Each tweet that goes through this analysis outputs a date, a label of "positive", "negative", or "neutral", and a compound, which is a score that shows how positive or negative a tweet is: positive tweets are > 0, negative tweets are < 0, and the greater the absolute value the more extreme.

In `adjustSentimentDataFrame`, we arrange these tweets by their date and count the number of positive and negative tweets per day, as well as the compound average of these tweets. Both deliverables use this final dataframe we make

**Note:** To test data over multiple days enter "test" and hit the Submit button. This will pull up a pre-scraped dataframe to show data over many days.

**1. Positive/Negative Bar Chart**
Displays a pair of bars that show the number of positive and negative tweets counted. If the API pulled tweets from multiple days, this graph will display tweets from each day separately. The default company scraped when you first click the tab is Tesla.

![](https://imgur.com/joVikUh.png)

**2. Compound Average Line Graph**
Displays a line graph that shows the change in average of compound the number of positive and negative tweets counted. Unfortunatly, most times the API pulls tweets from a company, they all occur on the same day, but panning your cursor over the center of the line graph displays the correct number. For convenience, we have also displayed the current day's number on the html page as well. Here's an example of the compound average over multiple days though. 

![](https://imgur.com/zfuzrnJ.png)

The default company scraped when you first click the tab is Tesla.

Some unfortunate drawbacks to calling Tweepy with every change of the textbox in our deliverables are 
1. Tweepy takes time to scrape, so results are not immediate, and sometimes the plots take awhile to load.   
2. Like we mention in previous paragraphs, sometimes Tweepy doesn't pull tweets from multiple days, so it's hard to gauge how a company does over time. 
3. Tweepy only allows so many calls to the API, so after a lot of requests the API may time out and cause a "too many requests" error. Although having pre-stored data for this project was feasible, it would take up a lot of memory and take freedom away from the user to search up any company or hashtag they wanted. We've also hindered this drawback to a minimum by finding a good number for the sample size of tweets pulled so that it still displays a good enough reflection of the sentiment of the company but not so large as to cause quick timeouts.

## 3. Stock visualization and Price Prediction

For the quantitative analysis portion, we performed  quantitative analysis on various stock close prices by looking at the moving averages and comparing the days. part, we decided to showcase the deliverables: charts with different moving averages plotted

The data displayed in both deliverables can be changed through typing the company's ticker into the search box. After a company is inputted, callback methods for the app trigger, calling `init_callbacks` and `moving_average functions`. 

The `moving_average functions` uses the Yahoo Finance Api to get historical stock data and plots that along side the moving average from the long term mean and the short term mean of the closing price by building dataframes and using ploty to plot the numbers. The default stock entered is Facebook which a popular indicator and usually have huge directional pull on the stock market because of it's size and popularitry 

The basis of the moving average trading style is very simple. If the short moving average exceeds the long moving average then you go long, if the long moving average exceeds the short moving average then you exit.


Some unfortunate drawbacks to calling Yahoo Finance Api and using methods are 
1. Stock prediction is extrememly diffcult and near impossible
2. There is a decent amount of time in getting the information because it is pulling a amount of data beyond the closing price like industry and sector of the stock 
3. The model works on historical data so there is a large margin of error for new stocks that have just hit the market like Robinhood, HOOD, and Coinbase, COIN as examples 



## 4. Summary Statistics & Performance Indicator
In the Performance Indicators section of this project, we gathered summary statistics on the adjusted close price of a user inputed stock so the potential investor is able to make informed decisions as to the movement of the stock. The best way to display this data was a line plot showing price data over a period of time and an output of statistical data. 

The deliverables of the project show a line chart displaying time series data of the stock's price and an output of the statistics for the stock. The user is able to enter stock ticker in the search box and the graph and statistics will update by making a call to yfinance, which is how the data is downloaded. 

![](https://i.imgur.com/qD5JXTj.png)


In the method `getData()`, an empty data frame is initialized. Once the user inputs a stock ticker, a start date and an end date, the data frame is updated with the downloaded information for yfinance. We then compute the summary statistics, and then convert both to a json to be transfer the data to be updated in the graph. 

From there, axious.post is used to grab the data and plot it into a chart. The X-Axis labels are the dates and the Y-Axis labels are the stock prices. The stock statistics are appended below in their own div container. 

![](https://i.imgur.com/Gui7Eoa.png)
![](https://i.imgur.com/oPyXZrL.png)


Some drawbacks to using yfinance to grab the stock data include: 

1. Stock performance and statistics only account for historical data and do not give 100% accurate indication as to what the future of the stock might look like
2. Extracting the correct data can be difficult 
