#coding:utf-8
#!/usr/bin/python
'''
#EPS_PEG_Estimatation
# Author: Noah
# First Release : 2016.12
'''
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import datetime
#from datetime
import datetime as dt
import pandas_datareader.data as web
from collections import defaultdict

import re
import sys
import os
import time
import argparse
#import shutil
#from datetime import datetime,timedelta
#import getopt

#import stkLIB.basicfunc

class pegest :
  '''
    #PEG_estimatation
	#Demo Target: Get PER(Price EPS Ratio) YoY
  '''
  def __init__(self):
      self.debug = 0
      self.ExtMode = 0 # 0 : path ./ , 1: path ../
      pass

  def isfloat(self,value):
    try:
      float(value)
      return True
    except ValueError:
      return False

  def isint(self,val):
     try:
         x = int(val)
         return  True
     except ValueError:
         return False
#ivals= list(filter(isint,values))
#clip_pos = [n if n< 0 else 0 for n in mylist]
#more5 = [n> 5 for n in counts]
#list(compress(address,more5))

#Get Adjust Price, return tuple
#Input: tw and two is different market type
# Adj :1 , return Adjustice price
#     :0 , return normal price
#The reuturn tuple is Adjustice price after EXCLUDE DIVIDEND and EXCLUDE RIGHT.
  def GetAdjPrice(self,CO_ID=2330,marketype="tw",NOWYEAR=2016,Adjust=1):
    start = dt.datetime(2000, 1, 1)
    end = dt.datetime(2016, 1, 27) #TODO: THIS
    retrycount = 0
    #try :
    tg = web.DataReader( str(CO_ID)+"."+marketype, 'yahoo', start, end)
    #except IOError as e:
    #        if retrycount == 0:
    #           marketype = "two"
    #           tg = web.DataReader( str(CO_ID)+"."+marketype, 'yahoo', start, end)
    #           retrycount = 1
    #        else:
    #           print "Please check {:4d} ".format(CO_ID)
    #           return -1
    #finally:

    if Adjust == 1 :
       tgAdjC = tg['Adj Close']
    else:
       tgAdjC = tg['Close']

    #print tg['Close'].max() , tg['Adj Close'],min(), Adj

    startY = tg.iloc[0].name.year
    stopY  = tg.iloc[len(tg)-1].name.year
    Adjprice = {}
    for i in range(startY,stopY+1):
        #print i  , tgAdjC[str(i)].max(), tgAdjC[str(i)].min()
        Adjprice[int(i)] = (tgAdjC[str(i)].max(),tgAdjC[str(i)].min())
    #print Adjust
    return Adjprice
#Norprice =GetAdjPrice(2330,'tw',0)
#Adjprice = GetAdjPrice(StockID,market,2016,0)
#Adjprice
#Adjprice = GetAdjPrice(StockID,market,2016,1)
#Adjprice

  def GetInfoEPS(self,ICO_ID=2330):
      '''
  	  #Get Yearly EPS function
      #Target_link:http://www.goodinfo.tw/StockInfo/StockBzPerformance.asp?STOCK_ID=2330
      #goodlink = "http://www.goodinfo.tw/StockInfo/StockBzPerformance.asp?STOCK_ID=2330&YEAR_PERIOD=9999&RPT_CAT=M_YEAR"
      '''
      ResCode = 0
      table_index = 0
      stkID = str(ICO_ID)
      #print  stkID, type(stkID), ICO_ID, type(ICO_ID)
      headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

      goodlink = "http://www.goodinfo.tw/StockInfo/StockBzPerformance.asp"
      postData = {
         "STOCK_ID": stkID,
         "YEAR_PERIOD":"9999",
         "RPT_CAT": "M_YEAR" }#,
         #"STEP"   : "DATA",
         #  }
      res = requests.post(goodlink,data=postData,headers=headers)
      res.encoding = "utf8" #The web is utf8 or big5?
      tables = pd.read_html(res.text)
      if self.debug:
        print "len(tables) %s"%(len(tables))
        table_index = 16
        print tables[table_index][0]
      else:
        table_index = 16 #Target index for ESP, ...

      try :

         EPSlist = zip(tables[table_index][0] ,tables[table_index][18])
      except Exception , exc:
         print 'GetInfoEPS()exception:%s exc %s' % (Exception, exc)
         ResCode = -1
         return ResCode


     #return tables
      EPSdict = defaultdict(float)
     #d = OrderedDict(float)
      for key,value in EPSlist:
         #print "1",key,value, type(key),type(value)
         #if(type(key) != 'unicode'):
         #key = key.dtype('U')
         key =unicode(str(key),'utf-8')
         #key = key.encode('ascii','ignore')
         #value = value.encode('ascii','ignore')

         fvalue =0.0
         if self.isfloat(value):
            value = float(value)
         else:
            value = 0.0
         #print key,value, type(key),type(value)
         EPSdict[key] = value

      return EPSdict
