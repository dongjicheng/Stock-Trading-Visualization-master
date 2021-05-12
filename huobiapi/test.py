#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from websocket import create_connection

url = 'wss://ws.btcfans.com/ws-v2'
while True:  # 一直链接，直到连接上就退出循环
    time.sleep(2)
    try:
        ws = create_connection(url,header=["Sec-WebSocket-Version: 13","Upgrade: websocket","Origin: https://price.btcfans.com","User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36","Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits","Sec-WebSocket-Key: GSS2a8skGMg3rOL02b9Xrw==","Connection: Upgrade"])
        print(ws)
        break
    except Exception as e:
        print('连接异常：', e)
        continue
while True:  # 连接上，退出第一个循环之后，此循环用于一直获取数据
    ws.send('{"event":"subscribe", "channel":"btc_usdt.ticker"}')
    response = ws.recv()
    print(response)
