#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
from django.core.cache import cache
from ztmanage.models import OrderBBNo, PlanNo, Scx, Code, OrderNo, OrderList

__author__ = u'王健'

def getResult(result,success=True,message=None):
    return {'result':result,'success':success,'message':message}

def newLSHNoByUser(user):
    '''
    根据用户，生成流水号
    '''
    date=datetime.datetime.now().strftime("%Y%m%d")

#    lastNo=OrderBBNo.objects.filter(lsh__startswith=date,user=user).delete()
#    lastNo=[]
    lastNo=OrderBBNo.objects.filter(lsh__startswith=date,user=user).order_by('-lsh')[:1]
    if len(lastNo)>0:
        lsh=lastNo[0].lsh.split('-')[2]
        lsh=int(lsh)
        lsh+=1
        lsh=lastNo[0].lsh.split('-')[0]+'-'+lastNo[0].lsh.split('-')[1]+'-'+('0000'+str(lsh))[-4:]
        return lsh
    else:
        return date+'-'+('000'+str(user.pk))[-3:]+'-'+'0000'[-4:]


def newPlanLSHNoByUser(user):
    '''
    根据用户，生成流水号
    '''
    date=datetime.datetime.now().strftime("%Y%m%d")

    lastNo=PlanNo.objects.filter(lsh__startswith=date+'-'+('000'+str(user.pk))[-3:]+'-').order_by('-lsh')[:1]
    if len(lastNo)>0:
        lsh=lastNo[0].lsh.split('-')[2]
        lsh=int(lsh)
        lsh+=1
        lsh=lastNo[0].lsh.split('-')[0]+'-'+lastNo[0].lsh.split('-')[1]+'-'+('0000'+str(lsh))[-4:]
        return lsh
    else:
        return date+'-'+('000'+str(user.pk))[-3:]+'-'+'0000'[-4:]


def delFile(date,is_open):
    cache.delete('%s_%s'%(date,is_open))

def savePickle(date,is_open,obj):
    cache.set('%s_%s'%(date,is_open),obj,3600*24*2)

def getPickleObj(date,is_open):
    obj = cache.get('%s_%s'%(date,is_open))
    return obj

def cacheScx():
    scxmap={}
    for scx in Scx.objects.all():
        scxvalue={'id':scx.pk,'name':scx.name}
        scxmap['scx'+str(scx.pk)]=scxvalue
    return scxmap

def getScxById(id):
    scx=cache.get('scx'+str(id))
    if scx:
        return scx
    scx=Scx.objects.get(pk=id)
    scx={'id':scx.pk,'name':scx.name}
    cache.set('scx'+str(id),scx,3600*24*20)
    return scx

def getCodeByList(l):
    scxmap=cacheScx()
    codemap={}
    for code in Code.objects.filter(pk__in=l):
        codevalue={'id':code.pk,'code':code.code,'name':code.name,'gg':code.gg,'dj':code.dj,'scx':scxmap['scx'+str(code.scx_id)]['name']}
        codemap['code'+str(code.pk)]=codevalue
    return codemap

def getOrderNoByList(l):
    ordernomap={}
    for o in OrderNo.objects.filter(pk__in=l):
        ovalue={'id':o.pk,'ddbh':o.ddbh}
        ordernomap['orderno'+str(o.pk)]=ovalue
    return ordernomap

def getCodeNameById(codeid):
    code=cache.get('code'+str(codeid))
    if code:
        return code
    code=Code.objects.get(pk=codeid)
    code={'id':code.pk,'code':code.code,'name':code.name,'gg':code.gg,'dj':code.dj,'scx':getScxById(code.scx_id)['name']}
    cache.set('code'+str(codeid),code,3600*24*20)
    return code

def getOrderByOrderlistid(orderid):
    # orderlist=cache.get('orderlist'+str(orderid))
    # if orderlist:
    #     return orderlist
    o=OrderList.objects.get(pk=orderid)
    orderlist={'id':o.pk,'dj':o.dj,'cz':o.cz,'ddbh':getOrderNoByOrderList(o.ddbh_id).get('ddbh'),'closedate':o.closeDate,'ordernum':o.num,'code':o.code_id}
    # cache.set('orderlist'+str(orderid),orderlist,3600*24*20)
    return orderlist

def getOrderNoByOrderList(orderid):
    orderlist=cache.get('orderno'+str(orderid))
    if orderlist:
        return orderlist
    o=OrderNo.objects.get(pk=orderid)
    orderlist={'id':o.pk,'ddbh':o.ddbh}
    cache.set('orderno'+str(orderid),orderlist,3600*24*20)
    return orderlist

