# -*- coding: utf-8 -*-

__author__ = "Mengxuan Chen"
__email__  = "chenmx19@mails.tsinghua.edu.cn"
__date__   = "20191216"

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
        self.test_range_po = range(5, 22, 1)
        self.test_range_ne = range(60,120,3)
        return
    def Strategy(self,datas,index):
        datas.dropna()
        datas = datas.copy()

        for indica in indicators:
            corr = datas['%s' % indica ].corr(datas['close'])
            if corr >0:
                datas['corr_dir'] = 1
                test_range = self.test_range_po
            else:
                datas['corr_dir'] = -1
                test_range = self.test_range_ne
            stats_list = []

            for paratest in test_range:
                datas['%s' % indica + ':ma'] = datas[indica].rolling(paratest).mean()
                # 买入信号
                condition1a = (datas[indica] >= datas['%s' % indica + ':ma'])
                condition1b = (datas[indica].shift(1) > datas['%s' % indica + ':ma'].shift(1))
                datas.loc[condition1a & condition1b, 'signal'] = 1 *datas['corr_dir']
                # 卖出信号
                condition1a = (datas[indica] <= datas['%s' % indica + ':ma'])
                condition1b = (datas[indica].shift(1) < datas['%s' % indica + ':ma'].shift(1))
                datas.loc[condition1a & condition1b, 'signal'] = -1 * datas['corr_dir']
                #把小于0的部分全部替换W为0
                datas['signal'] = np.maximum(datas['signal'], 0)
                # 交易
                datas_trade, transactions_trade = trade(datas)
                datas_trade.to_csv(para.path_results + 'index:%s' % index + '_%s' % paratest +
                                   '_%s' % indica + '.csv')
                # 交易表现
                stats = performance(transactions_trade, datas_trade)
                graph(index, paratest, indica, datas_trade)
                stats.index = ['para_ %s' % paratest]
                # stats.tolist();stats.insert(0,indica)
                stats_list.append(stats.ix[0])
            stats_all = pd.DataFrame(stats_list)
            stats_all.columns = ['Sharp', 'RetYearly', 'WinRate',
                                 'MDD', 'maxlossOnce', 'num', 'R2VaR', 'R2CVaR']
            #stats_all.to_csv(para.path_results + "indicator_%s" % indica + '.csv')
            stats_all.to_csv(para.path_results + 'index_%s'%index+"indicator_%s" % indica + stats_all['RetYearly'].argmax() + '.csv')
            print('index:%s'%index+"indicator:%s" % indica, stats_all['RetYearly'].argmax())
            print(stats_all.ix[stats_all['RetYearly'].argmax()].T)
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
        _optimizer_().Strategy(datas,index_)


