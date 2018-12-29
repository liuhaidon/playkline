# encoding:utf-8
import json
import logging
import os
import urllib
import urllib2
import time
from db import database
from utils import Singleton
from BaseHandler import BaseHandler

# //除权公式
# double CalPriceByCQ(double price, double give, double profit,double pei,double peiPrice)
# {
# 	return (price - profit + pei * peiPrice ) / (1 + give);
# }

# double CalPriceByDIFF(double todayprice,double* ema12,double* ema26)
# {
# 	double result=0;
# 	double todayEma12 = 2*todayprice/13+11* (*ema12)/13;
# 	double todayEma26 = 2*todayprice/27+25* (*ema26)/27;
# 	result=todayEma12-todayEma26;
# 	*ema12=todayEma12;
# 	*ema26=todayEma26;
# 	return result;
# }

#除权公式
def Stock_Exdividend(price,give,profit,pei,peiprice):
    return float(price-profit+pei*peiprice)/(1+give)

#计算DIFF
def Stock_DIFF(price, ema12, ema26):
    Ema12 = 2 * price / 13 + 11 * ema12 / 13
    Ema26 = 2 * price / 27 + 25 * ema26 / 27
    return Ema12-Ema26, Ema12, Ema26

def Stock_MA(dayline,):
