#!/usr/bin/env python
# -*- coding: utf-8 -*-
from huobi.client.market import MarketClient
from huobi.client.generic import GenericClient
import numpy as np
import pandas as pd

DECAYE = 1-0.0015


def floyd1(matrix: pd.DataFrame, mode='max'):
    final = matrix.copy()
    path = matrix.copy().astype(np.str)
    for i in path.columns:
        for j in path.columns:
            path[i][j] = "{}->{}".format(i,j)
    for k in final.columns:
        for i in final.columns:
            for j in final.columns:
                if final[i][k] * final[k][j] * DECAYE > final[i][j]:
                    final[i][j] = final[i][k] * final[k][j] * DECAYE
                    path[i][j] = path[i][k] + "->" + path[k][j] if path[i][k].split('->')[-1] != path[k][j].split('->')[0] else '->'.join(path[i][k].split('->')[:-1]) + "->" + '->'.join(path[k][j].split('->')[1:])
    print(matrix)
    print(final)
    print(path)
    return final, path


def showDistances1(final, path):
    for i in final.columns:
        builder = ''
        for j in final.columns:
            builder += i + '->' + j + ',distance: ' + str(final[i][j]) + ':' + path[i][j] + "\n"
        print(builder)


def floyd(matrix: pd.DataFrame, mode='max'):
    final = matrix.copy()
    path = matrix.copy().astype(np.str)
    for i in path.columns:
        for j in path.columns:
            path[i][j] = j
    for k in final.columns:
        for i in final.columns:
            for j in final.columns:
                if final[i][k] * final[k][j] * DECAYE > final[i][j]:
                    final[i][j] = final[i][k] * final[k][j] * DECAYE
                    path[i][j] = path[i][k]
    return final, path


def showDistances(final, path, mode='value'):
    #mode all/diag/value
    for i in final.columns:
        builder = ''
        for j in final.columns:
            if mode == 'diag':
                if i == j:
                    builder += i + '->' + j + ',distance: ' + str(final[i][j]) + ':' + i
                    import sys
                    print(builder, file=sys.stderr)
                    temp = path[i][j]
                    while temp != j:
                        builder += "->" + temp
                        temp = path[temp][j];
                    builder += "->" + j + "\n"
            elif mode == 'all':
                builder += i + '->' + j + ',distance: ' + str(final[i][j]) + ':' + i
                temp = path[i][j]
                while temp != j:
                    builder += "->" + temp
                    temp = path[temp][j];
                builder += "->" + j + "\n"
            elif mode == 'value':
                if i == j and final[i][j] > 1.0:
                    builder += i + '->' + j + ',distance: ' + str(final[i][j]) + ':' + i
                    import sys
                    print(builder,file=sys.stderr)
                    temp = path[i][j]
                    while temp != j:
                        builder += "->" + temp
                        temp = path[temp][j];
                    builder += "->" + j + "\n"
        print(builder)


def showDistancesFromi2j(final, path, ij=('btc','usdt')):
    i,j = ij
    builder = i + '->' + j + ',distance: ' + str(final[i][j]) + ':' + i
    temp = path[i][j]
    while temp != j:
        builder += "->" + temp
        temp = path[temp][j];
    builder += "->" + j + "\n"
    print(builder)


def symbols2currencies():
    r = {}
    currencis=set()
    generic_client = GenericClient()
    list_obj = generic_client.get_exchange_symbols()
    if len(list_obj):
        for idx, row in enumerate(list_obj):
            if row.state == 'online':
                r[row.symbol]={'from':row.base_currency,'to':row.quote_currency,'state':row.state}
                currencis.add(row.base_currency)
                currencis.add(row.quote_currency)

    market_client = MarketClient(init_log=True)
    list_obj = market_client.get_market_tickers()
    if len(list_obj):
        for idx, row in enumerate(list_obj):
            if row.symbol in r:
                r[row.symbol]['open'] = row.open
                r[row.symbol]['close'] = row.close
                r[row.symbol]['high'] = row.high
                r[row.symbol]['low'] = row.low
    currencis = sorted(list(currencis))[:100]
    #currencis = ['btc','usdt','doge','shib']
    matrix = np.zeros(shape=(len(currencis),len(currencis)),dtype=np.float64)
    df = pd.DataFrame(matrix, columns=currencis,index=currencis)
    for key in r:
        if r[key]['from'] in currencis and r[key]['to'] in currencis:
            df[r[key]['from']][r[key]['to']] = r[key]['close'] * DECAYE
            df[r[key]['to']][r[key]['from']] = 1/r[key]['close'] * DECAYE
    return r, floyd(df)


while True:
    s2c, (distance,path) = symbols2currencies()
    showDistances(distance, path,mode='diag')
    #showDistancesFromi2j(distance, path,('btc','usdt'))
    import time
    time.sleep(1)