#http://www.goodinfo.tw/StockInfo/ShowK_Chart.asp?STOCK_ID=1565&CHT_CAT2=YEAR
#Get more Yearly price data
#Maintain and Generate PER table
#Input: Adjprice = {key : (Maxprice, Minprice)} # dict
#EPSdict = {unicode,float} #dict Year: Price
  def GetPERtable(self,Adjprice,EPSdict):
    dictPER = defaultdict(float)
    MaxPER =0.0
    MinPER =0.0
    for Yearidx in Adjprice:
       # print Yearidx , type(Yearidx)
       MaxPrice , MinPrice =Adjprice[Yearidx]
       if EPSdict[unicode(Yearidx)] !=None: #> 0:  # Don't use negative EPS ?
          MaxPER = MaxPrice / float(EPSdict[unicode(Yearidx)])
          MinPER = MinPrice / float(EPSdict[unicode(Yearidx)])
       #else:
       #   MaxPER = None
       #   MinPER = None
       #print Yearidx ,MaxPER , MinPER, MaxPrice, MinPrice,EPSdict[unicode(Yearidx)]

       dictPER[int(Yearidx)] = (MaxPER,MinPER,EPSdict[unicode(Yearidx)])
    return dictPER

#Get datafrme about EPS and PER
  def GetPERDF(self,dictPER,EPSdict):
    StartY = max(dictPER.keys())-1
    EndY   = min(dictPER.keys())
    MaxPER_YoY = []
    MinPER_YoY = []
    EPSYoY = []
    HiPER = []
    LoPER = []
    Hiprice =[]
    Loprice =[]
    Yearidx = []
    listEPS =[]
    #print "Year is from {:4d} to {:4d} ".format(StartY,EndY) #,StartY, EndY

    for i in range(StartY,EndY, -1):
        if (dictPER[i][0] != None): #Get YoY rate
           MaxPER_YoY.append(format((dictPER[i][0] /dictPER[i-1][0])-1,".2%" ))
           MinPER_YoY.append(format((dictPER[i][1] /dictPER[i-1][1])-1,".2%"))
           EPSYoY.append( format((dictPER[i][2]/dictPER[i-1][2])-1,".2%" ))
           Yearidx.append(i)
           listEPS.append(EPSdict[unicode(i)])

    for i in range(StartY,EndY, -1):
        if (dictPER[i][0] != None): #Generate the list High/Low PER
           HiPER.append(dictPER[i][0])
           LoPER.append(dictPER[i][1])

    Marketprice = self.GetAdjPrice(StockID,market,0) #Get High/Low Non-adjust price in each year
    for i in range(StartY,EndY, -1):
    #if (dictPER[i][0] != None):
        Hiprice.append(Marketprice[i][0])
        Loprice.append(Marketprice[i][1])

#Gen PER YoY Dataframe table
    tabcol = [u'股價高點',u'股價低點',u'PER高點',u'PER低點',u'PER高點YoY',u'PER低點YoY',u'EPS',u'EPS成長率YoY']

    dat = {tabcol[0]: Hiprice,
           tabcol[1]: Loprice,
           tabcol[2]: HiPER,
           tabcol[3]: LoPER,
           tabcol[4]: MaxPER_YoY,
           tabcol[5]: MinPER_YoY,
           tabcol[6]: listEPS,
           tabcol[7]: EPSYoY
      }
#print len(Hiprice),len(Loprice),len(HiPER),len(LoPER),len(MaxPER_YoY),len(MinPER_YoY),len(EPSYoY)
    df_table = pd.DataFrame(dat,columns=tabcol,index = Yearidx)

    return df_table

