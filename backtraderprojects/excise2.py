#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime  # 用于管理日期时间
import os.path  # 来管理路径
import sys  # 用于找到脚本名称（argv[0]）

# 导入BackTrader平台
import backtrader as bt

# 创建一个策略
class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        '''此策略的日志记录功能'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # 保存对收盘价线最新数据的引用
        self.dataclose = self.datas[0].close

        # 跟踪待处理订单和买入价格/佣金
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # 添加简单移动平均指标
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

        # 用于绘图的指标
        bt.indicators.ExponentialMovingAverage(self.datas[0], period=25)
        bt.indicators.WeightedMovingAverage(self.datas[0], period=25,
                                            subplot=True)
        bt.indicators.StochasticSlow(self.datas[0])
        bt.indicators.MACDHisto(self.datas[0])
        rsi = bt.indicators.RSI(self.datas[0])
        bt.indicators.SmoothedMovingAverage(rsi, period=10)
        bt.indicators.ATR(self.datas[0], plot=False)

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
        # 引用的收盘价的日志
        self.log('Close, %.2f' % self.dataclose[0])

        # 检查订单是否挂起。。。如果是，我们无法发送第二个
        if self.order:
            return

        # 检查我们是否在市场上
        if not self.position:
            # 还没有。。。我们可能会做多如果。。。
            if self.dataclose[0] > self.sma[0]:
                # 买，买，买!!! (应用所有可能的默认参数)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # 跟踪创建的订单以避免第二个订单
                self.order = self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                # 卖，卖，卖!!! (应用所有可能的默认参数)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                # 跟踪创建的订单以避免第二个订单
                self.order = self.sell()


if __name__ == '__main__':
    # 创建一个大脑实例
    cerebro = bt.Cerebro()

    # 添加一个策略
    cerebro.addstrategy(TestStrategy)

    # 数据保存在样本的一个子文件夹中。我们需要找到脚本的位置
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../../datas/orcl-1995-2014.txt')

    # 创建一个数据槽
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # 不接收这个日期更早的数据
        fromdate=datetime.datetime(2000, 1, 1),
        # 不接收晚于这个日期的数据
        todate=datetime.datetime(2000, 12, 31),
        reverse=False)

    data = bt.feeds.YahooFinanceData(dataname='MSFT',
                                     fromdate=datetime.datetime(2020, 12, 1,0,0,0),
                                     todate=datetime.datetime(2021, 5, 25,0,0,0))

    import pandas as pd
    df = pd.read_csv('./samples/candlestick1')
    df.index = pd.to_datetime(df.pop('id'), unit='s')
    df.columns = ['high','low','open','close','volume','Adjusted_Close']
    df.pop('Adjusted_Close')
    df = df.sort_index()
    df = df[-500:]
    print(df.head())
    data = bt.feeds.PandasData(dataname=df)


    # 把数据槽添加到大脑引擎中
    cerebro.adddata(data)

    # 设定我们希望的初始金额
    cerebro.broker.setcash(100000.0)

    # 根据stake添加一个固定下单量
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # 设定佣金
    cerebro.broker.setcommission(commission=0.001)

    # 打印起始条件
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # 运行所有命令
    cerebro.run()

    # 打印最终结果
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()

