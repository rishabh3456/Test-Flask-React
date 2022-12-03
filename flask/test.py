import websocket

websocket.enableTrace(True)
SOCKET = "wss://stream.binance.us:9443/ws/btcusdt@kline_1m"


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    print('received message')


ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)
ws.run_forever()
