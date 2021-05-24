import gym

from stable_baselines.common.policies import MlpPolicy,CnnPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

import tensorflow as tf

from env.StockTradingEnv import StockTradingEnv
import huobi

import pandas as pd

from huobi.client.market import MarketClient
from huobi.constant import *
from huobi.utils import *

market_client = MarketClient(init_log=True)
interval = CandlestickInterval.MIN1
symbol = "ethusdt"
list_obj = market_client.get_candlestick(symbol, interval, 2000)
LogInfo.output("---- {interval} candlestick for {symbol} ----".format(interval=interval, symbol=symbol))
LogInfo.output_list(list_obj)
a=[]
for e in list_obj:
    a.append({'Date':e.id,'High':e.high,'Low':e.low,'Open':e.open,'Close':e.close,'Volume':e.vol,'Adjusted_Close':e.close})
import pandas as pd
df = pd.DataFrame(a)
df.sort_values('Date',ascending=True)

# The algorithms require a vectorized environment to run
env = DummyVecEnv([lambda: StockTradingEnv(df)])
env = StockTradingEnv(df)

model = PPO2(MlpPolicy, env, verbose=1)
model.learn(total_timesteps=5000)

obs = env.reset()
for i in range(len(df['Date'])):
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render(title='MSF')
