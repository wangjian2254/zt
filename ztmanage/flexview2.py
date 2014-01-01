#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime,json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from zt.ztmanage.models import OrderList, OrderNo, OrderBB, PlanNo, PlanRecord, PlanDetail, ProductSite, Ztperm
from zt.ztmanage.tools import getResult,  newPlanLSHNoByUser, getOrderByOrderlistid, getCodeNameById

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

def str2date2(strdate):
    return datetime.datetime.strptime(strdate, '%Y%m%d')



def permission_required(code):
    def permission(func):
        def test(request, *args, **kwargs):
            if request.user.has_perm(code):
                return func(request, *args, **kwargs)
            else:
                return getResult(False,False,u'权限不够,需要具有：%s 权限'%Ztperm.perm[code])
        return test
    return permission

def plandel_required(code):
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

def planchange_required(code):
    def permission(func):
        def test(request, *args, **kwargs):
            if request.user.has_perm(code):
                return func(request, *args, **kwargs)
            else:
                lsh=kwargs.get('lsh','')
                if not lsh:
                    return func(request, *args, **kwargs)
                if lsh and  request.user.pk==PlanNo.objects.get(lsh=lsh).bianzhi.pk:
                    return func(request, *args, **kwargs)
                return getResult(False,False,u'权限不够,需要具有：%s 权限,并且只能修改自己编织的计划'%Ztperm.perm[code])
        return test
    return permission


@login_required
@planchange_required('ztmanage.plan_update')
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
        planrecord.level = int(getattr(planrecordobj,'level',0))
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
            if not hasattr(planrecordobj,'enddate%s'%psite.id) or getattr(planrecordobj,'enddate%s'%psite.id,None)==u'永久':
                plandetail.enddate=None
            else:
                plandetail.enddate=str2date(getattr(planrecordobj,'enddate%s'%psite.id))
            plandetail.startsite = psite
            plandetail.endsite = ProductSite.objects.get(pk=getattr(planrecordobj,'zrwz%s'%psite.id))
            plandetail.save()
    return getResult(planno,True,u'计划制定成功,流水号：%s'%planno.lsh)



@login_required
def getPlanDetailByIdOrLsh(request,obj):
    lsh =None
    id = None
    try:
        id = int(obj)
    except:
        lsh = obj
    if id:
        planno = PlanNo.objects.filter(pk=id)[:1]
    if lsh:
        planno = PlanNo.objects.filter(lsh=lsh)[:1]
    if len(planno):
        planno = planno[0]
    else:
        return getResult(False,False,u'主计划不存在')

    resultlist=[]
    for record in PlanRecord.objects.filter(planno=planno):
        orderlist = getOrderByOrderlistid(record.orderlist_id)
        code=getCodeNameById(orderlist.get('code'))
        planrecord = {"id":record.pk,'yddbh':record.orderlist_id,'code':code.get('id'),'codestr':code.get('code'),'codename':code.get('name'),'codegg':code.get('gg'),'scx':code.get('scx')}
        planrecord['zydh'] = record.zydh
        planrecord['plannum'] = record.plannum
        planrecord['planbz'] = record.planbz
        planrecord['ordergongyi'] = record.ordergongyi
        planrecord['level'] = record.level
        planrecord['isdel'] = record.isdel
        if record.oldData:
            planrecord['oldDataDict'] =  json.loads(record.oldData)
        else:
            planrecord['oldDataDict'] = {}

        for plandetail in PlanDetail.objects.filter(planrecord=record):
            planrecord['startdate%s'%plandetail.startsite_id] = plandetail.startdate.strftime('%Y/%m/%d')
            if plandetail.enddate:
                planrecord['enddate%s'%plandetail.startsite_id] = plandetail.enddate.strftime('%Y/%m/%d')
            else:
                planrecord['enddate%s'%plandetail.startsite_id] = u'永久'
            planrecord['zrwz%s'%plandetail.startsite_id] = plandetail.endsite_id
            if plandetail.oldData:
                planrecord['oldDataDict'].update(json.loads(plandetail.oldData))
            planrecord['isdel%s'%plandetail.startsite_id] = plandetail.isdel
        if not planrecord['oldDataDict']:
            del planrecord['oldDataDict']
        resultlist.append(planrecord)
    return getResult({"list":resultlist,'plan':planno})



