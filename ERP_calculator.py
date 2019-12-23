# -*- coding: utf-8 -*-

__author__ = "Mengxuan Chen"
__email__  = "chenmx19@mails.tsinghua.edu.cn"
__date__   = "20191130"

#--* pakages*--
import pandas as pd

#--* parameters*--
class Para:
    path_data = '.\\input\\'
    path_results = '.\\output\\'
para = Para()
codelist = [str('000300'), str('000905'), str('000016')]

#--* loop the calculation*--
for i in codelist:
#%% read the datas
    ERP_source = pd.read_excel(para.path_data+'INPUT.xlsx',sheet_name= '%s'%i+ '_日频ERP',index_col=0)
    signal_source = pd.read_excel(para.path_data + 'INPUT.xlsx', sheet_name='%s'%i + '_月频XP分位数', index_col=0)

    #%% calculate the daily return of the index and load the risk free rate
    ### risk free rate is the yiled to maturity of the 10-years treasury
    hist_return = ERP_source['close'].pct_change()
    rf_data = ERP_source['treasurybond_ytm_10']

    #%% descriptive anlaysis
    describe = hist_return.describe()
    print(describe)

    #%% calculate total ERP
    ret_mu = hist_return.mean()*252
    rf_mu = rf_data.mean()
    erp_mu_all = ret_mu-rf_mu


    ret_gmu = (1+hist_return).cumprod().iloc[-1]**(252/hist_return.count())-1
    rf_gmu = (1+rf_data).cumprod().iloc[-1]**(1/rf_data.count())-1 #注意：无风险利率已经年化
    erp_gmu_all = ret_gmu-rf_gmu

    print('算术平均历史ERP',round(erp_mu_all,4))
    print('几何平均历史ERP',round(erp_gmu_all,4))

    #%% calculate rolling historical ERP
    ### attention: time paramters need sensitive test
    a = 252
    erp_data = pd.DataFrame(index = ERP_source.index)

    ret_mu_roll = hist_return.rolling(a).mean()*252
    rf_mu_roll = rf_data.rolling(a).mean() #attention: risk free rate has already been annulized
    mu_roll = ret_mu_roll-rf_mu_roll
    erp_data['ERP:mu_roll_anl'] =mu_roll
    #mu_roll_df = pd.DataFrame(mu_roll,columns=['mu_roll_anl'])
    #mu_roll_df.dropna(inplace = True)
    #print('算术平均滚动历史ERP',mu_roll_df)


    ret_gmu_roll=pd.DataFrame()
    for i in range(hist_return.index.size):
        hist_r = pd.DataFrame(hist_return[i:i+a])
        ret_gmu_roll[i] = (1+hist_r).cumprod().iloc[-1]**(252/hist_r.count())-1

    rf_gmu_roll=pd.DataFrame()
    for i in range(rf_data.index.size-1):
        rf_d = pd.DataFrame(rf_data[i+1:i+1+a])
        rf_gmu_roll[i] = (1+rf_d).cumprod().iloc[-1]**(1/rf_d.count())-1
        #attention: risk free rate has already been annulized

    gmu_roll_df = pd.DataFrame()
    gmu_roll_df = pd.concat([ret_gmu_roll,rf_gmu_roll],axis = 0)
    gmu_roll_df = gmu_roll_df.T

    gmu_roll_df.columns = ['EP','rf']
    erp_data['ERP: gmu_roll_anl'] = gmu_roll_df['EP'].values - gmu_roll_df['rf'].values


    #%% calculate rolling forward ERP
    erp_init = ERP_source['ERP_init']
    erp_roll = erp_init.rolling(a).mean()
    erp_data['ERP:implied'] =erp_init
    erp_data['ERP:implied_roll_anl'] =erp_roll

    #%% frequenccy is monthly set
    erp_data['signal'] = signal_source['signal1'].loc[erp_data.index]
    erp_data['signal2'] = signal_source['signal2'].loc[erp_data.index]
    erp_data['close'] = ERP_source['close'].loc[erp_data.index]
    erp_data_m = erp_data.resample('M').last()
    #erp_data_m.fillna(method = ffill, inplace=True)
    #print(erp_data.tail())
    #erp_data.to_excel(para.path_data+ '%s' % i + '_ERP_daily.xlsx')
    erp_data_m.to_excel(para.path_data + '%s' % i + '_ER_.xlsx')