#Get  Coefficient of Variation = Standard Deviation (SD) / mean
  def GetStdMean(self,dfPER_table):
   HiPER=list(dfPER_table[u'PER高點'])
   LoPER=list(dfPER_table[u'PER低點'])
   CVHiPER = np.std(HiPER) / np.mean(HiPER)
   CVLoPER = np.std(LoPER) / np.mean(LoPER)
   #print np.std(HiPER), np.std(LoPER)
   #print np.mean(HiPER), np.mean(LoPER)
   return CVHiPER,CVLoPER


  def GetStdMeanDict(self,dictPER,StartY,EndY):
   #HiPER=list(dfPER_table[u'PER高點'])
   #LoPER=list(dfPER_table[u'PER低點'])
   i = 0
   HiPER =[]
   LoPER =[]
   for i in range(StartY,EndY, -1):
    if (dictPER[i][0] != None):
        HiPER.append(dictPER[i][0])
        LoPER.append(dictPER[i][1])
   HiStd = np.std(HiPER) # HiPER SD
   LoStd = np.std(LoPER) # LoPER SD
   HiMean = np.mean(HiPER)
   LoMean = np.mean(LoPER)
   #print HiStd, LoStd, HiMean, LoMean
   Hipredict = HiStd + HiMean
   Lopredict = LoStd + LoMean

   CVHiPER = HiStd / HiMean
   CVLoPER = LoStd / LoMean
   return CVHiPER,CVLoPER ,Hipredict , Lopredict


  def DetMarketType(self,StockID=2330):
    #if self.ExtMode == 1:
    if 'csv_data' in os.listdir('.'):
       mkt_two = pd.read_csv("./csv_data/mkt_two.csv")
       mkt_tw = pd.read_csv("./csv_data/mkt_tw.csv")
    else:
       mkt_two = pd.read_csv("../csv_data/mkt_two.csv")
       mkt_tw = pd.read_csv("../csv_data/mkt_tw.csv")

    liTWOID = mkt_two.values[0:,0]
    liTWID = mkt_tw.values[0:,0]
    market = None
    if StockID in liTWOID:
       market = "two"
    elif StockID in liTWID:
       market = "tw"
    else:
       print "StockID {:4d} is not vaild".format(StockID)
    return market

  def ShowPERCV(self,StockID=2330,StartY = 2015,offset=6):
   EPSdict  = self.GetInfoEPS(StockID)
   market   = self.DetMarketType(StockID)
   Adjprice = self.GetAdjPrice(StockID,market)
   dictPER  = self.GetPERtable(Adjprice,EPSdict)

   ##dfPER_table = GetPERDF(dictPER)
   ##CVHiPER,CVLoPER = GetStdMean(dfPER_table)
   #print StockID,CVHiPER,CVLoPER

   EndY = StartY - offset
   if len(dictPER) < 10 :
      CVHiPER = 1.0
      CVLoPER = 1.0
      return CVHiPER,CVLoPER
   #else:
   CVHiPER,CVLoPER,HiPPER , LoPPER = self.GetStdMeanDict(dictPER,StartY,EndY)
   return CVHiPER,CVLoPER
   #print StockID,CVHiPER,CVLoPER , StartY,EndY

#Get Last trade date price , the close price is bigger than price threshold
  def PriceFilter(self,StkList,price_thr=50):
    liHighPrice =[]
    start = dt.datetime(2016, 1, 1)
    end = dt.datetime.now()
    for StockID in StkList: #tw1603:
        market= self.DetMarketType(StockID)
        tg = web.DataReader( str(StockID)+"."+market, 'yahoo', start.date(), end.date())
        Last_price = tg.iloc[len(tg)-1]['Close']
        if Last_price >= price_thr:
           liHighPrice.append(StockID)

    return liHighPrice

def usage():
    print "The Usage of the Script as following:"
    print "Command Format:"
    print " "
    print "./pegest.py -f <log file name>"
    print "=============================================================================\n\n"
    print "Example:"
    print " "
    print "./pegest.py -f PEGxxxx.log"
    print "=============================================================================\n\n"
    sys.exit()

def main(argv):
    logFile = ""
    parser = argparse.ArgumentParser(description='Search some files')
    parser.add_argument('-f', dest='logFile', action='store',
    help='log file name')
    parser.add_argument('-w', dest='webtable', action='store_true',
    help='get website table')


    args = parser.parse_args()
    PEG = pegest()
    if args.webtable :
    	PEG.debug = 0
        #PEG.GetInfoEPS()

        CVHiPER,CVLoPER = PEG.ShowPERCV(2030,2015,6)
        print CVHiPER,CVLoPER

    elif args.logFile != None:
        logFile = args.logFile
    else:
        usage()
        sys.exit(-1)

    #self.pegest(logFile)

if __name__ == "__main__":
    main(sys.argv[1:])
