import websocket
from DataBase import DB
from functools import partial
import multiprocessing
import threading
import os
import time


class adder():
    def __init__(self):
        self.entries = multiprocessing.Queue()
        self.database = DB()
        self.pool = multiprocessing.Pool(
            os.cpu_count(), self.database.add_db_entry, (self.entries,))
        self.socket = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

    def run(self):
        while True:
            try:
                self.ws = websocket.WebSocketApp(
                    self.socket, on_open=self.on_open, on_close=self.on_close)
                self.ws.on_message = partial(
                    self.database.add_db_entry(), self.entries)
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
