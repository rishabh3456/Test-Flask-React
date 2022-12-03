import websocket
from DataBase import DB
from functools import partial
import queue
import threading
import time
import json
import pandas as pd


class adder():
    def __init__(self):
        self.prev_ts = 0
        self.entries = queue.Queue()
        self.database = DB()
        self.socket = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

    def on_message(self, websocket, message, entries):
        message_dict = json.loads(message)
        candle_closed = message_dict['k']['x']
        if candle_closed and message_dict['k']['T'] != self.prev_ts:
            self.prev_ts = message_dict['k']['T']
            self.entries.put(message_dict['k'])
            self.database.add_db_entry(self.entries)

    def run(self):
        while True:
            try:
                self.ws = websocket.WebSocketApp(
                    self.socket, on_message=partial(self.on_message, entries=self.entries))
                self.wst = threading.Thread(target=self.ws.run_forever)
                self.wst.daemon = True
                self.wst.start()
                time.sleep(600)
                self.ws.keep_running = False
                self.wst.stop = True
            except Exception as e:
                print("ERROR: {}".format(e))
                break
        self.ws.close()
        self.database.closed()

    def get_data(self):
        return self.database.get_data()
