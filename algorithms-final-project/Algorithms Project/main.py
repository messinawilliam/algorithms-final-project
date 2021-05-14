import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math

SPY = yf.Ticker('SPY')

SPY_History = SPY.history(start="2015-01-01", end="2020-04-28")

def gdCross():
  crossing = {'golden':[0 for i in range(len(SPY_History))],
                'death':[0 for i in range(len(SPY_History))]}
  df = pd.DataFrame(crossing)

  count = 0
  current50 = SPY_History.iloc[count, 7]
  current200 = SPY_History.iloc[count, 8]

  while math.isnan(current50) or math.isnan(current200):
    count += 1
    current50 = SPY_History.iloc[count, 7]
    current200 = SPY_History.iloc[count, 8]

  while count < len(SPY_History):
    last50 = SPY_History.iloc[count-1, 7]
    current50 = SPY_History.iloc[count, 7]
    current200 = SPY_History.iloc[count, 8]

    if (last50 < current200) and (current50 > current200):
        df.at[count,'golden'] = 1
    elif (last50 > current200) and (current50 < current200):
        df.at[count,'death'] = 1
    count += 1
  
  return df

def MACD():
  #'MACD' 16, 'MACDEWM' 17
  trendLines = {'MACD':[0]*len(SPY_History),
                'signal':[0]*len(SPY_History),
                'momentum':[0]*len(SPY_History)}
  df = pd.DataFrame(trendLines)

  for i in range(len(SPY_History)):
    lastMACD = SPY_History.iloc[i-1, 16]
    currentMACD = SPY_History.iloc[i,16]
    signalLine = SPY_History.iloc[i,17]
    if (lastMACD <= signalLine) and (currentMACD >= signalLine):
      df['momentum'][i] = 1
    elif (lastMACD >= signalLine) and (currentMACD <= signalLine):
      df['momentum'][i] = -1
    df['MACD'][i] = currentMACD
    df['signal'][i] = signalLine

  return df

def RSI():
  days = []
  RS = [math.nan]*14
  RSI = [math.nan]*14
  for i in range(0,14):
    days.append(SPY_History.iloc[i].name)
  #Observe the last 14 closing prices of a stock.
  for date in range(14,len(SPY_History)):
    tailCloses = SPY_History.iloc[date-14:date,3]  #previous 14 days's closing price
    day = SPY_History.iloc[date].name
  
    #Determine whether the current day’s closing price is higher or lower than the previous day.
    i = 0
    upPrices=[]
    downPrices=[]
    while i < len(tailCloses):
      if i == 0:
        upPrices.append(0)
        downPrices.append(0)
      else:
        if (tailCloses[i]-tailCloses[i-1])>0:
          upPrices.append(tailCloses[i]-tailCloses[i-1])
          downPrices.append(0)
        else:
          downPrices.append(tailCloses[i]-tailCloses[i-1])
          upPrices.append(0)
      i += 1
    #calculate the average gain and loss over the last 14 days.
    x = 0
    avgGain = []
    avgLoss = []
    while x < len(upPrices):
      if x > 15:
        avgGain.append(0)
        avgLoss.append(0)
      else:
        sumGain = 0
        sumLoss = 0
        y = x-14
        while y<=x:
          sumGain += upPrices[y]
          sumLoss += downPrices[y]
          y += 1
        avgGain.append(sumGain/14)
        avgLoss.append(abs(sumLoss/14))
      x += 1
    #Compute the relative strength (RS): (AvgGain/AvgLoss)
    #Compute the relative strength index (RSI): (100–100 / ( 1 + RS))
    days.append(SPY_History.iloc[date].name)
    RSvalue = (avgGain[len(avgGain)-1]/avgLoss[len(avgGain)-1])
    RS.append(RSvalue)
    RSI.append(100 - (100/(1+RSvalue)))

  to_df = {
    'RS' : RS,
    'RSI' : RSI
  }
  df_rsi = pd.DataFrame.from_dict(to_df)
  df_rsi['date'] = days
  df_rsi = df_rsi.set_index('date')
  return df_rsi

def bollingerBands():
  #20day upperband: 12, 20day lowerband: 13
  breakAbove = [0]*19
  breakBelow = [0]*19
  for i in range(19,len(SPY_History)):
    if SPY_History.iloc[i, 12] < SPY_History.iloc[i, 9]:  #Comparing bands to day's typical price
      breakAbove.append(1)
      breakBelow.append(0)
    elif SPY_History.iloc[i, 13] > SPY_History.iloc[i, 9]:
      breakAbove.append(0)
      breakBelow.append(1)
    else:
      breakAbove.append(0)
      breakBelow.append(0)

  to_df = {
    'breakAbove': breakAbove,
    'breakBelow': breakBelow
  }
  df_bands = pd.DataFrame.from_dict(to_df)
  return df_bands
  

def movingAverages():
    #200/50 are used for Golden Cross/Death Cross
    SPY_History['50dayMA'] = SPY_History['Close'].rolling(50).mean()
    SPY_History['200dayMA'] = SPY_History['Close'].rolling(200).mean()
    
    #Bollinger Bands use 20 day moving average of the 'typical price'
    #and 20 day standard deviations to create their margins
    SPY_History['Typical'] = (SPY_History['Close'] + SPY_History['High'] + SPY_History['Low'])/3
    SPY_History['20dayMA'] = SPY_History['Typical'].rolling(20).mean()
    SPY_History['20dayStddev'] = SPY_History['Typical'].rolling(20).std()
    SPY_History['20dayUpperBand'] = SPY_History['20dayMA'] + 2*SPY_History['20dayStddev']
    SPY_History['20dayLowerBand'] = SPY_History['20dayMA'] - 2*SPY_History['20dayStddev']
    
    #MACD uses the difference of the 26 and 12 day exponential moving average
    #and the 9 day exponential moving average of the the difference
    SPY_History['26dayEWM'] = SPY_History['Close'].ewm(span=26, adjust=False).mean()
    SPY_History['12dayEWM'] = SPY_History['Close'].ewm(span=12, adjust=False).mean()
    SPY_History['MACD'] = SPY_History['12dayEWM']-SPY_History['26dayEWM']
    SPY_History['MACDEWM'] = (SPY_History['MACD']).ewm(span=9, adjust=False).mean()

