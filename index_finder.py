# -*- coding: utf-8 -*-

__author__ = "Mengxuan Chen"
__email__  = "chenmx19@mails.tsinghua.edu.cn"
__date__   = "20191130"

#--* pakages*--
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.stats.diagnostic import unitroot_adf
import pandas_profiling
zhfont1 = matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\msyh.ttf')
indexlist = ['EP', 'BP', 'SP', 'CFP','ERP']
codelist = ['000300', '000905', '000016']

class Para:
    path_data = '.\\input\\'
    path_results = '.\\output\\'


para = Para()
#f = open(para.path_results + 'result', 'w')

for i in indexlist:
    for j in codelist:
        file_name = para.path_data + str(i) + '.csv'
        datas_filename = para.path_data + '%s' % j + '_' + '%s' % i + '.xlsx'
        datas = pd.read_excel(datas_filename, index_col=0, parse_dates=True)
        datas_minus_signal = pd.DataFrame(datas.iloc[:,2:])

        #step 1:描述性统计分析报告
        profile = datas_minus_signal.profile_report(title = '%s' % j + '_' + '%s' % i +' Exploratory Data Analysis')
        profile.to_file(output_file = para.path_results+ '%s' % j + '_' + '%s' % i +'Exploratory Data Analysis.html')

        period = 30
        dict_roll = {}
        dict_aic = {}
        dict_bic = {}
        for k in range(1,datas_minus_signal.columns.size):
            columns_name = datas_minus_signal.columns[k]
            # step 2: 时间序列检验：单位根检验
            adf_result = unitroot_adf(datas_minus_signal.iloc[:,k].dropna())
            adf_result_diff = unitroot_adf(datas_minus_signal.iloc[:,k].diff().dropna())
            print('时间序列检验：单位根检验: %s' % j + '_%s' % i,columns_name,
                  round(adf_result[0],4), round(adf_result[4]['5%'],4))
            print('时间序列检验：单位根检验: %s' % j + '_%s' % i,columns_name,'同比',
                  round(adf_result_diff[0],4),round(adf_result_diff[4]['5%'],4))
            # step 3: 画图
            y = pd.DataFrame(datas_minus_signal.iloc[:, 0]).apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
            X = pd.DataFrame(datas_minus_signal.iloc[:, k]).apply(
                lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
            figure_count = 1
            plt.figure(figure_count)
            figure_count += 1
            plt.plot(y, 'k-', label='%s' % j)
            plt.plot(X, 'b-', label='%s' % i + '%s' % columns_name)
            plt.legend(loc='upper right')
            plt.legend(prop=zhfont1)
            kk =(k-1)*5
            plt.savefig(para.path_results + '%s' % i +'%s' % j+'%i'%kk +'% '+ ' %d.jpg'%(k))
            plt.close()
            #plt.show()
            # step 4：时间序列检验：格兰杰因果检验
            x_value = datas_minus_signal.iloc[:,k].diff().dropna().values   #原来的代码是对环比数据进行格兰杰因果检验
            y = datas_minus_signal.iloc[:,0]
            y_value = y.loc[datas_minus_signal.iloc[:,k].dropna().index].pct_change().dropna()
            gr_result = grangercausalitytests(np.array([x_value, y_value]).T, maxlag=period, addconst=True,
                                              verbose=False)
            dict_roll[k] = [gr_result[j + 1][0]['lrtest'][1] for j in range(period)]
            dict_aic[k] = [gr_result[j + 1][1][1].aic for j in range(period)]
            dict_bic[k] = [gr_result[j + 1][1][1].bic for j in range(period)]
        # 输出p值小于0.05的lag
        pvalue_roll = pd.DataFrame(dict_roll, index=range(1, period + 1))
        aic_implied = pd.DataFrame(dict_aic, index=range(1, period + 1))
        bic_implied = pd.DataFrame(dict_bic, index=range(1, period + 1))
        for d in pvalue_roll.columns:
            dd = float((d-1)*5)
            print(i,j,'%i'% dd + '%', pvalue_roll[(pvalue_roll[d] <= 0.05)].index.tolist(),
                  [aic_implied[d].idxmin(), bic_implied[d].idxmin()])
        #step 5: 找到个阶段各指标时间序列上相关性最大和最小对应的情况
        corr=datas_minus_signal.corr().iloc[:1,:].T
        corr_final=corr.iloc[1:,:]
        corr_final.to_excel(para.path_results+'%s' % j + '_' + '%s' % i + '_corr.xlsx')
        corr_max=corr_final.iloc[:,-1].max()
        corr_min=corr_final.iloc[:,-1].min()
        corr_argmax = corr_final[corr_final.iloc[:,-1] == corr_final.iloc[:,-1].max()].index
        corr_argmin = corr_final[corr_final.iloc[:, -1] == corr_final.iloc[:, -1].min()].index
        print('%s'%j +':%s'% i+':时间序列上相关性最大的是'+corr_argmax,"%.4f" % corr_max)
        print('%s'%j +':%s'% i+':时间序列上相关性最小的是'+corr_argmin,"%.4f" % corr_min)

