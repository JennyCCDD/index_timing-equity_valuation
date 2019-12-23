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

indexlist = ['ERP','EP', 'BP', 'SP', 'CFP']
codelist = ['000300', '000905', '000016']
stagelist = [1,2,3,4]#['主动去库存','被动去库存','主动补库存','被动补库存']


class Para:
    stage = stagelist[1]
    path_data = '.\\input\\'
    path_results = '.\\output\\'
para = Para()
#f = open(para.path_results + 'result', 'w')


#分阶段考虑
for c in stagelist:
    if c == 1:
        stage = '主动去库存'
    elif c == 2:
        stage = '被动去库存'
    elif c == 3:
        stage = '主动补库存'
    elif c == 4:
        stage = '被动补库存'
    else:
        pass
    for i in indexlist:
        for j in codelist:
            datas_filename = para.path_data + '%s' % j + '_' + '%s' % i + '.xlsx'
            datas = pd.read_excel(datas_filename, index_col=0, parse_dates=True)
            datas_minus_signal = pd.DataFrame(datas[datas.signal == c],columns = datas.columns)
            datas_minus_signal = pd.DataFrame(datas.iloc[:,2:])
            # step 1:描述性统计分析报告
            profile = datas_minus_signal.profile_report(title='%s' % j + '_' + '%s' % i + '_' + '%s' % stage+ ' Exploratory Data Analysis')
            profile.to_file(
                output_file=para.path_results + '%s' % j + '_' + '%s' % i + '_' + '%s' % stage+ 'Exploratory Data Analysis.html')

            period = 15
            dict_roll = {}
            for k in range(1, datas_minus_signal.columns.size):
                columns_name = datas_minus_signal.columns[k]
                # step 2: 时间序列检验：单位根检验
                adf_result = unitroot_adf(datas_minus_signal.iloc[:, k].dropna())
                adf_result_diff = unitroot_adf(datas_minus_signal.iloc[:, k].diff().dropna())
                print('时间序列检验：单位根检验: %s' % j + '_%s' % i+ '_' + '%s' % stage, columns_name,
                      round(adf_result[0], 4), round(adf_result[4]['5%'], 4))
                print('时间序列检验：单位根检验: %s' % j + '_%s' % i+ '_' + '%s' % stage, columns_name, '同比',
                      round(adf_result_diff[0], 4), round(adf_result_diff[4]['5%'], 4))
                # step 3: 画图
                y = pd.DataFrame(datas_minus_signal.iloc[:, 0]).apply(
                    lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
                X = pd.DataFrame(datas_minus_signal.iloc[:, k]).apply(
                    lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
                figure_count = 1
                plt.figure(figure_count)
                figure_count += 1
                plt.plot(y, 'k-', label='%s' % j+ '_' + '%s' % stage)
                plt.plot(X, 'b-', label='%s' % i + '_' + '%s' % stage+ '%s' % columns_name)
                plt.legend(loc='upper right')
                plt.legend(prop=zhfont1)
                plt.savefig(para.path_results + '%s' % i + '_' +'%s' % j + '_' + '%s' % stage + '%s' % columns_name+ '%d.jpg' % (k))
                plt.close()
                # step 4：时间序列检验：格兰杰因果检验
                x_value = datas_minus_signal.iloc[:, k].diff().dropna().values  # 原来的代码是对环比数据进行格兰杰因果检验
                y = datas_minus_signal.iloc[:, 0]
                y_value = y.loc[datas_minus_signal.iloc[:, k].dropna().index].pct_change().dropna()
                gr_result = grangercausalitytests(np.array([x_value, y_value]).T, maxlag=period, addconst=True,
                                                  verbose=False)
                dict_roll[k] = [gr_result[j + 1][0]['lrtest'][1] for j in range(period)]

                # step 6：输出excel
                y = pd.DataFrame(datas_minus_signal.iloc[:, 0])
                X = pd.DataFrame(datas_minus_signal.iloc[:, k])
                df = pd.merge(y, X, left_index=True, right_index=True)
                #a = (k - 1) * 5    a, '%'
                print(stage, '%s' % j + ':%s' % i + ':%s'% columns_name, round(df.corr().iloc[1, 0],4))
                
                X_name = 'percentile' + '%s' % columns_name + '%'
                df.columns = ['close price', str(X_name)]
                df.index = range(df.shape[0])
                name = '%s' % j + '_' + '%s' % stage + '%' + '%s' % stage+'.xlsx'
                # 需要生成文件的话，取消下行的注释
                df.to_excel(para.path_results + name)

            # 输出p值小于0.05的lag
            pvalue_roll = pd.DataFrame(dict_roll, index=range(1, period + 1))
            for d in pvalue_roll.columns:
                dd = float((d - 1) * 5)
                print(i,j,'%i'% dd + '%', stage, pvalue_roll[(pvalue_roll[d] <= 0.05)].index.tolist())

            # step 5: 找到个阶段各指标时间序列上相关性最大和最小对应的情况
            corr = datas_minus_signal.corr().iloc[:1, :].T
            corr_final = corr.iloc[1:, :]
            corr_final.to_excel(para.path_results + '%s' % j + '_' + '%s' % i + '_corr.xlsx')
            corr_max = corr_final.iloc[:, -1].max()
            corr_min = corr_final.iloc[:, -1].min()
            corr_argmax = corr_final[corr_final.iloc[:, -1] == corr_final.iloc[:, -1].max()].index
            corr_argmin = corr_final[corr_final.iloc[:, -1] == corr_final.iloc[:, -1].min()].index
            print('%s' % j + ':%s' % i + '_' + '%s' % stage+ ':时间序列上相关性最大的是' + corr_argmax, "%.4f" % corr_max)
            print('%s' % j + ':%s' % i + '_' + '%s' % stage+ ':时间序列上相关性最小的是' + corr_argmin, "%.4f" % corr_min)


