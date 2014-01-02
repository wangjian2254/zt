#coding=utf-8
#author:u'王健'
#Date: 12-8-10
#Time: 下午8:50
import time
from zt.settings import MEDIA_ROOT

__author__ = u'王健'

import logging

TIME_FORMATE="%Y_%m_%d"
TIME_FORMATE_LOG="%Y_%m_%d %H:%M:%S"
logger = logging.getLogger()
filename=MEDIA_ROOT+'/logging/%s.log'%(time.strftime(TIME_FORMATE, time.localtime()))
filehandler = logging.FileHandler(filename)
logger.addHandler(filehandler)
fmt = logging.Formatter('%(asctime)s, %(funcName)s, %(message)s')
#logging.basicConfig(filename=MEDIA_ROOT+'/logging/%s.log'%(time.strftime(TIME_FORMATE, time.localtime())))
def errorLog(msg,fun='',xingming='',data=''):
    try:
        global filename
        global filehandler
        newfilename=MEDIA_ROOT+'/logging/%s.log'%(time.strftime(TIME_FORMATE, time.localtime()))
        if newfilename!=filename:
            logger.removeHandler(filehandler)
            newfilehandler=logging.FileHandler(newfilename)
            logger.addHandler(newfilehandler)
            filename=newfilename
        logger.error('%s :'%(time.strftime(TIME_FORMATE_LOG, time.localtime()))+str(msg)+'fun:%s'%fun)
        logger.error('%s :'%(time.strftime(TIME_FORMATE_LOG, time.localtime()))+'name:%s:%s'%(xingming,str(data)))
    except Exception,e:
        print e


  