#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import pandas as pd
import backtrader as bt
import numpy as np

import datetime  # 用于管理日期时间
import os.path  # 来管理路径
import sys  # 用于找到脚本名称（argv[0]）

# 导入BackTrader平台
import backtrader as bt

start_date,end_date='20070123','20210619'
import tushare as ts
ts.set_token('1eda71057295b5ba834d31d24b572521d24689463e7328ca84fed1d6')
pro = ts.pro_api()
#df = pro.query('daily', ts_code='600519.SH', start_date='20070123',end_date='20210619')
#df = ts.pro_bar(ts_code='600519.SH', adj='hfq', start_date='20070123', end_date='20210619')
df = ts.pro_bar(ts_code='000858.SZ', adj='hfq', start_date=start_date, end_date=end_date)
df = df.set_index(["trade_date"])
df = df.sort_index(ascending=True)
features = df[['open', 'close', 'high', 'low', "vol"]]
features.columns = ['open', 'close', 'high', 'low','volume']
df = features
df.index = pd.to_datetime(df.index, format='%Y%m%d')

df1 = df[:-1]
df2 = df[1:]
df1.index = df2.index
df3 = (df2 - df1) / df1 * 100


#indexs=ts.get_index()[['code','name']]
for index_code in ['000001.SH','000016.SH','000300.SH','399001.SZ','399006.SZ']:
    shangzheng = pro.index_daily(ts_code=index_code, start_date=start_date, end_date=end_date)
    shangzheng = shangzheng[["trade_date","close","amount"]]
    shangzheng = shangzheng.set_index(["trade_date"])
    shangzheng = shangzheng.sort_index(ascending=True)
    shangzheng.index = pd.to_datetime(shangzheng.index, format='%Y%m%d')
    shangzheng.columns = ['close_'+index_code,'amount_'+index_code]
    shangzheng1 = shangzheng[:-1]
    shangzheng2 = shangzheng[1:]
    shangzheng1.index = shangzheng2.index
    shangzheng3 = (shangzheng2 - shangzheng1) / shangzheng1 * 100
    df3 = pd.concat([df3,shangzheng3],axis=1)
df3 = df3.fillna(0,)

CONV_WIDTH = 15
column_indices = {name: i for i, name in enumerate(df.columns)}

n = len(df)
train_df = df3[0:int(n*0.7)]
val_df = df3[int(n*0.7):int(n*0.9)]
test_df = df3[int(n*0.9):]
num_features = df3.shape[1]

# 创建一个策略
class TestStrategy(bt.Strategy):
    params = (
        ('deep', -0.3),
        ('printlog', False),
        ('profit', 0.3),
        ('isA', False),
        ('onlyprintgood', True)
    )

    def log(self, txt, dt=None, doprint=False):
        '''此策略的日志记录功能'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 保存对收盘价线最新数据的引用
        self.dataclose = self.datas[0].close
        # 跟踪待处理订单和买入价格/佣金
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.init_cash = self.broker.getvalue()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 做多/做空 订单 已提交/已执行 到/被代理 - 无事可做
            return

        # 检查订单是否已经完成
        # 注意：如果没有足够资金，代理可能拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # 做空
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # 检查订单是否挂起。。。如果是，我们无法发送第二个
        if self.order:
            return
        import numpy as np
        if len(self) > CONV_WIDTH + 1:
            x = np.zeros(shape=(CONV_WIDTH, num_features))
            for i in range(CONV_WIDTH):
                self.log([self.datas[1].l0[0]], doprint=True)
                x[-(i + 1)] = [self.datas[1][i] for i in range(num_features)]
            next_day_p = 0
            # 检查我们是否在市场上
            if not self.position:
                if next_day_p > self.params.deep:
                    # 最大回撤达到deep 买，买，买!!! (应用所有可能的默认参数)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0], doprint=False)

                    # 跟踪创建的订单以避免第二个订单
                    if self.params.isA:
                        size = int(self.broker.getvalue() * 0.95 / self.dataclose[0] / 100) * 100
                    else:
                        size = self.broker.getvalue() * 0.95 / self.dataclose[0]
                    self.order = self.buy(size=size)
            else:
                if next_day_p < -self.params.profit:
                    # 卖，卖，卖!!! (应用所有可能的默认参数)
                    self.log('SELL CREATE, %.2f' % self.dataclose[0], doprint=False)

                    # 跟踪创建的订单以避免第二个订单
                    self.order = self.sell(size=self.position.size)

    def stop(self):
        if self.params.isA:
            self.basesize = int(self.init_cash / self.dataclose[-(len(self) - 1)] / 100) * 100
            self.rest = self.init_cash - self.basesize * self.dataclose[-(len(self) - 1)]
        else:
            self.basesize = self.init_cash / self.dataclose[-(len(self) - 1)] - 0.1
            self.rest = self.init_cash - self.basesize * self.dataclose[-(len(self) - 1)]
        self.basline = self.basesize * self.dataclose[0] + self.rest
        if self.params.onlyprintgood:
            if self.broker.getvalue() / self.init_cash - 1 > self.basline / self.init_cash - 1:
                self.log('(MA deep %f, P %f, profit %f, baseline %f) Ending Value %.2f,baseline Value %.2f' %
                         (self.params.deep, self.params.profit, self.broker.getvalue() / self.init_cash - 1,
                          self.basline / self.init_cash - 1, self.broker.getvalue(), self.basline), doprint=True)
        else:
            self.log('(MA deep %f, P %f, profit %f, baseline %f) Ending Value %.2f,baseline Value %.2f' %
                     (self.params.deep, self.params.profit, self.broker.getvalue() / self.init_cash - 1,
                      self.basline / self.init_cash - 1, self.broker.getvalue(), self.basline), doprint=True)


# 创建一个大脑实例
cerebro = bt.Cerebro()

# 添加一个策略
cerebro.addstrategy(TestStrategy, deep=0.1, profit=0.3, isA=True, printlog=False, onlyprintgood=False)
# 最大回撤达到deep后买入，盈利profit后卖出
# cerebro.optstrategy(
#     TestStrategy,
#     deep=[i/10 for i in range(0, 10)], profit=[i/10 for i in range(0, 10)],isA=True, printlog=False, onlyprintgood=False)


data1 = bt.feeds.PandasData(dataname=df.loc[test_df.index])
data2 = bt.feeds.PandasData(dataname=test_df)

bt.feeds.PandasDirectData

# 把数据槽添加到大脑引擎中
cerebro.adddata(data1)
cerebro.adddata(data2)

# 设定我们希望的初始金额
cerebro.broker.setcash(4000000000.0)

# 根据stake添加一个固定下单量
# cerebro.addsizer(bt.sizers.FixedSize, stake=1)

# 设定佣金为0.1%，去掉百分号除以100
cerebro.broker.setcommission(commission=0.001)

# 运行所有命令
cerebro.run(maxcpus=1)
# cerebro.plot()