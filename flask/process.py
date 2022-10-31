import websocket
from DataBase import DB
from functools import partial
import multiprocessing
import threading
import os
import time
import json


class adder():
    def __init__(self):
        self.entries = multiprocessing.Queue()
        self.database = DB()
        self.socket = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

    def on_message(self, websocket, message):
        print("msg")
        message_dict = json.loads(message)
        candle_closed = message_dict['k']['x']
        if candle_closed:
            print(message_dict['k'])
            self.entries.put(message_dict['k'])
            self.database.add_db_entry(self.entries)

    def on_open(self, ws):
        print('opened connection')
        print("-----------------------")

    def on_close(self, ws):
        print('closed connection')
        print("-----------------------")

    def run(self):
        while True:
            try:
                print("run")
                self.ws = websocket.WebSocketApp(
                    self.socket, on_open=self.on_open(), on_close=self.on_close())
                self.ws.on_message = partial(
                    self.on_message(),)
                self.wst = threading.Thread(target=self.ws.run_forever)
                self.wst.daemon = True
                self.wst.start()
                time.sleep(600)
                self.ws.keep_running = False
                self.wst.stop = True
            except Exception as e:
                print("ERROR: {}".format(e))
                break
        self.entries.close()
        self.entries.join_thread()
        self.ws.close()
        self.database.closed()

    def get_data(self):
        return self.database.get_data()
