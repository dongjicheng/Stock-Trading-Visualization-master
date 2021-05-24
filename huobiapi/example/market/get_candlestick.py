from huobi.client.market import MarketClient
from huobi.constant import *
from huobi.utils import *

market_client = MarketClient(init_log=True)
interval = CandlestickInterval.MIN1
symbol = "ethusdt"
list_obj = market_client.get_candlestick(symbol, interval, 2)
LogInfo.output("---- {interval} candlestick for {symbol} ----".format(interval=interval, symbol=symbol))
LogInfo.output_list(list_obj)
a=[]
for e in list_obj:
    a.append({'id':e.id,'High':e.high,'low':e.low,'open':e.open,'close':e.close,'Volume':e.vol})
import pandas as pd
df = pd.DataFrame(a)
print(df.head())















