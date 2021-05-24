import gym

from stable_baselines.common.policies import MlpPolicy,CnnPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

import tensorflow as tf
from tf_agents.networks import q_network
from tf_agents.agents.dqn import dqn_agent

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
    a.append({'id':e.id,'High':e.high,'low':e.low,'open':e.open,'close':e.close,'Volume':e.vol})
import pandas as pd
df = pd.DataFrame(a)

# The algorithms require a vectorized environment to run
env = DummyVecEnv([lambda: StockTradingEnv(df)])

model = PPO2(CnnPolicy, env, verbose=1)
model.learn(total_timesteps=50)

obs = env.reset()
for i in range(len(df['id'])):
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render(title="MSFT")
