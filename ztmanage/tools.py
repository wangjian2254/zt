#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
from django.core.cache import cache
from zt.ztmanage.models import OrderBBNo, PlanNo, Scx, Code, OrderNo, OrderList, Ztperm, OrderBB

__author__ = u'王健'


PLANSTATUS = (u'非常紧急', u'一般紧急', u'标准生产', u'库备')


def str2date(strdate):
    return datetime.datetime.strptime(strdate, '%Y/%m/%d')


def str2date2(strdate):
    return datetime.datetime.strptime(strdate, '%Y%m%d')


def date2str(date):
    if date:
        return date.strftime('%Y/%m/%d')
    return u'永久'

def date2str2(date):
    if date:
        return date.strftime('%Y%m%d')
    return u'永久'


def permission_required(code):
    def permission(func):
        def test(request, *args, **kwargs):
            if request.user.has_perm(code):
                return func(request, *args, **kwargs)
            else:
                return getResult(False, False, u'权限不够,需要具有：%s 权限' % Ztperm.perm[code])

        return test

    return permission

def planchange_required(code):
    def permission(func):
        def test(request, *args, **kwargs):
            if request.user.has_perm(code):
                return func(request, *args, **kwargs)
            else:
                lsh = kwargs.get('lsh', '')
                if not lsh:
                    return func(request, *args, **kwargs)
                if lsh and request.user.pk == PlanNo.objects.get(lsh=lsh).bianzhi.pk:
                    return func(request, *args, **kwargs)
                return getResult(False, False, u'权限不够,需要具有：%s 权限,并且只能修改自己编织的计划' % Ztperm.perm[code])

        return test

    return permission

def orderbbdel_required(code):
    def permission(func):
        def test(request, *args, **kwargs):
            if request.user.has_perm(code):
                return func(request, *args, **kwargs)
            else:
                idlist=args[0]
                if len(idlist)>0:
                    if request.user.pk==OrderBB.objects.get(pk=idlist[0]['id']).lsh.user.pk:
                        return func(request, *args, **kwargs)
                return getResult(False,False,u'权限不够,需要具有：%s 权限'%Ztperm.perm[code])
        return test
    return permission
def orderbbchange_required(code):
    def permission(func):
        def test(request, *args, **kwargs):
            if len(args)==1 or not args[1]:
                return func(request, *args, **kwargs)
            elif request.user.has_perm(code):
                return func(request, *args, **kwargs)
            else:
                lsh=args[1]
                if request.user.pk==OrderBBNo.objects.get(lsh=lsh).user.pk:
                    return func(request, *args, **kwargs)
                return getResult(False,False,u'权限不够,需要具有：%s 权限'%Ztperm.perm[code])
        return test
    return permission




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
    date=datetime.datetime.now().strftime("JH%Y%m%d")

    lastNo=PlanNo.objects.filter(lsh__startswith=date+'-'+('000'+str(user.pk))[-3:]+'-').order_by('-lsh')[:1]
    if len(lastNo)>0:
        lsh=lastNo[0].lsh.split('-')[2]
        lsh=int(lsh)
        lsh+=1
        lsh=lastNo[0].lsh.split('-')[0]+'-'+lastNo[0].lsh.split('-')[1]+'-'+('0000'+str(lsh))[-2:]
        return lsh
    else:
        return date+'-'+('000'+str(user.pk))[-3:]+'-'+'0000'[-2:]


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
        if code.ismain==False:
            codevalue['ismain']=False
        else:
            codevalue['ismain']=True
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
    codevalue={'id':code.pk,'code':code.code,'name':code.name,'gg':code.gg,'dj':code.dj,'scx':getScxById(code.scx_id)['name']}
    if code.ismain==False:
        codevalue['ismain']=False
    else:
        codevalue['ismain']=True
    cache.set('code'+str(codeid),codevalue,3600*24*20)
    return codevalue

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

