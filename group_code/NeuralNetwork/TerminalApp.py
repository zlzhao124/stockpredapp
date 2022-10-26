from Predictor import TrendPredictor

predictor = TrendPredictor()
print("====================================================================")
print("------------------ Stock Trend Predictor V 1.0 ---------------------")
print("   This application takes a ticker as input (e.g FB, AAPL).") 
print("It will then predict (using the last 6 trading hours data) on how \nlikely this stock is going to increase/decrease/stay the same with \ntheir associated confidence levels.")
print("====================================================================")

while True:
    ticker = input("Input ticker to predict: ")
    predictor.set_ticker(ticker)
    predictor.predict()
    print("------------------------------------------------------------------")