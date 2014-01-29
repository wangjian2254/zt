#coding=utf-8
'''
Created on 2011-3-19

@author: 王健
'''
from django.conf.urls.defaults import patterns
from zt.ztmanage.views import  top, menu, welcome
from zt.ztmanage.views import noperm, dataadd, codeupload, orderbbsave, orderbblist
from zt.ztmanage.dataPrint import getExcelByData, getExcelByGroupData, uploadImage
from zt.ztmanage.flexurls import orderGateway
from zt.ztmanage.flexview2 import initZYDH, initQXDDBH
from ztmanage.autoTask import autoCompleteGenZong

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
#                       (r'^tiaozheng', tiaozhengOrderBB),
                       (r'^geteway/', orderGateway
                           ),
                       )
