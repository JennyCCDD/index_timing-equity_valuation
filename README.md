# index_timing-equity_valuation

在这篇报告中，我们运用了股权风险溢价模型、相对估值模型这两个权益市场估值模型对沪深300（000300.SH）、中证500（000905.SH）、上证50（000016.SH）
这三个指数进行了指标构建和筛选，并进行了择时研究。

回测方式为纯多头策略，我们将长周期指标设置为反转指标，将短周期指标设置为趋势指标；
调仓价为前收盘价，调仓手续费为单边千三，印花税为单边千一；
调仓频率为天；
通过调整参数对指标择时效果进行遍历性测试。

首先，我们将简单加权平均的历史滚动股权风险溢价模型拓展到几何加权平均的历史滚动股权风险溢价，将隐含股权风险溢价模型拓展到滚动加权隐含股权风险溢价模型，计算它们与三个指数的时间序列上的相关系数，发现在几何加权平均的情况下，历史滚动股权风险溢价与指数收盘价的相关性由正相关变为更强的负相关，在简单加权平均下，隐含股权风险溢价与指数收盘价的负相关更强（除沪深300几乎不变以外）。在择时检验中，沪深300指数的表现最好，其中隐含ERP单指标策略（移动平均参数为78天）的年化收益率可以达到16.90%、夏普比率可以达到0.94，简单加权平均历史滚ERP单指标策略（移动平均参数为102天）的年化收益率可以达到15.87%、夏普比率可以达到0.91。股权风险溢价指标在上证50指数上的表现次于沪深300。简单加权平均的隐含ERP单指标策略在三大指数的策略胜率上表现都比较好，分别可以达到75%、60%、50%。

在相对估值模型中，我们将简单的相对估值模型拓展到研究指数成分股相对估值指标分位数表现与收盘价之间关系，其中分位数的范围是0%至100%，步长为5%。我们发现，将XP分位数细化后得出的结论更加丰富。其中，SP分位数的表现比较突出，25%SP分位数（移动平均参数为96天）对沪深300择时的年化收益率为13.00%、夏普比率为0.7003、胜率为65.22%；20%SP分位数（移动平均参数为90天）对中证500择时的年化收益率为6.02%、夏普比率为0.3287、胜率为61.11%；60%SP分位数（移动平均参数为105天）对上证50择时的年化收益率为12.24%、夏普比率为0.6621、胜率为61.54%。偏中低排序的SP分位数之所以能取得这样的表现，一方面，与销售收入往往难以被操纵或扭曲有关系，另一方面，可能与每股销售收入相对较小的公司更能反映指数真实投资价值有关。
