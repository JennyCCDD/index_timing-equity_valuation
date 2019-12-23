# -*- coding: utf-8 -*-

__author__ = "Mengxuan Chen"
__email__  = "chenmx19@mails.tsinghua.edu.cn"
__date__   = "20191216"

import pandas as pd
import numpy as np
from performance_output import performance,performance_anl
from trade_setting import trade
import warnings
warnings.filterwarnings("ignore")

class Para:
    path_data = '.\\input\\'
    path_results = '.\\output\\'
para = Para()
class _optimizer_:
    def __init__(self):
        self.para = 7
        self.indica = '25%SP分位数'
        return
    def Strategy(self,datas):
        datas.dropna()
        datas = datas.copy()
        corr = datas['%s' % self.indica].corr(datas['close'])
        if corr > 0:
            datas['corr_dir'] = 1
        else:
            datas['corr_dir'] = -1
        datas['%s' % self.indica + ':ma'] = datas[self.indica].rolling( self.para).mean()
        # 买入信号
        condition1a = (datas[self.indica] >= datas['%s' % self.indica + ':ma'])
        condition1b = (datas[self.indica].shift(1) > datas['%s' % self.indica + ':ma'].shift(1))
        datas.loc[condition1a & condition1b, 'signal'] = 1 *datas['corr_dir']
        # 卖出信号
        condition1a = (datas[self.indica] <= datas['%s' % self.indica + ':ma'])
        condition1b = (datas[self.indica].shift(1) < datas['%s' % self.indica + ':ma'].shift(1))
        datas.loc[condition1a & condition1b, 'signal'] = -1 * datas['corr_dir']
        #把小于0的部分全部替换W为0
        datas['signal'] = np.maximum(datas['signal'], 0)
        # 交易
        datas_trade, transactions_trade = trade(datas)
        # 交易表现
        stats = performance(transactions_trade, datas_trade)
        stats_anl = performance_anl(transactions_trade, datas_trade)
        return stats, stats_anl

if __name__ == '__main__':
    index = '000300'#, '000905', '000016']
    sheetindex = '%s'%index+'_日频'
    datas = pd.read_excel(para.path_data+ 'backtestdata.xlsx', sheet_name=sheetindex,
                              index_col=0, parse_dates=True)
    datas['pre_close']=datas['close'].shift()
    #dropna(how='all')整列是空值时才会被删除  #print(datas.columns)
    _optimizer_().Strategy(datas)


