from huobi.client.market import MarketClient
from huobi.constant import *
from huobi.exception.huobi_api_exception import HuobiApiException
import pandas as pd

def callback(candlestick_req: 'CandlestickReq'):
    a=[]
    for e in candlestick_req.data:
        a.append({'id': e.id, 'High': e.high, 'Low': e.low, 'Open': e.open, 'Close': e.close, 'Volume': e.vol,
                  'Adjusted_Close': e.close})
    df = pd.DataFrame(a)
    df = df.set_index('id')
    df.to_csv('candlestick', mode='a')


def error(e: 'HuobiApiException'):
    print(e.error_code + e.error_message)

sub_client = MarketClient(init_log=True)
#sub_client.request_candlestick_event("btcusdt", CandlestickInterval.MIN1, callback, from_ts_second=None, end_ts_second=None, error_handler=None)
#sub_client.request_candlestick_event("btcusdt", CandlestickInterval.MIN1, callback, from_ts_second=1571124360, end_ts_second=1571129820)
#sub_client.request_candlestick_event("btcusdt", CandlestickInterval.MIN1, callback, from_ts_second=1569361140, end_ts_second=0)
#sub_client.request_candlestick_event("btcusdt", CandlestickInterval.MIN1, callback, from_ts_second=1569379980)
#sub_client.req_candlestick("btcusdt", CandlestickInterval.MIN1, callback, from_ts_second=1514736000, end_ts_second=1514736000 + 60 * 899)


# for i, v in enumerate(range(1514736000, 1621499973, 15 * 60 * 899)):
#     if i == 0:
#         left = v
#         right = v
#     else:
#         left = right
#         right = v
#         sub_client.req_candlestick("btcusdt", CandlestickInterval.MIN15, callback, from_ts_second=left,
#                                    end_ts_second=right)
#     import time
#     time.sleep(2)

# import pandas as pd
# df = pd.read_csv('candlestick')
# df = df.drop_duplicates(['id'], keep='first')
# df['Date'] = df['id']
# df = df.set_index('id')
# df = df.drop(['id'], axis=0)
# df = df.sort_index(ascending=True)
# print(df.head(903))
s=set()
for i in open('candlestick'):
    s.add(i)
with open('candlestick1','w') as f:
    for i in s:
        f.write(i)



