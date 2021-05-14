import pandas as pd

xls = pd.ExcelFile('/Users/scott/Downloads/AAPL5yr.xlsx')
df1 = pd.read_excel(xls)

#200/50 are used for Golden Cross/Death Cross
df1['50dayMA'] = df1['Close/Last'].rolling(50).mean()
df1['200dayMA'] = df1['Close/Last'].rolling(200).mean()

#Bollinger Bands use 20 day moving average of the 'typical price'
#and 20 day standard deviations to create their margins
df1['Typical'] = (df1['Close/Last'] + df1['High'] + df1['Low'])/3
df1['20dayMA'] = df1['Typical'].rolling(20).mean()
df1['20dayStddev'] = df1['Typical'].rolling(20).std()
df1['20dayUpperBand'] = df1['20dayMA'] + 2*df1['20dayStddev']
df1['20dayLowerBand'] = df1['20dayMA'] - 2*df1['20dayStddev']

#MACD uses the difference of the 26 and 12 day exponential moving average
#and the 9 day exponential moving average of the the difference
df1['26dayEWM'] = df1['Close/Last'].ewm(span=26, adjust=False).mean()
df1['12dayEWM'] = df1['Close/Last'].ewm(span=12, adjust=False).mean()
df1['MACD'] = df1['26dayEWM']-df1['12dayEWM']
df1['MACDEWM'] = (df1['MACD']).ewm(span=9, adjust=False).mean()