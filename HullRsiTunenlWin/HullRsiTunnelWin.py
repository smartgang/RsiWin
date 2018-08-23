# -*- coding: utf-8 -*-
"""
对RSI相对强弱指标进行三重平滑，其计算步骤如下：
                 ⒈计算21日RSI指标；
                 ⒉计算21日RSI指标的10日ema平均得出 RSI1；
                 ⒊将第2步计算结果求5日ema平均得出  RSI2；
                 ⒋求第2步、第3步计算结果的差额    NEWRSI;
                 5.对第4步的结果进行hull运算，得出HULLRSI;

开仓条件和平仓条件：
--------------------------------------------------------------------------------
   HULLRSI>0 同时  RSI1<70         做多             HULLRSI<0   平仓
   HULLRSI<0 同时  RSI1 >30         做空             HULLRSI>0   平仓
   HULLRSI=0  延续上根K线的状态
"""
import MA
import Indexer.RSI as RSI
import pandas as pd
import os
import DATA_CONSTANTS as DC
import numpy as np
import multiprocessing
import ResultStatistics as RS


def HullRsiTunnelWin(symbolinfo, rawdata, para_set):
    setname = para_set['Setname']
    para_n1 = para_set['N1']
    para_m1 = para_set['M1']
    para_m2 = para_set['M2']
    para_n = para_set['N']
    para_tunnel_n = para_set['Tunnel_N']
    #para_rsi1_up = para_set['RSI1_UP']
    #para_rsi1_down = para_set['RSI1_DOWN']
    # print setname
    """
    LC := REF(CLOSE,1);
    BACKGROUNDSTYLE(1);
    RSI1:SMA(MAX(CLOSE-LC,0),N1,1)/SMA(ABS(CLOSE-LC),N1,1)*100;
    RMA1:EMA(RSI1,M1);
    RMA2:EMA(RMA1,M2);
    RSINEW:=RMA1-RMA2;
    X:= 2*EMA2(RSINEW,ROUND(N/2,0))-EMA2(RSINEW,N);
    HURSI:10*EMA2(X,ROUND(SQRT(N),0)),COLORSTICK;
    """
    rsi1 = pd.Series(RSI.rsi(rawdata['close'], para_n1))
    rsi_ema1 = MA.calEMA(rsi1, para_m1)
    rsi_ema2 = MA.calEMA(rsi_ema1, para_m2)
    rsi_new = rsi_ema1 - rsi_ema2
    hull_rsi = MA.hull_ma(rsi_new, para_n)
    #rawdata['RSI1'] = rsi1
    rawdata['RSI_EMA1'] = rsi_ema1
    #rawdata['RSI_EMA2'] = rsi_ema2
    #rawdata['RSI_NEW'] = rsi_new
    rawdata['HullRsi'] = hull_rsi
    rawdata['TOP_EMA'] = MA.calEMA(rawdata['high'], para_tunnel_n)
    rawdata['BOTTOM_EMA'] = MA.calEMA(rawdata['low'], para_tunnel_n)
    rawdata['zero'] = 0
    rawdata['Unnamed: 0'] = range(rawdata.shape[0])
    # 计算M金叉和死叉
    rawdata['HullRsi_True'], rawdata['HullRsi_Cross'] = MA.dfCross(rawdata, 'HullRsi', 'zero')

    # ================================ 找出买卖点================================================
    # 1.先找出SAR金叉的买卖点
    # 2.找到结合判决条件的买点
    # 3.从MA买点中滤出真实买卖点
    # 取出金叉点
    goldcrosslist = pd.DataFrame({'goldcrosstime': rawdata.loc[rawdata['HullRsi_Cross'] == 1, 'strtime']})
    goldcrosslist['goldcrossutc'] = rawdata.loc[rawdata['HullRsi_Cross'] == 1, 'utc_time']
    goldcrosslist['goldcrossindex'] = rawdata.loc[rawdata['HullRsi_Cross'] == 1, 'Unnamed: 0']
    goldcrosslist['goldcrossprice'] = rawdata.loc[rawdata['HullRsi_Cross'] == 1, 'close']
    goldcrosslist['goldcrossrsi'] = rawdata.loc[rawdata['HullRsi_Cross'] == 1, 'RSI_EMA1']

    # 取出死叉点
    deathcrosslist = pd.DataFrame({'deathcrosstime': rawdata.loc[rawdata['HullRsi_Cross'] == -1, 'strtime']})
    deathcrosslist['deathcrossutc'] = rawdata.loc[rawdata['HullRsi_Cross'] == -1, 'utc_time']
    deathcrosslist['deathcrossindex'] = rawdata.loc[rawdata['HullRsi_Cross'] == -1, 'Unnamed: 0']
    deathcrosslist['deathcrossprice'] = rawdata.loc[rawdata['HullRsi_Cross'] == -1, 'close']
    deathcrosslist['deathcrossrsi'] = rawdata.loc[rawdata['HullRsi_Cross'] == -1, 'RSI_EMA1']

    goldcrosslist = goldcrosslist.reset_index(drop=True)
    deathcrosslist = deathcrosslist.reset_index(drop=True)

    # 生成多仓序列（金叉在前，死叉在后）
    if goldcrosslist.ix[0, 'goldcrossindex'] < deathcrosslist.ix[0, 'deathcrossindex']:
        longcrosslist = pd.concat([goldcrosslist, deathcrosslist], axis=1)
    else:  # 如果第一个死叉的序号在金叉前，则要将死叉往上移1格
        longcrosslist = pd.concat([goldcrosslist, deathcrosslist.shift(-1)], axis=1)
    longcrosslist = longcrosslist.set_index(pd.Index(longcrosslist['goldcrossindex']), drop=True)

    # 生成空仓序列（死叉在前，金叉在后）
    if deathcrosslist.ix[0, 'deathcrossindex'] < goldcrosslist.ix[0, 'goldcrossindex']:
        shortcrosslist = pd.concat([deathcrosslist, goldcrosslist], axis=1)
    else:  # 如果第一个金叉的序号在死叉前，则要将金叉往上移1格
        shortcrosslist = pd.concat([deathcrosslist, goldcrosslist.shift(-1)], axis=1)
    shortcrosslist = shortcrosslist.set_index(pd.Index(shortcrosslist['deathcrossindex']), drop=True)

    # 取出开多序号和开空序号
    #openlongindex = rawdata.loc[
    #    (rawdata['HullRsi_Cross'] == 1) & (rawdata['RSI_EMA1'] < para_rsi1_up)].index
    #openshortindex = rawdata.loc[
    #    (rawdata['HullRsi_Cross'] == -1) & (rawdata['RSI_EMA1'] > para_rsi1_down)].index
    openlongindex = rawdata.loc[(rawdata['HullRsi_Cross'] == 1) & (rawdata['close'] > rawdata['TOP_EMA'])].index
    openshortindex = rawdata.loc[(rawdata['HullRsi_Cross'] == -1) & (rawdata['close'] < rawdata['BOTTOM_EMA'])].index
    # 从多仓序列中取出开多序号的内容，即为开多操作
    longopr = longcrosslist.loc[openlongindex]
    longopr['tradetype'] = 1
    longopr.rename(columns={'goldcrosstime': 'opentime',
                            'goldcrossutc': 'openutc',
                            'goldcrossindex': 'openindex',
                            'goldcrossprice': 'openprice',
                            'goldcrossrsi': 'open_rsi',
                            'deathcrosstime': 'closetime',
                            'deathcrossutc': 'closeutc',
                            'deathcrossindex': 'closeindex',
                            'deathcrossprice': 'closeprice',
                            'deathcrossrsi': 'close_rsi'}, inplace=True)

    # 从空仓序列中取出开空序号的内容，即为开空操作
    shortopr = shortcrosslist.loc[openshortindex]
    shortopr['tradetype'] = -1
    shortopr.rename(columns={'deathcrosstime': 'opentime',
                             'deathcrossutc': 'openutc',
                             'deathcrossindex': 'openindex',
                             'deathcrossprice': 'openprice',
                             'deathcrossrsi': 'open_rsi',
                             'goldcrosstime': 'closetime',
                             'goldcrossutc': 'closeutc',
                             'goldcrossindex': 'closeindex',
                             'goldcrossprice': 'closeprice',
                             'goldcrossrsi': 'close_rsi'}, inplace=True)

    # 结果分析
    result = pd.concat([longopr, shortopr])
    result = result.sort_index()
    result = result.reset_index(drop=True)
    # result.drop(result.shape[0] - 1, inplace=True)
    result = result.dropna()
    # 去掉跨合约的操作
    # 使用单合约，不用再去掉跨合约
    # result = removeContractSwap(result, contractswaplist)

    #rawdata.to_csv('%s_rawdata.csv' % setname)
    slip = symbolinfo.getSlip()
    result['ret'] = ((result['closeprice'] - result['openprice']) * result['tradetype']) - slip
    result['ret_r'] = result['ret'] / result['openprice']
    return result


if __name__ == '__main__':
    pass