# -*- coding: utf-8 -*-
import pandas as pd
import DATA_CONSTANTS as DC
import HullRsiWin_Parameter as Parameter
import os


def set_generator():
    setlist = []
    i = 0
    for n1 in range(15, 36, 5):
        for m1 in range(6, 17, 4):
            #   for m2 in range(3, 15, 3):
            for m2 in [3, 6, 9]:
                # for n in range(3, 16, 3):
                for n in [6, 10, 14, 18]:
                    # for ma_n in range(20, 51, 10):
                    for ma_n in [20, 30, 40, 50]:
                        setname = "Set%d N1_%d M1_%d M2_%d N_%d MaN_%d" % (i, n1, m1, m2, n, ma_n)
                        l = [setname, n1, m1, m2, n, ma_n]
                        setlist.append(l)
                        i += 1

    setpd = pd.DataFrame(setlist, columns=['Setname', 'N1', 'M1', 'M2', 'N', 'MaN'])
    # setpd['RSI1_UP'] = 70
    # setpd['RSI1_DOWN'] = 30

    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    setpd.to_csv(resultpath + Parameter.parasetname)


def stat_multi_symbol_result():
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    multi_symbol_df = pd.read_excel('HullRsiWin_symbol_KMIN_set.xlsx')
    for n, row in multi_symbol_df.iterrows():
        strategy_name = row['strategyName']
        exchange_id = row['exchange_id']
        sec_id = row['sec_id']
        bar_type = row['K_MIN']
        folder_name = "%s %s %s %d\\" % (strategy_name, exchange_id, sec_id, bar_type)
        result_file_name = "%s %s.%s %d finalresults.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        print result_file_name
        result_df = pd.read_csv(folder_name + result_file_name)
        multi_symbol_df.ix[n, 'OprTimes'] = result_df['OprTimes'].mean()
        multi_symbol_df.ix[n, 'Annual_max'] = result_df['Annual'].max()
        multi_symbol_df.ix[n, 'Annual_avg'] = result_df['Annual'].mean()
        multi_symbol_df.ix[n, 'EndCash_avg'] = result_df['EndCash'].mean()
        multi_symbol_df.ix[n, 'EndCash_max'] = result_df['EndCash'].max()
        multi_symbol_df.ix[n, 'own_cash_max_max'] = result_df['max_own_cash'].max()
        multi_symbol_df.ix[n, 'own_cash_max_avg'] = result_df['max_own_cash'].mean()
        multi_symbol_df.ix[n, 'Sharpe_max'] = result_df['Sharpe'].max()
        multi_symbol_df.ix[n, 'SR_avg'] = result_df['SR'].mean()
        multi_symbol_df.ix[n, 'DR_avg'] = result_df['DrawBack'].mean()
        multi_symbol_df.ix[n, 'SingleEarn_avg'] = result_df['MaxSingleEarnRate'].mean()
        multi_symbol_df.ix[n, 'SingleLoss_avg'] = result_df['MaxSingleLossRate'].mean()
        multi_symbol_df.ix[n, 'ProfitLossRate_avg'] = result_df['ProfitLossRate'].mean()
    multi_symbol_df.to_csv('HullRsiWin_symbol_KMIN_set2_result.csv')


def add_max_period_cash_to_finalresult():
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    para_set_list = pd.read_csv('ParameterSet_HullRsi.csv')['Setname'].tolist()
    multi_symbol_df = pd.read_excel('HullRsiWin_symbol_KMIN_set.xlsx')
    for n, row in multi_symbol_df.iterrows():
        strategy_name = row['strategyName']
        exchange_id = row['exchange_id']
        sec_id = row['sec_id']
        bar_type = row['K_MIN']
        folder_name = "%s %s %s %d\\" % (strategy_name, exchange_id, sec_id, bar_type)
        result_file_name = "%s %s.%s %d finalresults.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        # print result_file_name
        result_df = pd.read_csv(folder_name + result_file_name, index_col='Setname')
        for setname in para_set_list:
            set_file_name = "%s %s.%s%d %s result.csv" % (strategy_name, exchange_id, sec_id, bar_type, setname)
            print set_file_name
            set_result = pd.read_csv(folder_name + set_file_name)
            max_own_cash = set_result['own cash'].max()
            result_df.ix[setname, 'max_own_cash'] = max_own_cash
        result_df.to_csv(folder_name + result_file_name)
    pass


def plot_parameter_result_pic():
    """绘制finalresult结果中参数对应的end cash和max own cash的分布柱状图"""
    import matplotlib.pyplot as plt
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    symbol_sellected = pd.read_excel("multi_symbol_1st_xu.xlsx")
    for n , rows in symbol_sellected.iterrows():
        fig = plt.figure(figsize=(6, 12))
        exchange = rows['exchange']
        sec = rows['sec']
        bar_type = rows['bar_type']
        folder_name = "%s %s %s %d\\" % (Parameter.strategyName, exchange, sec, bar_type)
        final_result_file = pd.read_csv(folder_name + "%s %s.%s %d finalresults.csv" % (Parameter.strategyName, exchange, sec, bar_type))
        para_file = pd.read_csv(folder_name + "%s %s %d ParameterSet_HullRsi.csv" % (exchange, sec, bar_type))
        para_name_list = ['N', 'N1', 'M1', 'M2', 'MaN']
        for i in range(len(para_name_list)):
            para_name = para_name_list[i]
            final_result_file[para_name_list] = para_file[para_name_list]
            grouped = final_result_file.groupby(para_name)
            end_cash_grouped = grouped['EndCash'].mean()
            p = plt.subplot(len(para_name_list), 1, i+1)
            p.set_title(para_name)
            p.bar(end_cash_grouped.index.tolist(), end_cash_grouped.values)
            print end_cash_grouped
        fig.savefig('%s %s %s %d_para_distribute.png' % (Parameter.strategyName, exchange, sec, bar_type), dip=500)
    """
    for i in range(1, len(test_data) + 2):
        p = plt.subplot(2, 5, i)
        p.set_title(str(i))
        p.bar([1, 2, 3, 4], test_data_2)

    for i in range(1, len(test_data) + 2):
        p = plt.subplot(2, 5, i + 5)
        p.set_title(str(i))
        p.bar([1, 2, 3, 4], test_data_2)
    """


if __name__ == "__main__":
    # set_generator()
    # stat_multi_symbol_result()
    # add_max_period_cash_to_finalresult()
    plot_parameter_result_pic()
    pass
