import glob

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#setup #####################################################################
start_date = '2010-1-1'
ema_list = list(range(10, 150))

price_period = "day" #week day 

# how many stock chart will be created
range_len = 10
#############################################################################


def calculate_ema_fark(period, stock_in):
    data = pd.read_csv("./data/yahoo/" + stock_in + ".csv", delimiter=',')
    data = data.dropna(how='any', axis=0)  # clean NULL data
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

    # date filter
    data = data[data.Date > start_date]

    data.set_index("Date", inplace=True)
    data.rename(columns={"Adj Close": "Adj_Close"}, inplace=True)

    if price_period == "week":
        Adj_Close_series = data.Adj_Close.resample('W-FRI').last()
    elif price_period == "day":
        Adj_Close_series = data.Adj_Close

    weekly_pd = pd.concat([Adj_Close_series], axis=1)

    
    #calculate EMA
    weekly_pd.iloc[0:period] = None
    rolling_mean = weekly_pd.ewm(span=period, adjust=False).mean()

    Counter_lowerthanEMA = 0
    for n in range(len(weekly_pd)):
        if(weekly_pd.Adj_Close.iloc[n] < rolling_mean.Adj_Close.iloc[n]):
            Counter_lowerthanEMA = Counter_lowerthanEMA + 1


    # how close to trend
    kapanis = (weekly_pd.Adj_Close.iloc[-1])
    last_rolling_mean = (rolling_mean.Adj_Close.iloc[-1])

    yuzde_last_rolling_mean = (kapanis / last_rolling_mean) - 1  # yüzde kaçı

    return stock_in, kapanis, yuzde_last_rolling_mean, Counter_lowerthanEMA

def plotgraphic(period, stock_in, ihlal, sirano):
    data = pd.read_csv("./data/yahoo/" + stock_in + ".csv", delimiter=',')
    data = data.dropna(how='any', axis=0) 

    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

    # date filter
    data = data[data.Date > start_date]

    data.set_index("Date", inplace=True)
    data.rename(columns={"Adj Close": "Adj_Close"}, inplace=True)

    if price_period == "week":
        Adj_Close_series = data.Adj_Close.resample('W-FRI').last()
    elif price_period == "day":
        Adj_Close_series = data.Adj_Close

    weekly_pd = pd.concat([Adj_Close_series], axis=1)
    weekly_pd_org = weekly_pd.copy() # grafik çiziminde fiyat kısmında org kullanılacak

    weekly_pd.iloc[0:period] = None
    rolling_mean = weekly_pd.ewm(span=period, adjust=False).mean()

    plt.figure()
    plt.plot(weekly_pd_org.index, weekly_pd_org["Adj_Close"], label=stock_in)
    ema_title = "EMA " + str(period)
    plt.plot(weekly_pd_org.index, rolling_mean.Adj_Close, label=ema_title, color='orange')
    plt.legend(loc='upper left')
    title = stock_in+" ihlal: "+str(ihlal)
    plt.title(title, fontsize=20)
    filename = './output/ema/'+stock_in+"_ema_"+str(period)+"_"+str(sirano)+".jpg"
    plt.savefig(filename)

#######################################################################################################################
#
# def END
#
#######################################################################################################################

df_output = pd.DataFrame(columns=['Stock', "Close", "ema", "ema_fark", "Counter_lowerthanEMA"])


path = './data/yahoo/'
files = [f for f in glob.glob(path + "**/*.csv", recursive=True)]

counter = 0

for each_ema in ema_list:
    df_output = df_output.iloc[0:0]
    print(" Ema: ", each_ema, " calculating")
    for f in files:
        counter = counter + 1
        StockName = f.replace("./data/yahoo\\", "")
        StockName = StockName.replace('.csv', "")

        try:
            stock_out, close, ema_fark, counter_ema = calculate_ema_fark(each_ema, StockName)
        except:
            print("An exception occurred: ", StockName)

        insert_row = {
            'Stock': stock_out,
            "Close" : close,
            "ema": each_ema,
            "ema_fark": ema_fark,
            "Counter_lowerthanEMA": counter_ema
        }

        df_output = pd.concat([df_output, pd.DataFrame([insert_row])])

    # filter against to minus figures
    df_output = df_output[df_output.ema_fark > 0]

    # filter for trend brakes
    df_output = df_output[df_output.Counter_lowerthanEMA < 3]

    # sorting
    df_output_sort = df_output.sort_values(by=['ema_fark'], ascending=True)  
   

    if(len(df_output_sort) < 10):
        range_len = len(df_output_sort)


    for i in range(range_len):
        plotgraphic(df_output_sort.iloc[i,2], df_output_sort.iloc[i,0], df_output_sort.iloc[i,4], i)


    print(df_output)








print("Bttiiiiiiiiii")
