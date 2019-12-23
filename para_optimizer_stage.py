# -*- coding: utf-8 -*-

__author__ = "Mengxuan Chen"
__email__  = "chenmx19@mails.tsinghua.edu.cn"
__date__   = "20191222"

import pandas as pd
import numpy as np
from performance_output import performance,graph
from trade_setting import trade
import warnings
warnings.filterwarnings("ignore")

class Para:
    path_data = '.\\input\\'
    path_results = '.\\output\\'
para = Para()
class _optimizer_:
    def __init__(self):
        return
    def Strategy(self,datas,index,test_po,test_ne):
        datas.dropna()
        datas = datas.copy()

        if index == '000300':
            datas['0%EP分位数:ma'] = datas['0%EP分位数'].rolling(test_po).mean()
            datas['5%EP分位数:ma'] = datas['5%EP分位数'].rolling(test_po).mean()
            datas['0%SP分位数:ma'] = datas['0%SP分位数'].rolling(test_po).mean()

            datas['10%SP分位数:ma'] = datas['10%SP分位数'].rolling(test_ne).mean()
            datas['50%SP分位数:ma'] = datas['50%SP分位数'].rolling(test_ne).mean()
            datas['80%SP分位数:ma'] = datas['80%SP分位数'].rolling(test_ne).mean()

            # 主动去库存买入信号
            condition1a = (datas['5%EP分位数'] <= datas['5%EP分位数:ma'])
            condition1b = (datas['5%EP分位数'].shift(1) < datas['5%EP分位数:ma'].shift(1))
            condition1c = (datas['50%SP分位数'] >= datas['50%SP分位数:ma'])
            condition1d = (datas['50%SP分位数'].shift(1) > datas['50%SP分位数:ma'].shift(1))
            datas.loc[condition1a & condition1b&condition1c&condition1d& datas['signal1']==1, 'signal'] = 1
            # 主动去库存卖出信号
            condition1a_ = (datas['5%EP分位数'] >= datas['5%EP分位数:ma'])
            condition1b_ = (datas['5%EP分位数'].shift(1) > datas['5%EP分位数:ma'].shift(1))
            condition1c_ = (datas['50%SP分位数'] <= datas['50%SP分位数:ma'])
            condition1d_ = (datas['50%SP分位数'].shift(1) < datas['50%SP分位数:ma'].shift(1))
            datas.loc[condition1a_ & condition1b_& condition1c_&condition1d_&datas['signal1']==1, 'signal'] = -1
            #被动去库存买入信号
            condition2a = (datas['5%EP分位数'] <= datas['5%EP分位数:ma'])
            condition2b = (datas['5%EP分位数'].shift(1) < datas['5%EP分位数:ma'].shift(1))
            condition2c = (datas['10%SP分位数'] >= datas['10%SP分位数:ma'])
            condition2d = (datas['10%SP分位数'].shift(1) > datas['10%SP分位数:ma'].shift(1))
            datas.loc[condition2a & condition2b&condition2c& condition2d&datas['signal1']==2, 'signal'] = 1
            #被动去库存卖出信号
            condition2a_ = (datas['5%EP分位数'] >= datas['5%EP分位数:ma'])
            condition2b_ = (datas['5%EP分位数'].shift(1) > datas['5%EP分位数:ma'].shift(1))
            condition2c_ = (datas['10%SP分位数'] <= datas['10%SP分位数:ma'])
            condition2d_ = (datas['10%SP分位数'].shift(1) < datas['10%SP分位数:ma'].shift(1))
            datas.loc[condition2a_ & condition2b_&condition2c_& condition2d_&datas['signal1']==2, 'signal'] = -1

            # 主动补库存买入信号
            condition3a = (datas['0%EP分位数'] >= datas['0%EP分位数:ma'])
            condition3b = (datas['0%EP分位数'].shift(1) > datas['0%EP分位数:ma'].shift(1))
            condition3c = (datas['10%SP分位数'] <= datas['10%SP分位数:ma'])
            condition3d = (datas['10%SP分位数'].shift(1) < datas['10%SP分位数:ma'].shift(1))
            datas.loc[condition3a & condition3b &condition3c&condition3d& datas['signal1']==3, 'signal'] = 1
            # 主动补库存卖出信号
            condition3a_ = (datas['0%EP分位数'] <= datas['0%EP分位数:ma'])
            condition3b_ = (datas['0%EP分位数'].shift(1) < datas['0%EP分位数:ma'].shift(1))
            condition3c_ = (datas['10%SP分位数'] >= datas['10%SP分位数:ma'])
            condition3d_ = (datas['10%SP分位数'].shift(1) > datas['10%SP分位数:ma'].shift(1))
            datas.loc[condition3a_ & condition3b_ & condition3c_&condition3d_&datas['signal1']==3, 'signal'] = 1

            # 被动补库存买入信号
            condition4a = (datas['0%SP分位数'] >= datas['0%SP分位数:ma'])
            condition4b = (datas['0%SP分位数'].shift(1) > datas['0%SP分位数:ma'].shift(1))
            condition4c = (datas['80%SP分位数'] <= datas['80%SP分位数:ma'])
            condition4d = (datas['80%SP分位数'].shift(1) < datas['80%SP分位数:ma'].shift(1))
            datas.loc[condition4a & condition4b&condition4c&condition4d & datas['signal1']==4, 'signal'] = 1

            # 被动补库存卖出信号
            condition4a_ = (datas['0%SP分位数'] <= datas['0%SP分位数:ma'])
            condition4b_ = (datas['0%SP分位数'].shift(1) < datas['0%SP分位数:ma'].shift(1))
            condition4c_ = (datas['80%SP分位数'] >= datas['80%SP分位数:ma'])
            condition4d_ = (datas['80%SP分位数'].shift(1) > datas['80%SP分位数:ma'].shift(1))
            datas.loc[condition4a_ & condition4b_&condition4c_&condition4d_ & datas['signal1']==4, 'signal'] = 1

            #print(datas)
            # 交易
            datas_trade, transactions_trade = trade(datas)
            # 交易表现
            stats = performance(transactions_trade, datas_trade)
        return

if __name__ == '__main__':
    codelist = ['000300', '000905', '000016']
    for index_ in codelist:
        print('_______________________%s'%index_+'.SH__________________________')
        sheetindex = '%s'%index_+'_日频'
        datas = pd.read_excel(para.path_data+ 'backtestdata.xlsx', sheet_name=sheetindex,
                              index_col=0, parse_dates=True)
        datas['pre_close']=datas['close'].shift()
        #dropna(how='all')整列是空值时才会被删除  #print(datas.columns)
        indicators= datas.columns.tolist()
        indicators.remove('signal1')
        indicators.remove('signal2')
        indicators.remove('close')
        indicators.remove('pre_close')
        #print(indicators)
        _optimizer_().Strategy(datas,index_,5,60)


