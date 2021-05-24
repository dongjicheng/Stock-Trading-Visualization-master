import gym

from stable_baselines.common.policies import MlpPolicy,CnnPolicy,LstmPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2,A2C

import tensorflow as tf

from env.StockTradingEnv import StockTradingEnv
import huobi

import pandas as pd

from huobi.client.market import MarketClient
from huobi.constant import *
from huobi.utils import *

import pandas as pd
df = pd.read_csv('huobiapi//example//market//candlestick1',dtype = {'id' : int,'High':float,'Low':float,'Open':float,'Close':float,'Volume':float,'Adjusted_Close':float})
df = df.drop_duplicates(['id'], keep='first')
df['Date'] = df['id']
#df = df.set_index('id')
df = df.sort_values('Date',ascending=True)
print(df.head(903))

# The algorithms require a vectorized environment to run
env = DummyVecEnv([lambda: StockTradingEnv(df)])
env = StockTradingEnv(df)

model = A2C(LstmPolicy, env, verbose=1)
model.learn(total_timesteps=200000)

obs = env.reset()
for i in range(len(df['Date'])):
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render(title='MSF')
