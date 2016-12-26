# -*- coding: utf-8 -*-

'''
Collect some basic function template
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

#Demo Target: Get PER(Price EPS Ratio) YoY
def isfloat(value):
    try:
      float(value)
      return True
    except ValueError:
      return False

def isint(val):
     try:
         x = int(val)
         return  True
     except ValueError:
         return False
#ivals= list(filter(is_int,values))
#clip_pos = [n if n< 0 else 0 for n in mylist]
#more5 = [n> 5 for n in counts]
#list(compress(address,more5))

#Return percent string format to float
def GetPercent(strper):
    return float(str(strper).strip('%'))/100

#####################################################################################
#Date and Time
#####################################################################################
def CE2Ming(CEYear=1911):
    return CEYear - 1911


