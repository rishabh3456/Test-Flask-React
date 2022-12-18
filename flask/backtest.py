# -*- coding: utf-8 -*-
import random
import json
import pprint
import pandas as pd
import sqlite3
import os
import datetime
import time
import talib as ta
from binance.client import Client

client = Client()

stor = datetime.date.today()
END_TIME = stor.strftime("%d %b, %Y")
delta = datetime.timedelta(days=1030)
stor2 = stor-delta
START_TIME = stor2.strftime("%d %b, %Y")

data = client.get_historical_klines(
    symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_3MINUTE, start_str=START_TIME, end_str=END_TIME)

cols = ['Timestamp', 'O', 'H', 'L', 'C', 'V', 'CloseTime',
        'QuoteAssetVolume', 'NumberOfTrades', 'TBBAV', 'TBQAV', 'null']
new_df = pd.DataFrame(data, columns=cols)
new_df = new_df.reindex(columns=new_df.columns.tolist()[
                        0:6]+['macd1', 'macd2', 'macd3', 'chaikin', 'stochrsi1', 'stochrsi2', 'rsi', 'adx', 'obv', 'trix'])
new_df["macd1"], new_df["macd2"], new_df["macd3"] = ta.MACD(
    new_df['C'], fastperiod=12, slowperiod=26, signalperiod=9)
new_df["chaikin"] = ta.AD(new_df['H'], new_df['L'], new_df['C'], new_df['V'])
new_df["stochrsi1"], new_df["stochrsi2"] = ta.STOCHRSI(
    new_df['C'], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
new_df["trix"] = ta.TRIX(new_df['C'], timeperiod=10)
new_df["adx"] = ta.ADX(new_df['H'], new_df['L'], new_df['C'], timeperiod=14)
new_df["rsi"] = ta.RSI(new_df['C'], timeperiod=10)
new_df["obv"] = ta.OBV(new_df['C'], new_df['V'])

new_df = new_df[33:]
print(new_df)


def checker(num, idx, df):
    if num == 0:
        macd = df['macd3'].iloc[idx]
        rsi = df['rsi'].iloc[idx]
        adx = df['adx'].iloc[idx]
        if (macd >= -1 and macd <= 1) and df['macd3'].iloc[idx-1] < macd and rsi <= 31 and adx >= 25:
            return 'B'
        elif (macd >= -1 and macd <= 1) and df['macd3'].iloc[idx-1] > macd and rsi >= 69 and adx >= 20:
            return 'S'
        else:
            return 'N'

    if num == 1:
        macd = df['macd3'].iloc[idx]
        rsi = df['stochrsi2'].iloc[idx]
        adx = df['adx'].iloc[idx]
        if (macd >= -1 and macd <= 1) and df['macd3'].iloc[idx-1] < macd and rsi <= 31 and adx >= 25:
            return 'B'
        elif (macd >= -1 and macd <= 1) and df['macd3'].iloc[idx-1] > macd and rsi >= 69 and adx <= 24:
            return 'S'
        else:
            return 'N'

    if num == 2:
        trix = df['trix'].iloc[idx]
        rsi = df['stochrsi2'].iloc[idx]
        adx = df['adx'].iloc[idx]
        if (trix >= 0.03) and rsi <= 31 and adx >= 25:
            return 'B'
        elif trix <= -0.02 and rsi >= 69 and adx <= 25:
            return 'S'
        else:
            return 'N'


Multiplier = 0.99925

# create a class to define what each step


class Environment:
    def __init__(self, balance):
        self.distribution = {'USD0': balance, 'USD1': balance,
                             'USD2': balance, 'BTC0': 0.0, 'BTC1': 0.0, 'BTC2': 0.0}
        self.buys = []
        self.sells = []

    def buy(self, number, buy_price, time):
        self.distribution[f'BTC{number}'] = (
            self.distribution[f'USD{number}'] / float(buy_price)) * Multiplier
        self.distribution[f'USD{number}'] = 0.0
        self.buys.append([time, buy_price])

    def sell(self, number, sell_price, time):
        self.distribution[f'USD{number}'] = self.distribution[f'BTC{number}'] * \
            float(sell_price) * Multiplier
        self.distribution[f'BTC{number}'] = 0.0
        self.sells.append([time, sell_price])


env = Environment(balance=1)

check = ['N' for i in range(3)]

for i in range(len(new_df)):
    for j in range(3):
        check[j] = checker(num=j, idx=i, df=new_df)
        if env.distribution[f'USD{j}'] != 0:
            if check[j] == 'B':
                env.buy(j, new_df['L'].iloc[i], new_df['Timestamp'].iloc[i])
        if env.distribution[f'USD{j}'] == 0:
            if check[j] == 'S':
                env.sell(j, new_df['H'].iloc[i], new_df['Timestamp'].iloc[i])


for j in range(3):
    if env.distribution[f'USD{j}'] == 0:
        env.sell(j, new_df['H'].iloc[-1], new_df['Timestamp'].iloc[-1])

print(env.distribution)
print(len(env.buys))
print(env.buys[126])
