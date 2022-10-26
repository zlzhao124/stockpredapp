from cProfile import label
from email import message
from flask import Flask, render_template, request
import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt
import copy
import matplotlib.pyplot as plt
import json

app = Flask(__name__)


# use html template to show form with input for ticker, start date, and end date
@app.route("/", methods=["GET"])
def hello_world():
    return render_template("index.html")


# post route to use yfinance to get data
@app.route("/data", methods=["POST"])
def getData():
    if request.method == "POST":
        data = request.json
        close_price = pd.DataFrame()
        close_price[data["ticker"]] = yf.download(
            data["ticker"], data["startDate"], data["endDate"]
        )["Adj Close"]
        return close_price.to_json(date_format="iso")
