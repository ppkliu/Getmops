# -*- coding: utf-8 -*-

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import datetime
import datetime as dt
import pandas_datareader.data as web

from collections import defaultdict

#####################################################################################
#Get Web data
#####################################################################################
#Get history table
#https://www.cathayholdings.com/securities/exclude_AL/market.aspx?btn=1-00-00&st=2498
def GetCatRev(ICO_ID=2330):
    CO_ID = str(ICO_ID)
    catlink = "https://djinfo.cathaysec.com.tw/Z/ZC/ZCH/ZCH.DJHTM?A="+CO_ID
    res = requests.post(catlink)
    res.encoding = "big5" #The web is utf8 or big5?
    tables = pd.read_html(res.text)
    return tables[2]

#Get Stock Name and Number for Title
def GetCatStkName(ICO_ID=2330):
    CO_ID = str(ICO_ID)
    catlink = "https://djinfo.cathaysec.com.tw/Z/ZC/ZCH/ZCH.DJHTM?A="+CO_ID
    res = requests.post(catlink)
    res.encoding = "big5" #The web is utf8 or big5?
    tables = pd.read_html(res.text)
    uTitle = tables[0].iloc[3,0]
    uTitle = uTitle.split()[0]
    return uTitle

#"https://djinfo.cathaysec.com.tw/Z/ZC/ZCH/ZCH.DJHTM?A=2330"
#Use Get/Post function to get WEB data
def GetCathRev(ICO_ID=2330):
     stkID = str(ICO_ID)
     goodlink ="https://djinfo.cathaysec.com.tw/Z/ZC/ZCH/ZCH.DJHTM"
     postData = {
         "A": stkID
         }
     #res = requests.post(goodlink,data=postData)
     res = requests.get(goodlink,params=postData)
         #print res.url
     res.encoding = "big5" #"utf8" #The web is utf8 or big5?
     tables = pd.read_html(res.text)
     table_index = 2 #Target index for Revenue, ...

     return tables[table_index]


#https://djinfo.cathaysec.com.tw/Z/ZC/ZCR/ZCR.DJHTM?A=3673
def GetCathWebData_old(ICO_ID=2330):
     stkID = str(ICO_ID)
     goodlink ="https://djinfo.cathaysec.com.tw/Z/ZC/ZCR/ZCR.DJHTM"
     postData = {
         "A": stkID
         }
     res = requests.get(goodlink,params=postData)
         #print res.url
     res.encoding = "big5" #"utf8" #The web is utf8 or big5?
     tables = pd.read_html(res.text)
     table_index = 2 #Target index for Revenue, ...

     return tables[table_index]


#Get Capital
#Income Statement : https://djinfo.cathaysec.com.tw/Z/ZC/ZCQ/ZCQ.DJHTM
#Finance Rate     : https://djinfo.cathaysec.com.tw/Z/ZC/ZCR/ZCR.DJHTM
#Revenue table    : "https://djinfo.cathaysec.com.tw/Z/ZC/ZCH/ZCH.DJHTM"
def GetCathWebData(Targetlink,ICO_ID=2330):
     stkID = str(ICO_ID)
     postData = {
         "A": stkID
         }
     res = requests.get(Targetlink,params=postData)
         #print res.url
     res.encoding = "big5" #"utf8" #The web is utf8 or big5?
     tables = pd.read_html(res.text)
     table_index = 2 #Target index for Revenue, ...

     return tables[table_index]

#####################################################################################
#####################################################################################
#Get Last Quartter Capital (Million NT)
def GetCapital(StockID=2330):
    Caplink ="https://djinfo.cathaysec.com.tw/Z/ZC/ZCQ/ZCQ.DJHTM"
    IncomeSTM= GetCathWebData(Caplink,StockID)
    Capital = float(IncomeSTM.iloc[52,1])  # Milion
    return Capital

#Revenue and Profit
#
#From Data Source and Generate Revenue Table
def GetRevtable(StockID=2330):
    Revlink  = "https://djinfo.cathaysec.com.tw/Z/ZC/ZCH/ZCH.DJHTM"
    Webtables= GetCathWebData(Revlink,StockID)
    Revtable = Webtables.iloc[5:,0:]
    Revtable = Revtable.reset_index(drop=True)
    return Revtable

#Get Average N Q profit (conservative forecast)
#Return : Average, Minimum , Last Quarter  Profit Rate
def GetFC_ProfitRate(StockID,N=3):
    FRlink="https://djinfo.cathaysec.com.tw/Z/ZC/ZCR/ZCR.DJHTM"
    Webtable= GetCathWebData(FRlink,StockID)
    LastProfitR =float(Webtable.iloc[6,1]) #Get Last Quarter Profit Rate after Tax
    sli_ProfitR = (Webtable.iloc[6,1:(N+1)])
    fli_ProfitR = [float(x) for x in sli_ProfitR]
    AvgProfitR = np.mean(fli_ProfitR)
    MinProfitR = np.min(fli_ProfitR)
    return AvgProfitR, MinProfitR ,LastProfitR

