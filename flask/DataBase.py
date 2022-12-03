import os
import sqlite3
import pandas as pd
import talib as ta


DEFAULT_PATH = os.path.join(os.path.abspath(''), 'prices.sqlite3')
NUM_QUEUE_ITEMS = 250


class DB():
    def __init__(self):
        self.dbpath = DEFAULT_PATH
        self.df = pd.DataFrame(
            columns=['Timestamp', 'O', 'H', 'L', 'C', 'V', 'macd', 'stochrsi', 'adx'])
        self.cnec = sqlite3.connect(
            self.dbpath, timeout=15, check_same_thread=False)
        self.df.to_sql("BTCUSD", self.cnec, if_exists='replace')
        self.cnec.close()

    def connect(self):
        self.cnec = sqlite3.connect(
            self.dbpath, timeout=15, check_same_thread=False)

    def closed(self):
        self.cnec.close()

    def add_db_entry(self, entries):
        self.connect()
        data = entries.get(True)
        old_df = pd.read_sql(
            'SELECT Timestamp,O,H,L,C,V FROM BTCUSD', self.cnec)
        old_df.set_index('Timestamp', inplace=True)
        new_data = [str(data['t']), float(data['o']), float(
            data['h']), float(data['l']), float(data['c']), float(data['v'])]
        df = pd.DataFrame(data=[new_data], columns=[
                          'Timestamp', 'O', 'H', 'L', 'C', 'V'])
        df.set_index('Timestamp', inplace=True)
        new_df = pd.concat([old_df[-NUM_QUEUE_ITEMS:], df])
        macd, macdsignal, new_df["macd"] = ta.MACD(
            new_df['C'], fastperiod=12, slowperiod=26, signalperiod=9)
        fastk, new_df["stochrsi"] = ta.STOCHRSI(
            new_df['C'], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
        new_df["adx"] = ta.ADX(new_df['H'], new_df['L'],
                               new_df['C'], timeperiod=14)
        new_df.to_sql('BTCUSD', self.cnec, if_exists='replace')
        self.closed()

    def get_data(self):
        self.connect()
        df = pd.read_sql(
            'SELECT * FROM BTCUSD ORDER BY Timestamp DESC LIMIT 1', self.cnec)
        self.closed()
        if df.empty:
            return {"empty": "empty"}
        return df.to_json()
