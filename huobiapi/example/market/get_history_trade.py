from huobi.client.market import MarketClient
from huobi.utils import *
import numpy as np
import time
while True:
    market_client = MarketClient()
    list_obj = market_client.get_history_trade("btcusdt", 30)
    buy_info={'count':0,'prices':[],'amounts':[]}
    sell_info={'count':0,'prices':[],'amounts':[]}
    for a in list_obj:
        if a.direction == 'buy':
            buy_info['count'] = buy_info['count'] + 1
            buy_info['prices'].append(a.price)
            buy_info['amounts'].append(a.amount)
        elif a.direction == 'sell':
            sell_info['count'] = buy_info['count'] + 1
            sell_info['prices'].append(a.price)
            sell_info['amounts'].append(a.amount)
    buy_summary={'count':buy_info['count'],'amount':np.sum(np.array(buy_info['amounts'])),'avg_price':np.sum(np.array(buy_info['prices'])*np.array(buy_info['amounts']))/np.sum(np.array(buy_info['amounts']))}
    sell_summary={'count':sell_info['count'],'amount':np.sum(np.array(sell_info['amounts'])),'avg_price':np.sum(np.array(sell_info['prices'])*np.array(sell_info['amounts']))/np.sum(np.array(sell_info['amounts']))}
    print(buy_summary)
    print(sell_summary)
    print(buy_summary['amount']/sell_summary['amount'])
    time.sleep(0.5)
