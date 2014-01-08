#coding=utf-8
'''
Created on 2011-3-19

@author: 王健
'''
from django.conf.urls.defaults import patterns
from zt.ztmanage.views import  top, menu, welcome
from zt.ztmanage.flexview import autoCompleteGenZong
from zt.ztmanage.views import noperm, dataadd, codeupload, orderbbsave, orderbblist
from zt.ztmanage.dataPrint import getExcelByData
from zt.ztmanage.flexurls import orderGateway
from ztmanage.flexview2 import initZYDH

urlpatterns = patterns('^zt/$',
                       (r'^top/$', top),
                       (r'^menu/$', menu),
                       (r'^welcome/$', welcome),
                       (r'^noperm/$', noperm),
                       (r'^dataadd/$', dataadd),
                       (r'^codeupload/$', codeupload),
                       (r'^orderbbsave$', orderbbsave),
                       (r'^orderbblist$', orderbblist),
                       (r'^getExcelByData$', getExcelByData),
                       (r'^auto', autoCompleteGenZong),
                       (r'^initZYDH', initZYDH),
#                       (r'^tiaozheng', tiaozhengOrderBB),
                       (r'^geteway/', orderGateway
                           ),
                       )
