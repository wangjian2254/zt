#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
from django.shortcuts import render_to_response
from flexview import getOrderGenZongRow
from tools import savePickle
from django.db import transaction
from flexview_view import queryPlanDetail2

__author__ = u'王健'

@transaction.commit_on_success
def autoCompleteGenZong(request):
    datestr=datetime.datetime.now().strftime("%Y%m%d")
    #if not hasFile(datestr,True):
    data=getOrderGenZongRow(request,datestr,'open')
    savePickle(datestr,True,data)
    #if not hasFile(datestr,False):
    data=getOrderGenZongRow(request,datestr,'close')
    savePickle(datestr,False,data)

    queryPlanDetail2(request,{'uncache':True})

    url='http://'+request.META['HTTP_HOST']+'/static/swf/'
    return render_to_response('zt/index.html',{'url':url,'p':datetime.datetime.now()})

