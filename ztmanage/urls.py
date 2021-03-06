#coding=utf-8
'''
Created on 2011-3-19

@author: 王健
'''
from django.conf.urls.defaults import patterns
from views import  top, menu, welcome
from views import noperm, dataadd, codeupload, orderbbsave, orderbblist
from dataPrint import getExcelByData, getExcelByGroupData, uploadImage
from flexurls import orderGateway
from flexview2 import initZYDH, initQXDDBH
from autoTask import autoCompleteGenZong, initCachePlan

urlpatterns = patterns(r'^zt/$',
                       (r'^top/$', top),
                       (r'^menu/$', menu),
                       (r'^welcome/$', welcome),
                       (r'^noperm/$', noperm),
                       (r'^dataadd/$', dataadd),
                       (r'^codeupload/$', codeupload),
                       (r'^orderbbsave$', orderbbsave),
                       (r'^orderbblist$', orderbblist),
                       (r'^getExcelByData$', getExcelByData),
                       (r'^getExcelByGroupData$', getExcelByGroupData),
                       (r'^uploadImage$', uploadImage),
                       (r'^auto', autoCompleteGenZong),
                       (r'^initZYDH', initZYDH),
                       (r'^initQXDDBH', initQXDDBH),
                       (r'^initCachePlan', initCachePlan),
#                       (r'^tiaozheng', tiaozhengOrderBB),
                       (r'^geteway/', orderGateway
                           ),
                       )