def GetCathEPS(StockID=2330):
    EPSlink = "https://djinfo.cathaysec.com.tw/Z/ZC/ZCQ/ZCQA/ZCQA.DJHTM"
    EPStable = GetCathWebData(EPSlink, StockID)
    li_year = list(EPStable.iloc[0,1:9])
    li_EPS64 = list(EPStable.iloc[50,1:9])
    li_EPS = [float(np_float) for np_float in li_EPS64]

    ##print type(li_EPS64[0]) , type(li_EPS[0])

    li_BCyear = []
    for Yitem in li_year:
        uitem = unicode(str(int(Yitem) + 1911),'utf-8')
        li_BCyear.append(uitem)

    EPSdict = defaultdict(float)
    EPSdict = dict(zip(li_BCyear, li_EPS))
    return EPSdict

#No Use , only for reference
#Get N months Profit Rate's average YoY
#def GetAvgNProft(dfRateTable,N=3):
#    Avg3M_pro = 0.0
#    if N <=0 : N=1
#    for i in range(1,N+1):
#      Avg3M_pro = Avg3M_pro + float(dfRateTable.iloc[6,i])
#     return Avg3M_pro/N

#Get N months Revenue's average YoY
def GetFC_RevYoY(Revtable,N=6):
    sli_YoY = Revtable.iloc[1:(N+1),4]
    #print sli_YoY

    fli_YoY = []
    for item in sli_YoY:
        fli_YoY.append( float(item.replace("%","")))
        #print item
    AvgYoY = 1 + (np.mean(fli_YoY)/100)
    return AvgYoY

#Get Last Year Total Revenue
def GetLastYearRev(dfRevtable):
    iLastYear = dt.datetime.now().year -1
    iMLastYear = CE2Ming(iLastYear) #iLastYear -1911
    sLastM = str(iMLastYear) + "/"+"12"
    sLastM = unicode(sLastM)
    LastYMidx =0
    for i in range( 0 ,len(dfRevtable)-1):
        if (sLastM == dfRevtable.iloc[i,0]):
            LastYMidx =i
            break
    return int(dfRevtable.iloc[LastYMidx,5])

#####################################################################################

# Get Yesterday Close Price
def GetYesPrice(StockID):
     marketype = DetMarketType(StockID)
     end =  dt.date.today()
     start = end - dt.timedelta(days=15) # prevent no trade price in long time closed market
     retrycount = 0
     tg = web.DataReader( str(StockID)+"."+marketype, 'yahoo', start, end)
     LastPrice = float(tg['Close'].tail(1))
     return LastPrice

################################################################################
# Revenue Processing
################################################################################

def GetRevUpside(ICO_ID=2330,verbose=0):
     '''
     Get Revenue upside information
     '''
     df = GetCatRev(ICO_ID)
     title_col = df.values[5,1:7]
     title_col[3] = u'單月' + title_col[3]
     title_col[5] = u'累積' + title_col[5]
     idx_row = list(df.values[6:,0])
     months_idx = [pd.Period(s.replace(s[0:4] , str(int(s[0:3]) + 1911)+"-"),'M') for s in idx_row]
     df = pd.DataFrame(df.values[6:,1:7],columns=title_col,index=months_idx)
     df[u"累積年增率"]=df[u"累積年增率"].str.replace('%','')
     df[u"單月年增率"]=df[u"單月年增率"].str.replace('%','')
     df[u"月增率"]=df[u"月增率"].str.replace('%','')
     df = df.astype(float)
     # Set Filter condition  and get target table
     RevScore1 = 0
     RevScore2 = 0
     RevScore3 = 0
     AccYoY = df[u'累積年增率']
     MonYoY = df[u"單月年增率"]
     if MonYoY[0] > 10:  #The YoY of last month is over 10%
        RevScore1 = 1
     elif MonYoY[0] > 20:
        RevScore1 = 2
     elif MonYoY[0] > 30:
        RevScore1 = 3

     if MonYoY[0] > AccYoY[:6].mean():  #The YoY of last month is over last 3 month average
        RevScore2 = 1
     if MonYoY[0] > AccYoY[:3].mean():  #The YoY of last month is over last 6 month average
        RevScore3 = 1

     return (RevScore1 + RevScore2 +RevScore3 )
     if(verbose == 1):
        print AccYoY[:6]
        print "last",AccYoY[0] , type(AccYoY[0])
        print "First 6",AccYoY[:6].mean() ,"First 3", AccYoY[:3].mean()
        print "YoYacc.mean",AccYoY.mean()

        print df
        print Target_df

     #Target_df = df[Rule1 & Rule2 & Rule3]
     #current = datetime.now()
     #Nowdate = current.date().timetuple()
     #tarMonth = pd.Period(current,"M")
     #if Nowdate.tm_mday > 10:
     #    tarMonth = tarMonth - 1 # The previous month revenue already publish.
     #else:
     #    tarMonth = tarMonth - 2 # 1-10, not publish previous month revenue
     #if(Target_df[:1].index == tarMonth): return 1 #Target_df # Meet Rule1 and YoY raise
     #else: return 0
