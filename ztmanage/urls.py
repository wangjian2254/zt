#coding=utf-8
'''
Created on 2011-3-19

@author: 王健
'''
from django.conf.urls.defaults import patterns
from zt.ztmanage.views import  top, menu, welcome
from zt.ztmanage.flexview import orderGateway,autoCompleteGenZong
from zt.ztmanage.views import noperm, dataadd, codeupload, orderbbsave, orderbblist
from ztmanage.flexview import tiaozhengOrderBB

urlpatterns = patterns('^zt/$',
                       (r'^top/$', top),
                       (r'^menu/$', menu),
                       (r'^welcome/$', welcome),
                       (r'^noperm/$', noperm),
                       (r'^dataadd/$', dataadd),
                       (r'^codeupload/$', codeupload),
                       (r'^orderbbsave$', orderbbsave),
                       (r'^orderbblist$', orderbblist),
                       (r'^auto', autoCompleteGenZong),
#                       (r'^tiaozheng', tiaozhengOrderBB),
                       (r'^geteway/', orderGateway
                           ),
                       )