# -*- coding: utf-8 -*-

__author__ = "Mengxuan Chen"
__email__  = "chenmx19@mails.tsinghua.edu.cn"
__date__   = "20191130"

#--* pakages*--
import pandas as pd
import numpy as np
# 交易费用函数，双边都是万三
def trade_fee_buy(share, price):
    commission = share * price * 0.003
    transfer = share / 1000
    if share < 1000:
        transfer = 1
    return round(commission + transfer, 2)
def trade_fee_sell(share, price):
    tax = share * price * 0.001
    commission = share * price * 0.003
    transfer = share / 1000
    if share < 1000:
        transfer = 1
    return round(commission + transfer + tax, 2)

def trade(datas):
    # 设置仓位（未考虑跌停）
    datas['position'] = datas['signal'].shift()
    datas['position'].fillna(method='ffill', inplace=True)
    datas['position'].fillna(value=0, inplace=True)
    # 设定参数
    # 初始仓位
    initial_cash = 1000000
    datas.at[datas.index[0], 'hold_num'] = 0
    datas.at[datas.index[0], 'index_value'] = 0
    datas.at[datas.index[0], 'actual_position'] = 0
    datas.at[datas.index[0], 'cash'] = initial_cash
    datas.at[datas.index[0], 'asset'] = initial_cash
    datas = datas.fillna(datas.mean(axis=1))

    pricein = []
    priceout = []

    for i in range(1, datas.shape[0]):
        hold_num = datas.at[datas.index[i - 1], 'hold_num']
        if datas.at[datas.index[i], 'position'] != datas.at[datas.index[i - 1], 'position']:
            theory_num = int(
                datas.at[datas.index[i - 1], 'asset'] * datas.at[datas.index[i], 'position'] /
                datas.at[datas.index[i], 'pre_close'])
            if theory_num >= hold_num:
                buy_num = int((theory_num - hold_num) / 100) * 100
                buy_cash = buy_num * datas.at[datas.index[i], 'pre_close']

                datas.at[datas.index[i], 'hold_num'] = hold_num + buy_num
                datas.at[datas.index[i], 'cash'] = datas.at[datas.index[i - 1], 'cash'] - \
                                                   buy_cash - trade_fee_buy(buy_num,
                                                                            datas.at[datas.index[i], 'pre_close'])
                date_in = datas.index[i]
                price_in = datas.close[i]
                pricein.append([date_in, price_in])
            else:
                sell_num = hold_num - theory_num
                sell_cash = sell_num * datas.at[datas.index[i], 'pre_close']
                datas.at[datas.index[i], 'hold_num'] = hold_num - sell_num
                datas.at[datas.index[i], 'cash'] = datas.at[datas.index[i - 1], 'cash'] + sell_cash - trade_fee_sell(
                    sell_num, datas.at[datas.index[i], 'pre_close'])
                date_out = datas.index[i]
                price_out = datas.close[i]
                priceout.append([date_out, price_out])
        else:
            datas.at[datas.index[i], 'hold_num'] = hold_num
            datas.at[datas.index[i], 'cash'] = datas.at[datas.index[i - 1], 'cash']
        datas.at[datas.index[i], 'index_value'] = datas.at[datas.index[i], 'hold_num'] * datas.at[
            datas.index[i], 'close']
        datas.at[datas.index[i], 'asset'] = datas.at[datas.index[i], 'cash'] + datas.at[datas.index[i], 'index_value']
        datas.at[datas.index[i], 'actual_position(%)'] = datas.at[datas.index[i], 'index_value'] / datas.at[
            datas.index[i], 'asset']

    p1 = pd.DataFrame(pricein, columns=['datebuy', 'pricebuy'])
    p2 = pd.DataFrame(priceout, columns=['datesell', 'pricesell'])
    transactions = pd.concat([p1, p2], axis=1)

    # print(transactions.head())

    # 计算基准收益
    datas = datas.fillna(datas.mean(axis=0))
    theory_share = int(initial_cash / (datas.at[datas.index[0], 'pre_close'] * 100)) * 100
    cash_value = initial_cash - theory_share * datas.at[datas.index[0], 'pre_close'] - trade_fee_buy(theory_share,
                                                                                                     datas.at[
                                                                                                         datas.index[
                                                                                                             0], 'pre_close'])
    datas['benchmark'] = theory_share * datas['close'] + cash_value
    datas['nav'] = datas['asset']
    datas['ret'] = datas['nav'].pct_change(1).fillna(0)
    return datas, transactions