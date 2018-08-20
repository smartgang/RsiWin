# -*- coding: utf-8 -*-

import DynamicStopLoss as dsl
import OnceWinNoLoss as ownl
import FixRateStopLoss as frsl
import DslOwnlClose as dslownl
import MultiStopLoss as msl
import StopLossLib.AtrStopLoss as atrsl
import DATA_CONSTANTS as DC
import pandas as pd
import os
import numpy as np
import multiprocessing
import datetime
import HullRsiWin_Parameter as Parameter
import time


def getDSL(strategyName, symbolInfo, K_MIN, stoplossList, parasetlist, bar1mdic, barxmdic, result_para_dic, indexcols, progress=False):
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_'+i)
    allresultdf_cols=['setname','slTarget','worknum']+indexcols+new_indexcols
    allresultdf = pd.DataFrame(columns=allresultdf_cols)

    allnum = 0
    paranum=parasetlist.shape[0]
    for stoplossTarget in stoplossList:
        timestart = time.time()
        dslFolderName = ("DynamicStopLoss%.1f" % (stoplossTarget * 1000))
        try:
            os.mkdir(dslFolderName)  # 创建文件夹
        except:
            #print 'folder already exist'
            pass
        print ("stoplossTarget:%.3f" % stoplossTarget)

        resultdf = pd.DataFrame(columns=allresultdf_cols)
        setnum = 0
        numlist = range(0, paranum, 100)
        numlist.append(paranum)
        for n in range(1, len(numlist)):
            pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
            l = []
            for a in range(numlist[n - 1], numlist[n]):
                setname = parasetlist.ix[a, 'Setname']
                if not progress:
                    # l.append(dsl.dslCal(strategyName,symbolInfo, K_MIN, setname, oprdflist[a-a0], bar1mlist[a-a0], barxmlist[a-a0], positionRatio, initialCash, stoplossTarget, dslFolderName + '\\',
                    #                                       indexcols))
                    l.append(pool.apply_async(dsl.dslCal, (strategyName, symbolInfo, K_MIN, setname, bar1mdic, barxmdic, result_para_dic, stoplossTarget,
                                                           dslFolderName + '\\', indexcols)))
                else:
                    #l.append(dsl.progressDslCal(strategyName,symbolInfo, K_MIN, setname, bar1m, barxm, pricetick,
                    #                                               positionRatio, initialCash, stoplossTarget,
                    #                                               dslFolderName + '\\'))
                    l.append(pool.apply_async(dsl.progressDslCal, (strategyName,
                                                                   symbolInfo, K_MIN, setname, bar1mdic, barxmdic, result_para_dic, stoplossTarget,
                                                                   dslFolderName + '\\',indexcols)))
            pool.close()
            pool.join()

            for res in l:
                resultdf.loc[setnum] = res.get()
                allresultdf.loc[allnum] = resultdf.loc[setnum]
                setnum += 1
                allnum += 1
        resultdf.to_csv(dslFolderName + '\\' + strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_dsl%.3f.csv' % stoplossTarget, index=False)
        timeend = time.time()
        timecost = timeend - timestart
        print (u"dsl_%.3f 计算完毕，共%d组数据，总耗时%.3f秒,平均%.3f秒/组" % (stoplossTarget,paranum, timecost, timecost / paranum))
    allresultdf.to_csv(strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_dsl.csv', index=False)


def getOwnl(strategyName, symbolInfo, K_MIN, winSwitchList, nolossThreshhold, parasetlist, bar1mdic, barxmdic, result_para_dic, indexcols, progress=False):
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_'+i)
    allresultdf_cols = ['setname', 'winSwitch', 'worknum'] + indexcols + new_indexcols
    ownlallresultdf = pd.DataFrame(columns=allresultdf_cols)
    allnum=0
    paranum=parasetlist.shape[0]
    for winSwitch in winSwitchList:
        timestart = time.time()
        ownlFolderName = "OnceWinNoLoss%.1f" % (winSwitch * 1000)
        try:
            os.mkdir(ownlFolderName)  # 创建文件夹
        except:
            #print "dir already exist!"
            pass
        print ("OnceWinNoLoss WinSwitch:%.3f" % winSwitch)

        ownlresultdf = pd.DataFrame(columns=allresultdf_cols)

        setnum = 0
        numlist = range(0, paranum, 100)
        numlist.append(paranum)
        for n in range(1, len(numlist)):
            pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
            l = []
            for a in range(numlist[n - 1], numlist[n]):
                setname = parasetlist.ix[a, 'Setname']
                if not progress:
                    l.append(pool.apply_async(ownl.ownlCal,
                                              (strategyName, symbolInfo, K_MIN, setname, bar1mdic, barxmdic, winSwitch, nolossThreshhold, result_para_dic,
                                               ownlFolderName + '\\', indexcols)))
                else:
                    #l.append(ownl.progressOwnlCal(strategyName, symbolInfo, K_MIN, setname, bar1m, barxm, winSwitch,
                    #                           nolossThreshhold, positionRatio, initialCash,
                    #                           ownlFolderName + '\\'))
                    l.append(pool.apply_async(ownl.progressOwnlCal,
                                              (strategyName, symbolInfo, K_MIN, setname, bar1mdic, barxmdic, winSwitch, nolossThreshhold, result_para_dic,
                                               ownlFolderName + '\\', indexcols)))
            pool.close()
            pool.join()

            for res in l:
                ownlresultdf.loc[setnum] = res.get()
                ownlallresultdf.loc[allnum] = ownlresultdf.loc[setnum]
                setnum += 1
                allnum += 1
        # ownlresultdf['cashDelta'] = ownlresultdf['new_endcash'] - ownlresultdf['old_endcash']
        ownlresultdf.to_csv(ownlFolderName + '\\' + strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_ownl%.3f.csv' % winSwitch, index=False)
        timeend = time.time()
        timecost = timeend - timestart
        print (u"ownl_%.3f 计算完毕，共%d组数据，总耗时%.3f秒,平均%.3f秒/组" % (winSwitch,paranum, timecost, timecost / paranum))
    # ownlallresultdf['cashDelta'] = ownlallresultdf['new_endcash'] - ownlallresultdf['old_endcash']
    ownlallresultdf.to_csv(strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_ownl.csv', index=False)


def getFRSL(strategyName, symbolInfo, K_MIN, fixRateList, parasetlist, bar1mdic, barxmdic, result_para_dic, indexcols, progress=False):
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_'+i)
    allresultdf = pd.DataFrame(columns=['setname', 'fixRate', 'worknum']+indexcols+new_indexcols)
    allnum = 0
    paranum=parasetlist.shape[0]
    for fixRateTarget in fixRateList:
        timestart = time.time()
        folderName = "FixRateStopLoss%.1f" % (fixRateTarget * 1000)
        try:
            os.mkdir(folderName)  # 创建文件夹
        except:
            #print 'folder already exist'
            pass
        print ("fixRateTarget:%.3f" % fixRateTarget)

        resultdf = pd.DataFrame(columns=['setname', 'fixRate', 'worknum']+indexcols+new_indexcols)
        setnum = 0
        numlist = range(0, paranum, 100)
        numlist.append(paranum)
        for n in range(1, len(numlist)):
            pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
            l = []
            for a in range(numlist[n - 1], numlist[n]):
                setname = parasetlist.ix[a, 'Setname']
                if not progress:
                    #l.append(frsl.frslCal(strategyName,
                    #                                       symbolInfo, K_MIN, setname, bar1m, barxm, fixRateTarget, positionRatio,initialCash, folderName + '\\'))
                    l.append(pool.apply_async(frsl.frslCal, (strategyName,
                                                             symbolInfo, K_MIN, setname, bar1mdic, barxmdic, fixRateTarget, result_para_dic, folderName + '\\',
                                                             indexcols)))
                else:
                    l.append(pool.apply_async(frsl.progressFrslCal, (strategyName,
                                                                     symbolInfo, K_MIN, setname, bar1mdic, barxmdic, fixRateTarget, result_para_dic, folderName + '\\',
                                                                     indexcols)))
            pool.close()
            pool.join()

            for res in l:
                resultdf.loc[setnum] = res.get()
                allresultdf.loc[allnum] = resultdf.loc[setnum]
                setnum += 1
                allnum += 1
        # resultdf['cashDelta'] = resultdf['new_endcash'] - resultdf['old_endcash']
        resultdf.to_csv(folderName + '\\' + strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_frsl%.3f.csv' % fixRateTarget, index=False)
        timeend = time.time()
        timecost = timeend - timestart
        print (u"frsl_%.3f 计算完毕，共%d组数据，总耗时%.3f秒,平均%.3f秒/组" % (fixRateTarget,paranum, timecost, timecost / paranum))
    # allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv(strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_frsl.csv', index=False)


def get_atr_sl(strategyName, symbolInfo, bar_type, atr_para_list, parasetlist, bar1mdic, barxmdic, result_para_dic, indexcols, progress=False):
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_'+i)
    allresultdf = pd.DataFrame(columns=['setname', 'atr_sl_target', 'worknum']+indexcols+new_indexcols)
    allnum = 0
    paranum=parasetlist.shape[0]
    for atr_para in atr_para_list:
        timestart = time.time()
        atr_pendant_n = atr_para['atr_pendant_n']
        atr_pendant_rate = atr_para['atr_pendant_rate']
        atr_yoyo_n = atr_para['atr_yoyo_n']
        atr_yoyo_rate = atr_para['atr_yoyo_rate']
        folderName = '%d_%.1f_%d_%.1f' % (atr_pendant_n, atr_pendant_rate, atr_yoyo_n, atr_yoyo_rate)

        try:
            os.mkdir(folderName)  # 创建文件夹
        except:
            #print 'folder already exist'
            pass

        resultdf = pd.DataFrame(columns=['setname', 'atr_sl_target', 'worknum']+indexcols+new_indexcols)
        setnum = 0
        numlist = range(0, paranum, 100)
        numlist.append(paranum)
        for n in range(1, len(numlist)):
            pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
            l = []
            for a in range(numlist[n - 1], numlist[n]):
                setname = parasetlist.ix[a, 'Setname']
                if not progress:
                    l.append(atrsl.atrsl(strategyName,symbolInfo, bar_type, setname, bar1mdic, barxmdic, atr_para, result_para_dic, folderName + '\\',
                                                             indexcols, timestart))
                    #l.append(pool.apply_async(atrsl.atrsl, (strategyName,
                    #                                         symbolInfo, bar_type, setname, bar1mdic, barxmdic, atr_para, result_para_dic, folderName + '\\',
                    #                                         indexcols, timestart)))
                else:
                    l.append(pool.apply_async(atrsl.progress_atrsl, (strategyName,
                                                                     symbolInfo, K_MIN, setname, bar1mdic, barxmdic, atr_para, result_para_dic, folderName + '\\',
                                                                     indexcols)))
            pool.close()
            pool.join()

            for res in l:
                resultdf.loc[setnum] = res.get()
                allresultdf.loc[allnum] = resultdf.loc[setnum]
                setnum += 1
                allnum += 1
        # resultdf['cashDelta'] = resultdf['new_endcash'] - resultdf['old_endcash']
        resultdf.to_csv(folderName + '\\' + strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_atrsl%s.csv' % folderName, index=False)
        timeend = time.time()
        timecost = timeend - timestart
        print (u"atr_%s 计算完毕，共%d组数据，总耗时%.3f秒,平均%.3f秒/组" % (folderName,paranum, timecost, timecost / paranum))
    # allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv(strategyName + ' ' + symbol + str(K_MIN) + ' finalresult_atrsl.csv', index=False)


def getDslOwnl(strategyName, symbolInfo, K_MIN, parasetlist, stoplossList, winSwitchList, result_para_dic, indexcols):
    symbol = symbolInfo.domain_symbol
    allresultdf = pd.DataFrame(
        columns=['setname', 'dslTarget', 'ownlWinSwtich', 'old_endcash', 'old_Annual', 'old_Sharpe', 'old_Drawback',
                 'old_SR', 'new_endcash', 'new_Annual', 'new_Sharpe', 'new_Drawback', 'new_SR',
                 'dslWorknum', 'ownlWorknum', 'dslRetDelta', 'ownlRetDelta'])
    allnum=0
    paranum=parasetlist.shape[0]
    for stoplossTarget in stoplossList:
        for winSwitch in winSwitchList:
            dslFolderName = "DynamicStopLoss%.1f\\" % (stoplossTarget * 1000)
            ownlFolderName = "OnceWinNoLoss%.1f\\" % (winSwitch * 1000)
            newfolder = ("dsl_%.3f_ownl_%.3f" % (stoplossTarget, winSwitch))
            try:
                os.mkdir(newfolder)  # 创建文件夹
            except:
                # print newfolder, ' already exist!'
                pass
            print ("slTarget:%f ownlSwtich:%f" % (stoplossTarget, winSwitch))
            pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
            l = []
            for sn in range(0, paranum):
                setname = parasetlist.ix[sn, 'Setname']
                l.append(pool.apply_async(dslownl.dslAndownlCal,
                                                  (strategyName,symbolInfo, K_MIN,setname, stoplossTarget, winSwitch, result_para_dic,dslFolderName,
                                                   ownlFolderName, newfolder + '\\')))
            pool.close()
            pool.join()

            resultdf = pd.DataFrame(
                columns=['setname', 'dslTarget', 'ownlWinSwtich', 'old_endcash', 'old_Annual', 'old_Sharpe',
                         'old_Drawback',
                         'old_SR', 'new_endcash', 'new_Annual', 'new_Sharpe', 'new_Drawback', 'new_SR',
                         'dslWorknum', 'ownlWorknum', 'dslRetDelta', 'ownlRetDelta'])
            i = 0
            for res in l:
                resultdf.loc[i] = res.get()
                allresultdf.loc[allnum] = resultdf.loc[i]
                i += 1
                allnum+=1
            resultfilename = ("%s %s%d finalresult_dsl%.3f_ownl%.3f.csv" % (strategyName,symbol, K_MIN, stoplossTarget, winSwitch))
            resultdf.to_csv(newfolder + '\\' + resultfilename)

    #allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv(strategyName+' '+symbol + str(K_MIN)+ ' finalresult_dsl_ownl.csv')


def getMultiSLT(strategyName, symbolInfo, K_MIN, parasetlist, barxmdic, sltlist, result_para_dic, indexcols):
    """
    计算多个止损策略结合回测的结果
    :param strategyName:
    :param symbolInfo:
    :param K_MIN:
    :param parasetlist:
    :param sltlist:
    :param positionRatio:
    :param initialCash:
    :return:
    """
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_'+i)
    allresultdf_cols=['setname','slt','slWorkNum']+indexcols+new_indexcols
    allresultdf = pd.DataFrame(columns=allresultdf_cols)

    allnum=0
    paranum=parasetlist.shape[0]

    # dailyK = DC.generatDailyClose(barxm)

    #先生成参数列表
    allSltSetList=[] #这是一个二维的参数列表，每一个元素是一个止损目标的参数dic列表
    for slt in sltlist:
        sltset=[]
        for t in slt['paralist']:
            sltset.append({'name': slt['name'],
                           'sltValue': t,
                           'folder': ("%s%.1f\\" % (slt['folderPrefix'], (t * 1000))),
                           'fileSuffix': slt['fileSuffix']
                           })
        allSltSetList.append(sltset)
    finalSltSetList=[]#二维数据，每个一元素是一个多个止损目标的参数dic组合
    for sltpara in allSltSetList[0]:
        finalSltSetList.append([sltpara])
    for i in range(1,len(allSltSetList)):
        tempset = allSltSetList[i]
        newset = []
        for o in finalSltSetList:
            for t in tempset:
                newset.append(o + [t])
        finalSltSetList = newset
    print finalSltSetList

    for sltset in finalSltSetList:
        newfolder=''
        for sltp in sltset:
            newfolder += (sltp['name']+'_%.3f' %(sltp['sltValue']))
        try:
            os.mkdir(newfolder)  # 创建文件夹
        except:
            pass
        print (newfolder)
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        l = []
        for sn in range(0, paranum):
            setname = parasetlist.ix[sn, 'Setname']
            #l.append(msl.multiStopLosslCal(strategyName, symbolInfo, K_MIN, setname, sltset, positionRatio, initialCash,
            #                           newfolder + '\\'))
            l.append(pool.apply_async(msl.multiStopLosslCal,
                                      (strategyName, symbolInfo, K_MIN, setname, sltset, barxmdic, result_para_dic, newfolder, indexcols)))
        pool.close()
        pool.join()

        resultdf = pd.DataFrame(columns=allresultdf_cols)
        i = 0
        for res in l:
            resultdf.loc[i] = res.get()
            allresultdf.loc[allnum] = resultdf.loc[i]
            i += 1
            allnum += 1
        resultfilename = ("%s %s%d finalresult_multiSLT_%s.csv" % (strategyName, symbol, K_MIN, newfolder))
        resultdf.to_csv(newfolder + '\\' + resultfilename, index=False)

    allresultname=''
    for slt in sltlist:
        allresultname += slt['name']
    # allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv("%s %s%d finalresult_multiSLT_%s.csv" % (strategyName, symbol, K_MIN, allresultname), index=False)
    pass

if __name__=='__main__':
    # 文件路径
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName

    # 取参数集
    parasetlist = pd.read_csv(resultpath + Parameter.parasetname)
    paranum = parasetlist.shape[0]

    #indexcols
    indexcols=Parameter.ResultIndexDic

    # 参数设置
    strategyParameterSet = []
    if not Parameter.symbol_KMIN_opt_swtich:
        # 单品种单周期模式
        paradic = {
            'strategyName': Parameter.strategyName,
            'exchange_id': Parameter.exchange_id,
            'sec_id': Parameter.sec_id,
            'K_MIN': Parameter.K_MIN,
            'startdate': Parameter.startdate,
            'enddate': Parameter.enddate,
            'result_para_dic': Parameter.result_para_dic,
            'progress':Parameter.progress_close,
            'calcDsl': Parameter.calcDsl_close,
            'calcOwnl': Parameter.calcOwnl_close,
            'calcFrsl': Parameter.calcFrsl_close,
            'calcMultiSLT':Parameter.calcMultiSLT_close,
            'calcDslOwnl': Parameter.calcDslOwnl_close,
            'dslStep':Parameter.dslStep_close,
            'dslTargetStart':Parameter.dslTargetStart_close,
            'dslTargetEnd':Parameter.dslTargetEnd_close,
            'ownlStep' : Parameter.ownlStep_close,
            'ownlTargetStart': Parameter.ownlTargetStart_close,
            'ownltargetEnd': Parameter.ownltargetEnd_close,
            'nolossThreshhold':Parameter.nolossThreshhold_close,
            'frslStep': Parameter.frslStep_close,
            'frslTargetStart':Parameter.frslTargetStart_close,
            'frslTargetEnd': Parameter.frslTragetEnd_close,
            'calcAtrsl': Parameter.calcAtrsl_close,
            'atr_pendant_n_list': Parameter.atr_pendant_n_list,
            'atr_pendant_rate_list': Parameter.atr_pendant_rate_list,
            'atr_yoyo_n_list': Parameter.atr_yoyo_n_list,
            'atr_yoyo_rate_list': Parameter.atr_yoyo_rate_list
        }
        strategyParameterSet.append(paradic)
    else:
        # 多品种多周期模式
        symbolset = pd.read_excel(resultpath + Parameter.stoploss_set_filename,index_col='No')
        symbolsetNum = symbolset.shape[0]
        for i in range(symbolsetNum):
            exchangeid = symbolset.ix[i, 'exchange_id']
            secid = symbolset.ix[i, 'sec_id']
            strategyParameterSet.append({
                'strategyName': symbolset.ix[i, 'strategyName'],
                'exchange_id': exchangeid,
                'sec_id': secid,
                'K_MIN': symbolset.ix[i, 'K_MIN'],
                'startdate': symbolset.ix[i, 'startdate'],
                'enddate': symbolset.ix[i, 'enddate'],
                'result_para_dic': Parameter.result_para_dic,
                'progress':symbolset.ix[i,'progress'],
                'calcDsl': symbolset.ix[i, 'calcDsl'],
                'calcOwnl': symbolset.ix[i, 'calcOwnl'],
                'calcFrsl': symbolset.ix[i, 'calcFrsl'],
                'calcMultiSLT': symbolset.ix[i,'calcMultiSLT'],
                'calcDslOwnl': symbolset.ix[i, 'calcDslOwnl'],
                'dslStep': symbolset.ix[i, 'dslStep'],
                'dslTargetStart': symbolset.ix[i, 'dslTargetStart'],
                'dslTargetEnd': symbolset.ix[i, 'dslTargetEnd'],
                'ownlStep': symbolset.ix[i, 'ownlStep'],
                'ownlTargetStart': symbolset.ix[i, 'ownlTargetStart'],
                'ownltargetEnd': symbolset.ix[i, 'ownltargetEnd'],
                'nolossThreshhold': symbolset.ix[i, 'nolossThreshhold'],
                'frslStep': symbolset.ix[i, 'frslStep'],
                'frslTargetStart': symbolset.ix[i, 'frslTargetStart'],
                'frslTargetEnd': symbolset.ix[i, 'frslTargetEnd']
            }
            )

    for strategyParameter in strategyParameterSet:

        strategyName = strategyParameter['strategyName']
        exchange_id = strategyParameter['exchange_id']
        sec_id = strategyParameter['sec_id']
        K_MIN = strategyParameter['K_MIN']
        startdate = strategyParameter['startdate']
        enddate = strategyParameter['enddate']
        domain_symbol = '.'.join([exchange_id, sec_id])

        result_para_dic = strategyParameter['result_para_dic']

        symbolinfo = DC.SymbolInfo(domain_symbol, startdate, enddate)
        pricetick = symbolinfo.getPriceTick()

        #计算控制开关
        progress=strategyParameter['progress']
        calcDsl=strategyParameter['calcDsl']
        calcOwnl=strategyParameter['calcOwnl']
        calcFrsl=strategyParameter['calcFrsl']
        calcMultiSLT=strategyParameter['calcMultiSLT']
        calcDslOwnl=strategyParameter['calcDslOwnl']
        calcAtrsl = strategyParameter['calcAtrsl']

        #优化参数
        dslStep = strategyParameter['dslStep']
        stoplossList = np.arange(strategyParameter['dslTargetStart'], strategyParameter['dslTargetEnd'], dslStep)
        #stoplossList=[-0.022]
        ownlStep=strategyParameter['ownlStep']
        winSwitchList = np.arange(strategyParameter['ownlTargetStart'], strategyParameter['ownltargetEnd'], ownlStep)
        #winSwitchList=[0.009]
        nolossThreshhold = strategyParameter['nolossThreshhold'] * pricetick
        frslStep=strategyParameter['frslStep']
        fixRateList=np.arange(strategyParameter['frslTargetStart'], strategyParameter['frslTargetEnd'], frslStep)

        atrsl_para_dic_list = []
        if calcAtrsl:
            atr_pendant_n_list = strategyParameter['atr_pendant_n_list']
            atr_pendan_rate_list = strategyParameter['atr_pendant_rate_list']
            atr_yoyo_n_list = strategyParameter['atr_yoyo_n_list']
            atr_yoyo_rate_list = strategyParameter['atr_yoyo_rate_list']
            for atr_pendant_n in atr_pendant_n_list:
                for atr_pendant_rate in atr_pendan_rate_list:
                    for atr_yoyo_n in atr_yoyo_n_list:
                        for atr_yoyo_rate in atr_yoyo_rate_list:
                            atrsl_para_dic_list.append(
                                {
                                    'atr_pendant_n':atr_pendant_n,
                                    'atr_pendant_rate': atr_pendant_rate,
                                    'atr_yoyo_n': atr_yoyo_n,
                                    'atr_yoyo_rate': atr_yoyo_rate
                                }
                            )

        #文件路径
        foldername = ' '.join([strategyName,exchange_id, sec_id, str(K_MIN)])
        oprresultpath=resultpath+foldername+'\\'
        os.chdir(oprresultpath)

        # 原始数据处理
        # bar1m=DC.getBarData(symbol=symbol,K_MIN=60,starttime=startdate+' 00:00:00',endtime=enddate+' 23:59:59')
        # barxm=DC.getBarData(symbol=symbol,K_MIN=K_MIN,starttime=startdate+' 00:00:00',endtime=enddate+' 23:59:59')
        # bar1m计算longHigh,longLow,shortHigh,shortLow
        # bar1m=bar1mPrepare(bar1m)
        # bar1mdic = DC.getBarBySymbolList(domain_symbol, symbolinfo.getSymbolList(), 60, startdate, enddate)
        # barxmdic = DC.getBarBySymbolList(domain_symbol, symbolinfo.getSymbolList(), K_MIN, startdate, enddate)
        cols = ['open', 'high', 'low', 'close', 'strtime', 'utc_time', 'utc_endtime']
        #bar1mdic = DC.getBarDic(symbolinfo, 60, cols)
        #barxmdic = DC.getBarDic(symbolinfo, K_MIN, cols)
        bar1mdic = DC.getBarBySymbolList(domain_symbol, symbolinfo.getSymbolList(), 60, startdate, enddate, cols)
        barxmdic = DC.getBarBySymbolList(domain_symbol, symbolinfo.getSymbolList(), K_MIN, startdate, enddate, cols)

        if calcMultiSLT:
            sltlist=[]
            if calcDsl:
                sltlist.append({'name':'dsl',
                                'paralist':stoplossList,
                                'folderPrefix':'DynamicStopLoss',
                                'fileSuffix':'resultDSL_by_tick.csv'})
            if calcOwnl:
                sltlist.append({'name':'ownl',
                                'paralist':winSwitchList,
                                'folderPrefix':'OnceWinNoLoss',
                                'fileSuffix':'resultOWNL_by_tick.csv'})
            if calcFrsl:
                sltlist.append({'name': 'frsl',
                                'paralist': fixRateList,
                                'folderPrefix': 'FixRateStopLoss',
                                'fileSuffix': 'resultFRSL_by_tick.csv'})
            getMultiSLT(strategyName, symbolinfo, K_MIN, parasetlist, barxmdic, sltlist, result_para_dic, indexcols)
        else:
            if calcDsl:
                getDSL(strategyName, symbolinfo, K_MIN, stoplossList, parasetlist, bar1mdic, barxmdic, result_para_dic, indexcols, progress)

            if calcOwnl:
                getOwnl(strategyName, symbolinfo, K_MIN, winSwitchList, nolossThreshhold, parasetlist, bar1mdic, barxmdic, result_para_dic, indexcols, progress)

            if calcFrsl:
                getFRSL(strategyName, symbolinfo, K_MIN, fixRateList, parasetlist, bar1mdic, barxmdic, result_para_dic, indexcols, progress)

            if calcDslOwnl:
                getDslOwnl(strategyName, symbolinfo, K_MIN, parasetlist, stoplossList, winSwitchList, result_para_dic, indexcols)

            if calcAtrsl:
                get_atr_sl(strategyName, symbolinfo, K_MIN, atrsl_para_dic_list, parasetlist, bar1mdic, barxmdic, result_para_dic, indexcols, progress=False)
