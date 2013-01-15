#coding=utf-8
#author:u'王健'
#Date: 12-6-23
#Time: 上午7:55
__author__ = u'王健'




from pyamf.remoting.client import RemotingService
import   sys

gateway = RemotingService ( 'http://localhost:8000/zt/geteway/' )
adduserfavorite_service = gateway.getService ('service')
#edituserfavorite_service = gateway . getService ( ' edituserfavorite ' )
#userfavorite_service = gateway . getService ( ' userfavorite ' )

"""
#添加用户收藏
"""
rs = adduserfavorite_service.getOrderBBNo()
#print   rs [ ' id ' ]
print   " ---------------------------- "