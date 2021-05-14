import yfinance as yf
import pandas as pd

SPY = yf.Ticker('SPY')

SPY_History = SPY.history(start="2015-01-01", end="2020-04-28")
tailCloses = SPY_History['Close'].tail(14).tolist()
print(tailCloses)