@login_required
@planchange_required('ztmanage.plan_update')
@transaction.commit_on_success
def updatePlanDelete(request,recordids):
    planrecordquery = PlanRecord.objects.filter(pk__in=recordids)
    planrecordquery.update(isdel=True)
    PlanDetail.objects.filter(planrecord__in=planrecordquery).update(isdel=True)
    return getResult(True,True,u'删除主计划记录成功')


@login_required
@permission_required('ztmanage.plan_check')
@transaction.commit_on_success
def checkPlan(request,obj):
    lsh =None
    id = None
    try:
        id = int(obj)
    except:
        lsh = obj
    if id:
        planno = PlanNo.objects.filter(pk=id)[:1]
    if lsh:
        planno = PlanNo.objects.filter(lsh=lsh)[:1]
    if len(planno):
        planno = planno[0]
    else:
        return getResult(False,False,u'主计划不存在')
    if planno.bianzhi_id != request.user.id:
        return getResult(False,False,u'不能 审核 自己编制的主计划')
    if planno.status == "2":
        return getResult(False,False,u'已经审核过的主计划 不能 再次 审核')

    planno.status = '2'
    planno.shenhe = request.user
    planno.save()
    return getResult(True,True,u'审核 主计划成功，流水号为：%s'%planno.lsh)

@login_required
@permission_required('ztmanage.plan_uncheck')
@transaction.commit_on_success
def uncheckPlan(request,obj):
    lsh =None
    id = None
    try:
        id = int(obj)
    except:
        lsh = obj
    if id:
        planno = PlanNo.objects.filter(pk=id)[:1]
    if lsh:
        planno = PlanNo.objects.filter(lsh=lsh)[:1]
    if len(planno):
        planno = planno[0]
    else:
        return getResult(False,False,u'主计划不存在')

    if planno.bianzhi_id != request.user.id:
        return getResult(False,False,u'不能 退审 自己编制的主计划')
    if planno.status != "2":
        return getResult(False,False,u'未审核过的主计划 不能 退审')
    planno.status = '3'
    planno.shenhe = request.user
    planno.save()
    return getResult(True,True,u'退审 主计划成功，流水号为：%s'%planno.lsh)


@login_required
@permission_required('ztmanage.plan_all')
@transaction.commit_on_success
def allPlan(request,obj):
    pass



def queryPlanBy(request,planuser,checkuser,startdate,enddate,checkstartdate,checkenddate,status=None):
    '''
    status 0:全部 1:未通过 2:通过
    '''
    query =PlanNo.objects.all()
    if planuser:
        query = query.filter(bianzhi=planuser)
    if checkuser:
        query = query.filter(shenhe=checkuser)
    if startdate:
        query = query.filter(updateTime__gte=str2date2(startdate))
    if enddate:
        query = query.filter(updateTime__lte=str2date2(enddate))

    if checkstartdate:
        query = query.filter(lastcheckTime__gte=str2date2(checkstartdate))
    if checkenddate:
        query = query.filter(lastcheckTime__lte=str2date2(checkenddate))

    if status == 1:
        query = query.filter(status__in=('1','3'))
    elif status == 2:
        query = query.filter(status='2')

    resultlist=[]
    for plan in query:
        r={'id':plan.pk,'lsh':plan.lsh,'shenhe':getattr(getattr(plan,"shenhe",{}),"last_name",""),'bianzhi':getattr(getattr(plan,"bianzhi",{}),"last_name",""),'updateTime':plan.updateTime.strftime('%Y/%m/%d'),'status':plan.status}
        r['lastcheckTime']=''
        if plan.lastcheckTime:
            r['lastcheckTime']=plan.lastcheckTime.strftime('%Y/%m/%d')
        resultlist.append(r)
    return getResult(resultlist)



@login_required
def queryPlanByUser(request):
    return queryPlanBy(request,request.user,None,None,None,None,None,1)

@login_required
@permission_required('ztmanage.plan_query')
def queryPlan(request,planuser,checkuser,startdate,enddate,checkstartdate,checkenddate):
    return queryPlanBy(request,planuser,checkuser,startdate,enddate,checkstartdate,checkenddate)

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









