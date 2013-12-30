#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from zt.ztmanage.models import OrderList, OrderNo, OrderBB, PlanNo, PlanRecord, PlanDetail, ProductSite
from zt.ztmanage.tools import getResult,  newPlanLSHNoByUser

__author__ = u'王健'
'''
('plan_update',u'主计划编制'),
('plan_check',u'主计划审核'),
('plan_uncheck',u'主计划退审'),
('plan_all',u'主计划汇总'),
('plan_query',u'主计划查询'),
('plan_changerecord',u'主计划修改记录'),
'''

def str2date(strdate):
    return datetime.datetime.strptime(strdate, '%Y/%m/%d')


@login_required
@permission_required('ztmanage.plan_update')
@transaction.commit_on_success
def updatePlan(request,sitelist,unsitelist,planrecordlist,lsh=None):
    '''
    编制保存主计划，没有经过审核的主计划可以任意修改。
    审核状态的主计划，不可以修改，
    '''
    if lsh:
        planno=PlanNo.objects.get(lsh=lsh)
        for delsite in unsitelist:
            PlanDetail.objects.filter(planrecord__in=PlanRecord.objects.filter(planno=planno).filter(isdel=False)).filter(startsite=getattr(delsite,'id')).filter(isdel=False).update(isdel=True)
    else:
        planno=PlanNo()
        planno.lsh=newPlanLSHNoByUser(request.user)
        planno.status='1'
    planno.updateTime=datetime.datetime.now()
    planno.bianzhi=request.user
    planno.save()

    for planrecordobj in planrecordlist:
        if hasattr(planrecordobj,'id'):
            planrecord = PlanRecord.objects.get(pk=getattr(planrecordobj,'id'))
        else:
            planrecord = PlanRecord()
            planrecord.planno=planno
        planrecord.orderlist = OrderList.objects.get(pk=getattr(planrecordobj,'yddbh'))
        planrecord.zydh = getattr(planrecordobj,'zydh')
        planrecord.plannum = int(getattr(planrecordobj,'plannum',0))
        planrecord.level = int(getattr(planrecordobj,'level',1))
        planrecord.planbz = getattr(planrecordobj,'planbz','')
        planrecord.ordergongyi = getattr(planrecordobj,'ordergongyi','')
        planrecord.save()
        for site in sitelist:
            psite=ProductSite.objects.get(pk=getattr(site,'id'))
            plandetail = PlanDetail.objects.filter(planrecord=planrecord).filter(startsite=psite)[:1]
            if len(plandetail):
                plandetail = plandetail[0]
            else:
                plandetail = PlanDetail()
                plandetail.planrecord = planrecord
                plandetail.startsite = psite
            plandetail.isdel = False
            if not hasattr(planrecordobj,'startdate%s'%psite.id) or not hasattr(planrecordobj,'zrwz%s'%psite.id):
                plandetail.isdel=True
                if plandetail.pk:
                    plandetail.save()
                continue
            plandetail.startdate = str2date(getattr(planrecordobj,'startdate%s'%psite.id))
            if not hasattr(planrecordobj,'enddate%s'%psite.id) or getattr(planrecordobj,'enddate%s'%psite.id)==u'永久'or getattr(planrecordobj,'enddate%s'%psite.id)=='永久':
                plandetail.enddate=None
            else:
                plandetail.enddate=str2date(getattr(planrecordobj,'enddate%s'%psite.id))
            plandetail.startsite = psite
            plandetail.endsite = ProductSite.objects.get(pk=getattr(planrecordobj,'zrwz%s'%psite.id))
            plandetail.save()
    return getResult(planno,True,u'计划制定成功')









@login_required
@permission_required('ztmanage.plan_update')
@transaction.commit_on_success
def updatePlanDelete(request,obj):
    pass


@login_required
@permission_required('ztmanage.plan_check')
@transaction.commit_on_success
def checkPlan(request,obj):
    pass

@login_required
@permission_required('ztmanage.plan_uncheck')
@transaction.commit_on_success
def uncheckPlan(request,obj):
    pass


@login_required
@permission_required('ztmanage.plan_all')
@transaction.commit_on_success
def allPlan(request,obj):
    pass

@login_required
@permission_required('ztmanage.plan_query')
@transaction.commit_on_success
def queryPlan(request,planuser,startdate,enddate,status):
    pass

@login_required
@permission_required('ztmanage.plan_changerecord')
@transaction.commit_on_success
def changerecordPlan(request,obj):
    pass

@login_required
@permission_required('ztmanage.plan_changerecord')
@transaction.commit_on_success
def changerecordPlanDelete(request,obj):
    pass


@login_required
def getOrderEndDate(request,ddbhid):
    ddbh = OrderNo.objects.get(pk=ddbhid)
    lsh=''
    for b in OrderBB.objects.filter(yorder__in=OrderList.objects.filter(ddbh=ddbh)).order_by('-id')[:1]:
        lsh = b.lsh.lsh

    if lsh:
        return getResult({'ddbhid':ddbhid,'date': datetime.datetime.strptime(lsh.split('-')[0], '%Y%m%d') })
    else:
        return getResult({'ddbhid':ddbhid,'date':datetime.datetime.now() })

@login_required
@permission_required('ztmanage.orderruning')
def getOrderRuningList(request,start,end,ddbh=None):
    orderlistquery = OrderList.objects.all()
    if start and end:
        orderlistquery=orderlistquery.filter(createDate__gte=datetime.datetime.strptime(start,'%Y%m%d')).filter(createDate__lte=datetime.datetime.strptime(end,'%Y%m%d')+datetime.timedelta(hours =24))
    if isinstance(ddbh,int):
        orderlistquery=orderlistquery.filter(ddbh=ddbh)
    if isinstance(ddbh,str) or isinstance(ddbh,unicode):
        orderlistquery = orderlistquery.filter(ddbh__in=OrderNo.objects.filter(ddbh__istartswith=ddbh))
    orderbhids = set()
    for ol in orderlistquery:
        orderbhids.add(ol.ddbh_id)
    orderdict = {}
    for o in OrderNo.objects.filter(pk__in=orderbhids):
        orderdict[str(o.pk)]={'id':o.pk,'ddbh':o.ddbh,'xddate':None,'lr':'','orderlistnum':0,'productnum':0,'closeorderlistnum':0,'openorderlistnum':0,'closeflag':0}
    for ol in OrderList.objects.filter(ddbh__in=orderbhids).order_by('createDate'):
        orderdict[str(ol.ddbh_id)]['xddate']=ol.createDate.strftime('%Y/%m/%d')
        orderdict[str(ol.ddbh_id)]['orderlistnum']+=1
        orderdict[str(ol.ddbh_id)]['productnum']+=ol.num
        if ol.is_open:
            orderdict[str(ol.ddbh_id)]['openorderlistnum']+=1
        else:
            orderdict[str(ol.ddbh_id)]['closeorderlistnum']+=1
    #delkeys =[]
    for v in orderdict.values():
        #if isclose == 'open':
        #    if v['openorderlistnum'] ==0:
        #        delkeys.append(str(v['id']))
        #elif isclose == 'close':
        #    if v['openorderlistnum']!=0:
        #        delkeys.append(str(v['id']))
        if v['openorderlistnum']==0:
            v['closeflag']=1
    #for k in delkeys:
    #    del orderdict[k]
    l = list(orderbhids)
    l.sort()
    resultlist =[]
    for k in l:
        if orderdict.has_key(str(k)):
            resultlist.append(orderdict[str(k)])
    return getResult(resultlist)