def tradeSimulator():
  #RSI returns a number from 0-100
  #MACD returns 1 when signaling a buy and -1 when signaling a short
  #gdCross returns 1's when that column's signal fires
  df1 = gdCross()
  df2 = MACD()
  df3 = RSI()
  df4 = bollingerBands()
  
  crosstrades = 0
  crossprofit = 0
  macdtrades = 0
  macdprofit = 0
  rsitrades = 0
  rsiprofit = 0
  rsistart = 0
  rsistate = 0    #-1,0,1 to signal current type of trade
  bandstrades = 0
  bandsprofit = 0
  bandsstart = 0
  for i in range(len(SPY_History)):
    #Golden/Death Cross trades last 15 days in this scenario
    if df1['golden'][i] == 1:
      crosstrades += 1
      start = SPY_History.iloc[i,0] #open position at opening
      if i + 15 < len(SPY_History):
        end = SPY_History.iloc[i+15,3]  #exit position at closing
      else:
        end = SPY_History.iloc[len(SPY_History)-1,3]
      crossprofit += (end - start)  #closing a buy position
    elif df1['death'][i] == 1:
      crosstrades += 1
      start = SPY_History.iloc[i,0]
      if i + 15 < len(SPY_History):
        end = SPY_History.iloc[i+15,3]
      else:
        end = SPY_History.iloc[len(SPY_History)-1,3]
      crossprofit += (start - end)  #closing a short position
      
    #MACD trades last 15 days in this scenari
    if df2['momentum'][i] == 1:  #buy when MACD goes above its signal line
      macdtrades += 1
      start = SPY_History.iloc[i,0] #open position at opening
      if i + 15 < len(SPY_History):
        end = SPY_History.iloc[i+15,3]  #exit position at closing
      else:
        end = SPY_History.iloc[len(SPY_History)-1,3]
      macdprofit += (end - start)  #closing a buy position
    if df2['momentum'][i] == -1:  #short when MACD goes below its signal line
      macdtrades += 1
      start = SPY_History.iloc[i,0] #open position at opening
      if i + 15 < len(SPY_History):
        end = SPY_History.iloc[i+15,3]  #exit position at closing
      else:
        end = SPY_History.iloc[len(SPY_History)-1,3]
      macdprofit += (start - end)  #closing a short position
      
    #RSI trades are executed when RSI exceeds the normal range,
    #trades are completed when RSI returns to the normal range (>30, <70)
    if df3['RSI'][i] >= 70:
      rsistart = SPY_History.iloc[i,0]  #open position at opening
      rsistate = -1    #shorting, security about to fall
    if df3['RSI'][i] <= 30:
      rsistart = SPY_History.iloc[i,0]  #open position at opening
      rsistate = 1    #buying, security about to climb
    
    if df3['RSI'][i] < 70 and df3['RSI'][i] > 30:
      if rsistate == 1:
        rsitrades += 1
        end = SPY_History.iloc[i,3]  #exit position at closing
        rsiprofit += (end - rsistart)  #closing a buy position
        rsistate = 0
      if rsistate == -1:
        rsitrades += 1
        end = SPY_History.iloc[i,3]  #exit position at closing
        rsiprofit += (rsistart - end)  #closing a short position
        rsistate = 0

    #Bollinger Bands trades are executed when typical price exceeds 2 standard deviations above or below
    #the 20 day rolling mean, trades are completed when prices regress to this range
    if df4['breakAbove'][i] == 1 and i >= 1:  #error handling, there is no band data before i = 20 anyways
      if df4['breakAbove'][i-1] == 0:
        bandsStart = SPY_History.iloc[i,0]  #open position at opening
    if df4['breakAbove'][i] == 0 and i >= 1:
      if df4['breakAbove'][i-1] == 1:
        bandstrades += 1
        end = SPY_History.iloc[i,3]  #exit position at closing
        bandsprofit += (end - bandsstart)  #closing a buy position
    if df4['breakBelow'][i] == 1 and i >= 1:
      if df4['breakBelow'][i-1] == 0:
        bandsStart = SPY_History.iloc[i,0]  #open position at opening
    if df4['breakBelow'][i] == 0 and i >= 1:
      if df4['breakBelow'][i-1] == 1:
        bandstrades += 1
        end = SPY_History.iloc[i,3]  #exit position at closing
        bandsprofit += (bandsstart - end)  #closing a short position
        
  print("Golden/Death Cross Profit: ", crossprofit)
  print("MACD Profit: ", macdprofit)
  print("RSI Profit: ", rsiprofit)
  print("Bollinger Bands Profit: ", bandsprofit)
  print("Golden/Death Cross Profit Per Trade: ", crossprofit/crosstrades)
  print("MACD Profit Per Trade: ", macdprofit/macdtrades)
  print("RSI Profit Per Trade: ", rsiprofit/rsitrades)
  print("Bollinger Bands Profit Per Trade: ", bandsprofit/bandstrades)
  
movingAverages()
tradeSimulator()