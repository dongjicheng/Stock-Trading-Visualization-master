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
        ('deep', -0.3),
        ('printlog', False),
        ('profit',0.3),
        ('isA', False),
        ('onlyprintgood',True)
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
        # 引用的收盘价的日志
        self.log('Close, %.2f' % self.dataclose[0])

        # 检查订单是否挂起。。。如果是，我们无法发送第二个
        if self.order:
            return

        # 检查我们是否在市场上
        if not self.position:
            if (self.dataclose[0] - max(self.dataclose)) / max(self.dataclose) <= self.params.deep:
                # 最大回撤达到deep 买，买，买!!! (应用所有可能的默认参数)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # 跟踪创建的订单以避免第二个订单
                if self.params.isA:
                    size = int(self.broker.getvalue()*0.9 / self.dataclose[0]/100)*100
                else:
                    size =self.broker.getvalue()*0.9/self.dataclose[0]-0.1
                self.order = self.buy(size=size)
        else:
            # 已经在市场，我们可能需要做空
            if (self.dataclose[0] - self.position.price) / self.position.price >= self.params.profit:
                # 卖，卖，卖!!! (应用所有可能的默认参数)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # 跟踪创建的订单以避免第二个订单
                self.order = self.sell(size=self.position.size)

    def stop(self):
        if self.params.isA:
            self.basesize = int(self.init_cash / self.dataclose[-(len(self)-1)] / 100) * 100
            self.rest = self.init_cash- self.basesize * self.dataclose[-(len(self)-1)]
        else:
            self.basesize = self.init_cash / self.dataclose[-(len(self)-1)] - 0.1
            self.rest = self.init_cash - self.basesize * self.dataclose[-(len(self)-1)]
        self.basline = self.basesize * self.dataclose[0] + self.rest
        if self.params.onlyprintgood:
            if self.broker.getvalue()/self.init_cash - 1 > self.basline/self.init_cash - 1:
                self.log('(MA deep %f, P %f, profit %f, baseline %f) Ending Value %.2f,baseline Value %.2f' %
                     (self.params.deep, self.params.profit, self.broker.getvalue()/self.init_cash - 1,self.basline/self.init_cash - 1, self.broker.getvalue(),self.basline), doprint=True)
        else:
            self.log('(MA deep %f, P %f, profit %f, baseline %f) Ending Value %.2f,baseline Value %.2f' %
                     (self.params.deep, self.params.profit, self.broker.getvalue() / self.init_cash - 1,
                      self.basline / self.init_cash - 1, self.broker.getvalue(), self.basline), doprint=True)


if __name__ == '__main__':
    # 创建一个大脑实例
    cerebro = bt.Cerebro()

    # 添加一个策略(最大跌幅超过deep买，买入后盈利超过profit卖)
    cerebro.addstrategy(TestStrategy,deep=-0.15, profit=0.4, isA=True, printlog=False, onlyprintgood=False)
    #最大回撤达到deep后买入，盈利profit后卖出
    # cerebro.optstrategy(
    #     TestStrategy,
    #     deep=[-i/10 for i in range(1, 9)], profit=[i/10 for i in range(1, 100)], isA=True, printlog=False, onlyprintgood=True)
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


    import pandas as pd
    df = pd.read_csv('./samples/candlestick1')
    df.index = pd.to_datetime(df.pop('id'), unit='s')
    df.columns = ['high','low','open','close','volume','Adjusted_Close']
    df.pop('Adjusted_Close')
    df = df.sort_index()
    df1 = df[-345:]

    import tushare as ts
    ts.set_token('1eda71057295b5ba834d31d24b572521d24689463e7328ca84fed1d6')
    pro = ts.pro_api()
    df = pro.query('daily', ts_code='600519.SH', start_date='20070123',end_date='20181231')
    df = df.set_index(["trade_date"])
    df = df.sort_index(ascending=True)
    features_considered = ['open', 'close', 'high', 'low', "vol"]
    features = df[features_considered]
    features.columns = ['open', 'close', 'high', 'low','volume']
    df = features
    df.index = pd.to_datetime(df.index, format='%Y%m%d')

    data = bt.feeds.PandasData(dataname=df)

    # 把数据槽添加到大脑引擎中
    cerebro.adddata(data)

    # 设定我们希望的初始金额
    cerebro.broker.setcash(400000.0)

    # 根据stake添加一个固定下单量
    #cerebro.addsizer(bt.sizers.FixedSize, stake=1)

    # 设定佣金为0.1%，去掉百分号除以100
    cerebro.broker.setcommission(commission=0.001)

    # 运行所有命令
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DW')
    results = cerebro.run(maxcpus=1)
    strat = results[0]
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('SR:', strat.analyzers.SharpeRatio.get_analysis())
    print('DW:', strat.analyzers.DW.get_analysis())

    cerebro.plot()
