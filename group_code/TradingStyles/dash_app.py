from grpc import server
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State
import yfinance as yf
import numpy as np

stock = yf.Ticker('FB')
# test data for starting 
stock_data = stock.history(period="max")

df = pd.DataFrame(stock_data)
ecom_sales = pd.DataFrame(stock_data)
logo_link = 'https://assets.datacamp.com/production/repositories/5893/datasets/fdbe0accd2581a0c505dab4b29ebb66cf72a1803/e-comlogo.png'
ecom_scatter = px.line(ecom_sales, x=ecom_sales.index, y='Close', width=850, height=550)
ecom_scatter.update_layout({'legend':dict(orientation='h', y=-0.7,x=1, yanchor='bottom', xanchor='right')})

def get_dash_app(app):
    dash_app = Dash(
        __name__,
        server=app,
        url_base_pathname='/keith/'
    )
    
    # setting up dash connection to server
    dash_app.layout = html.Div([
    html.H1('Stocks'),
   
    html.H3("The basis of the moving average trading style is very simple. If the short moving average exceeds the long moving average then you go long, if the long moving average exceeds the short moving average then you exit."),
         html.Br(),
         html.H3('Enter Stock Ticker Symbols: '),
        dcc.Textarea(
            id='textarea-state-example',
            value='',
            style={'width': '10%', 'align': 'center'},
        ),
        html.Button('Submit', id='textarea-state-example-button', n_clicks=0, style={'height': 25}),
                
        html.Br(),
    
    html.Div(
        children=[
        html.Div(
            children=[
            html.H3('Date vs Close'),
            dcc.Graph(id='scatter'),
            ],
            
            style={'width':'950px', 'height':'650px', 'display':'inline-block', 
                'vertical-align':'top', 'border':'1px solid black', 'padding':'20px'}),    

        
        
        html.Br(),
        html.Div(id='textarea-state-example-output', style={'whiteSpace': 'pre-line'}),
        html.Div(
        children=[
            dcc.Graph(id='major_cat'),
            dcc.Graph(id='minor_cat'),
        ],
        style={'width':'1250px', 'height':'625px','display':'inline-block'})
        ]),], 
    style={'text-align':'center', 'display':'inline-block', 'width':'100%'}
    )
    #layout structure for the app
    init_callback(dash_app)
    #applies callbacks to the app and then returns the app so that it can be used else where 
    return dash_app
def init_callback(dash_app):
    @dash_app.callback(
    # Set the input and output of the callback to link the dropdown to the graph
    Output(component_id='scatter', component_property='figure'),
    Input('textarea-state-example-button', 'n_clicks'),
    State('textarea-state-example', 'value')

    )
    def chart_one(n_clicks,inputs):
        if inputs == None or inputs == '' or n_clicks <= 0:
            inputs = 'FB'
        stock = yf.Ticker(inputs)
        stock_data = stock.history(period="max") #where the time can be adjusted
        df = pd.DataFrame(stock_data)
        fig = px.line(df, x=df.index, y='Close', template="simple_white", title=f'{inputs} stock data')
        return fig
        #first chart for display with possible modeling fit
    @dash_app.callback(
    Output(component_id='major_cat', component_property='figure'),
    Input('textarea-state-example-button', 'n_clicks'),
    State('textarea-state-example', 'value')

    )
    def moving_average(n_clicks,inputs):
        #larger moving average calculation for the charts that takes the ticker and the submit button as input
        if inputs == None or inputs == '' or n_clicks <= 0:
            inputs = 'FB'

        stock = yf.Ticker(inputs)
        stock_data = stock.history(period="max")  #where the time can be adjusted
        df = pd.DataFrame(stock_data)
        df['SMA50'] = df['Close'].rolling(50).mean()
        df['SMA200'] = df['Close'].rolling(200).mean()
        fig = px.line(df, x=df.index, y=['Close','SMA200','SMA50'], template="simple_white", title=f'{inputs} stock data', width=900, height=500)
        return fig
        # predition chart with simple moving averages 
    @dash_app.callback(
    Output(component_id='minor_cat', component_property='figure'),
    Input('textarea-state-example-button', 'n_clicks'),
    State('textarea-state-example', 'value')

    )
    def short_moving_average(n_clicks,inputs):
        # by default if no ticker is entered or left blank then the chart uses Facebook 
        if inputs == None or inputs == '' or n_clicks <= 0:
            inputs = 'FB'
        stock = yf.Ticker(inputs)
        stock_data = stock.history(period="max")
        df = pd.DataFrame(stock_data)
        df['SMA40'] = df['Close'].rolling(40).mean()
        df['SMA100'] = df['Close'].rolling(100).mean()
        #lower moving averages predictions chart 

        figs = px.line(df, x=df.index, y=['Close','SMA100','SMA40'], template="simple_white", title=f'{inputs} stock data', width=900, height=500)
        return figs

    