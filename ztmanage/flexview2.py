#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime,json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render_to_response
from zt.ztmanage.models import OrderList, OrderNo, OrderBB, PlanNo, PlanRecord, PlanDetail, ProductSite, Ztperm, Zydh, OrderBBNo
from zt.ztmanage.tools import getResult,  newPlanLSHNoByUser ,getOrderByOrderlistid,getCodeNameById
from zt.ztmanage.errors import PlanRecordError

__author__ = u'王健'
'''
('plan_update',u'主计划编制'),
('plan_check',u'主计划审核'),
('plan_uncheck',u'主计划退审'),
('plan_all',u'主计划汇总'),
('plan_query',u'主计划查询'),
('plan_changerecord',u'主计划修改记录'),
('plan_daily',u'生产情况日报表'),
'''

PLANSTATUS=(u'非常紧急',u'一般紧急',u'标准生产',u'库备')

def str2date(strdate):
    return datetime.datetime.strptime(strdate, '%Y/%m/%d')

def str2date2(strdate):
    return datetime.datetime.strptime(strdate, '%Y%m%d')

def date2str(date):
    if date:
        return date.strftime('%Y/%m/%d')
    return u'永久'



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
    try:
        with transaction.commit_on_success():
            if lsh:
                planno=PlanNo.objects.get(lsh=lsh)
                if '2'==planno.status:
                    return getResult(planno,False,u'计划修改失败,流水号：%s，已经审核过了'%planno.lsh)
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
                planrecord.zydh = getattr(planrecordobj,'zydh','').strip().upper()
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

                    errorquery =PlanDetail.objects.filter(planrecord__in=PlanRecord.objects.filter(orderlist=planrecord.orderlist,zydh=planrecord.zydh)).filter(startsite=plandetail.startsite)
                    if not plandetail.pk and  0<errorquery.count():
                        error = errorquery[0]
                        raise PlanRecordError(error.planrecord.planno_id,error.planrecord.orderlist_id,error.planrecord.zydh,error.startsite_id,error.endsite_id)
                    plandetail.save()
            return getResult(planno,True,u'计划制定成功,流水号：%s'%planno.lsh)
    except PlanRecordError ,e:
        plan = PlanNo.objects.get(pk=e.planno)
        orderlist = OrderList.objects.get(pk=e.order)
        zydh = e.zydh
        startsite = ProductSite.objects.get(pk=e.startsite)
        if e.endsite:
            endsite = ProductSite.objects.get(pk=e.endsite)
        else:
            endsite={}
        msg=u'订单号为：%s ,物料号为：%s ,作业单号为：%s ,投入位置为：%s ，去向位置为：%s ，这条计划和流水号：%s 主计划中的一条计划重复。'%(orderlist.ddbh.ddbh,orderlist.code.code,zydh,startsite.name,getattr(endsite,'name',u'无'),plan.lsh)
        return getResult(False,False,msg)


@login_required
@planchange_required('ztmanage.plan_update')
@transaction.commit_on_success
def updatePlanZYDH(request,zydhlist):
    '''
    只有审核状态的主计划项的作业单号，可以修改，
    '''
    planidlist=[]
    for obj in zydhlist:
        planidlist.append(getattr(obj,"recordid",0))
        try:
            planrecord = PlanRecord.objects.get(pk=getattr(obj,"recordid",0))
            if planrecord.planno.status !='2':
                return getResult(False,False,u'只有审核过的计划才需要单独使用 作业单号修改，其他情况正常修改即可。')
            planrecord.zydh = getattr(obj,'zydh','').strip().upper()
            planrecord.save()
            if 0==Zydh.objects.filter(orderlist=planrecord.orderlist_id,zydh=planrecord.zydh).count():
                try:
                    zydh=Zydh()
                    zydh.zydh=planrecord.zydh
                    zydh.orderlist_id=planrecord.orderlist_id
                    zydh.save()
                except:
                    pass
        except :
            return getResult(False,False,u'只有审核过的计划才需要单独使用 作业单号修改，其他情况正常修改即可。')

    return getResult(True,True,u'作业单号修改成功')


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
    '''
    1.判断 计划是否审核过，退审的可以 删除记录，审核的 不可以删除，退审的可以恢复，其他不可以
    '''
    planrecordquery = PlanRecord.objects.filter(pk__in=recordids)
    for record in planrecordquery:
        if '2'==record.planno.status:
            return getResult(False,False,u'主计划记录删除失败,流水号：%s，已经审核过了'%record.planno.lsh)
    planrecordquery.update(isdel=True)
    PlanDetail.objects.filter(planrecord__in=planrecordquery).update(isdel=True)
    return getResult(recordids,True,u'删除主计划记录成功')

@login_required
@planchange_required('ztmanage.plan_update')
@transaction.commit_on_success
def updatePlanUNDelete(request,recordids):
    '''
    1.判断 计划是否审核过，退审的可以 删除记录，审核的 不可以删除，退审的可以恢复，其他不可以
    '''
    planrecordquery = PlanRecord.objects.filter(pk__in=recordids)
    for record in planrecordquery:
        if '3'!=record.planno.status:
            return getResult(False,False,u'主计划记录恢复失败,流水号：%s，不是退审状态'%record.planno.lsh)
    planrecordquery.update(isdel=False)
    PlanDetail.objects.filter(planrecord__in=planrecordquery).update(isdel=True)
    return getResult(recordids,True,u'删除主计划记录成功')


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
    if planno and len(planno):
        planno = planno[0]
    else:
        return getResult(False,False,u'主计划不存在')
    if planno.bianzhi_id == request.user.id:
        return getResult(False,False,u'不能 审核 自己编制的主计划')
    if planno.status == "2":
        return getResult(False,False,u'已经审核过的主计划 不能 再次 审核')

    planno.status = '2'
    planno.shenhe = request.user
    planno.save()
    PlanDetail.objects.filter(planrecord__in=PlanRecord.objects.filter(planno=planno)).filter(isdel=True).delete()
    PlanRecord.objects.filter(planno=planno).filter(isdel=True).delete()
    PlanDetail.objects.filter(planrecord__in=PlanRecord.objects.filter(planno=planno)).filter(isdel=False).update(oldData=None)
    PlanRecord.objects.filter(planno=planno).filter(isdel=False).update(oldData=None)
    for planrecord in PlanRecord.objects.filter(planno=planno).filter(isdel=False):
        if 0==Zydh.objects.filter(orderlist=planrecord.orderlist_id,zydh=planrecord.zydh).count():
            try:
                zydh=Zydh()
                zydh.zydh=planrecord.zydh
                zydh.orderlist_id=planrecord.orderlist_id
                zydh.save()
            except:
                pass
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
    if planno and len(planno):
        planno = planno[0]
    else:
        return getResult(False,False,u'主计划不存在')

    if planno.bianzhi_id == request.user.id:
        return getResult(False,False,u'不能 退审 自己编制的主计划')
    if planno.status != "2":
        return getResult(False,False,u'未审核过的主计划 不能 退审')
    planno.status = '3'
    planno.shenhe = request.user
    planno.save()
    PlanDetail.objects.filter(planrecord__in=PlanRecord.objects.filter(planno=planno)).filter(isdel=True).delete()
    PlanRecord.objects.filter(planno=planno).filter(isdel=True).delete()
    for planrecord in PlanRecord.objects.filter(planno=planno):
        oldData={"yddbh":planrecord.orderlist_id}
        oldData['zydh'] = planrecord.zydh
        oldData['plannum'] = planrecord.plannum
        oldData['planbz'] = planrecord.planbz
        oldData['ordergongyi'] = planrecord.ordergongyi
        oldData['level'] = planrecord.level
        oldData['isdel'] = planrecord.isdel
        PlanRecord.objects.filter(pk=planrecord.pk).update(oldData=json.dumps(oldData))

    for plandetail in PlanDetail.objects.filter(planrecord__in=PlanRecord.objects.filter(planno=planno).filter(isdel=False)).filter(isdel=False):
        oldData={}
        oldData['startdate%s'%plandetail.startsite_id] = plandetail.startdate.strftime('%Y/%m/%d')
        if plandetail.enddate:
            oldData['enddate%s'%plandetail.startsite_id] = plandetail.enddate.strftime('%Y/%m/%d')
        else:
            oldData['enddate%s'%plandetail.startsite_id] = u'永久'
        oldData['zrwz%s'%plandetail.startsite_id] = plandetail.endsite_id
        PlanDetail.objects.filter(pk=plandetail.pk).update(oldData=json.dumps(oldData))


    return getResult(True,True,u'退审 主计划成功，流水号为：%s'%planno.lsh)


def getAllPlanNo(request):
    l=[]
    for plan in PlanNo.objects.filter(status='2').filter(isdel=False):
        l.append({'id':plan.pk,'lsh':plan.lsh})
    return getResult(l)

@permission_required('ztmanage.plan_query')
def queryPlanDetail(request,obj):
    query = PlanDetail.objects.filter(planrecord__in=PlanRecord.objects.filter(planno__in=PlanNo.objects.filter(status='2')))
    if getattr(obj,'trstart','') and getattr(obj,'trend',''):
        query = query.filter(startdate__gte=str2date2(getattr(obj,'trstart')),startdate__lte=str2date2(getattr(obj,'trend')))
    if getattr(obj,'wcstart','') and getattr(obj,'wcend',''):
        query = query.filter(enddate__gte=str2date2(getattr(obj,'wcstart')),enddate__lte=str2date2(getattr(obj,'wcend')))
    if getattr(obj,'site',''):
        query = query.filter(startsite=getattr(obj,'site'))
    if getattr(obj,'zydh',''):
        query = query.filter(planrecord__in=PlanRecord.objects.filter(zydh=getattr(obj,'zydh')))
    if getattr(obj,'planid',''):
        query = query.filter(planrecord__in=PlanRecord.objects.filter(planno=PlanNo.objects.get(pk=getattr(obj,'planid'))))
    if getattr(obj,'orderbhid',''):
        query = query.filter(planrecord__in=PlanRecord.objects.filter(orderlist__in=OrderList.objects.filter(ddbh=getattr(obj,'orderbhid'))))
    if getattr(obj,'codeid',''):
        query = query.filter(planrecord__in=PlanRecord.objects.filter(orderlist__in=OrderList.objects.filter(code=getattr(obj,'codeid'))))

    l=[]
    for pd in query:
        r={'id':pd.pk,'planfinish':u'未投','planfinish_i':0,'orderlistid':pd.planrecord.orderlist_id,'code':pd.planrecord.orderlist.code_id,'codestr':pd.planrecord.orderlist.code.code,'codename':pd.planrecord.orderlist.code.name,'codegg':pd.planrecord.orderlist.code.gg,'scx':pd.planrecord.orderlist.code.scx_id,'scxstr':pd.planrecord.orderlist.code.scx.name,'ddbh':pd.planrecord.orderlist.ddbh.ddbh,'ddbh_id':pd.planrecord.orderlist.ddbh_id,'finishstartdate':'','finishstartnum':0,'finishenddate':'','finishendnum':0,'bfnum':0,'ysnum':0}
        r['startsite']=pd.startsite.name
        r['startsite_id']=pd.startsite_id
        if pd.endsite_id:
            r['endsite']=pd.endsite.name
            r['endsite_id']=pd.endsite_id
        else:
            r['endsite']=''
            r['endsite_id']=''

        r['zydh']=pd.planrecord.zydh
        r['level']=PLANSTATUS[pd.planrecord.level]
        r['plannum']=pd.planrecord.plannum
        r['startdate']=date2str(pd.startdate)
        r['enddate']=date2str(pd.enddate)
        r['planlsh']=pd.planrecord.planno.lsh
        r['ordergongyi']=pd.planrecord.ordergongyi
        r['planbz']=pd.planrecord.planbz

        l.append(r)
    # for r in l:
    #     r.update(queryPlanDetailComputer(r.get('id'),r.get('zydh'),r.get('orderlistid'),r.get('startsite_id'),r.get('endsite_id',None)))
    lm={}
    zrorderlist=[]
    zydhlist=[]
    startsitelist=[]
    hasendzrorderlist=[]
    hasendzydhlist=[]
    hasendstartsitelist=[]
    hasendendsitelist=[]

    noendzrorderlist=[]
    noendzydhlist=[]
    noendstartsitelist=[]

    for r in l:
        lm['z%(zydh)so%(orderlistid)ss%(startsite_id)se%(endsite_id)s'%r]=r
        lm['z%(zydh)so%(orderlistid)ss%(startsite_id)s'%r]=r
        zrorderlist.append(r['orderlistid'])
        zydhlist.append(r['zydh'])
        startsitelist.append(r['startsite_id'])
        if r.get('endsite_id',''):
            hasendendsitelist.append(r['endsite_id'])
            hasendzrorderlist.append(r['orderlistid'])
            hasendzydhlist.append(r['zydh'])
            hasendstartsitelist.append(r['startsite_id'])
        else:
            noendzrorderlist.append(r['orderlistid'])
            noendzydhlist.append(r['zydh'])
            noendstartsitelist.append(r['startsite_id'])

    for obb in OrderBB.objects.filter(zrorder__in=zrorderlist,yzydh__in=zydhlist,zrwz__in=startsitelist):
        if lm.has_key('z%so%ss%s'%(obb.yzydh,obb.zrorder_id,obb.zrwz_id)):
            lm['z%so%ss%s'%(obb.yzydh,obb.zrorder_id,obb.zrwz_id)]['finishstartnum']+=obb.zrwznum
            if not lm['z%so%ss%s'%(obb.yzydh,obb.zrorder_id,obb.zrwz_id)]['finishstartdate'] or lm['z%so%ss%s'%(obb.yzydh,obb.zrorder_id,obb.zrwz_id)]['finishstartdate']<obb.lsh.lsh.split('-')[0]:
                lm['z%so%ss%s'%(obb.yzydh,obb.zrorder_id,obb.zrwz_id)]['finishstartdate']=obb.lsh.lsh.split('-')[0]

    for obb in OrderBB.objects.filter(yorder__in=noendzrorderlist,yzydh__in=noendzydhlist,ywz__in=noendstartsitelist,zrwz=None):
        if lm.has_key('z%so%ss%s'%(obb.yzydh,obb.zrorder_id,obb.ywz_id)):
            lm['z%so%ss%s'%(obb.yzydh,obb.zrorder_id,obb.zrwz_id)]['finishendnum']+=obb.ywznum
            if not lm['z%so%ss%s'%(obb.yzydh,obb.zrorder_id,obb.zrwz_id)]['finishenddate'] or lm['z%so%ss%s'%(obb.yzydh,obb.zrorder_id,obb.zrwz_id)]['finishenddate']<obb.lsh.lsh.split('-')[0]:
                lm['z%so%ss%s'%(obb.yzydh,obb.zrorder_id,obb.zrwz_id)]['finishenddate']=obb.lsh.lsh.split('-')[0]
    for obb in OrderBB.objects.filter(yorder__in=hasendzrorderlist,yzydh__in=hasendzydhlist,ywz__in=hasendstartsitelist,zrwz__in=hasendendsitelist):
        if lm.has_key('z%so%ss%se%s'%(obb.yzydh,obb.zrorder_id,obb.ywz_id,obb.zrwz_id)):
            lm['z%so%ss%se%s'%(obb.yzydh,obb.zrorder_id,obb.ywz_id,obb.zrwz_id)]['finishendnum']+=obb.ywznum
            if not lm['z%so%ss%se%s'%(obb.yzydh,obb.zrorder_id,obb.ywz_id,obb.zrwz_id)]['finishenddate'] or lm['z%so%ss%se%s'%(obb.yzydh,obb.zrorder_id,obb.ywz_id,obb.zrwz_id)]['finishenddate']<obb.lsh.lsh.split('-')[0]:
                lm['z%so%ss%se%s'%(obb.yzydh,obb.zrorder_id,obb.ywz_id,obb.zrwz_id)]['finishenddate']=obb.lsh.lsh.split('-')[0]
    for r in l:
        if r['finishstartnum']==0:
            r['planfinish']=u'未投'
            r['planfinish_i']=1
        elif r['finishstartnum']==r['finishendnum']+r['bfnum']+r['ysnum']:
            r['planfinish']=u'完成'
            r['planfinish_i']=2
        elif r['finishstartnum']>r['finishendnum']+r['bfnum']+r['ysnum']:
            r['planfinish']=u'在线'
            r['planfinish_i']=3
        else:
            r['planfinish']=u'异常'
            r['planfinish_i']=4
    return getResult(l)


def queryPlanDetailComputer(id,zydh,orderlist,startsite,endsite=None):

    r={'id':id,'finishstartdate':'','finishstartnum':0,'finishenddate':'','finishendnum':0,'bfnum':0,'ysnum':0}

    for obb in OrderBB.objects.filter(zrorder=orderlist,yzydh=zydh,zrwz=startsite):
        r['finishstartnum']+=obb.zrwznum
        if not r['finishstartdate'] or r['finishstartdate']<obb.lsh.lsh.split('-')[0]:
            r['finishstartdate']=obb.lsh.lsh.split('-')[0]

    query = OrderBB.objects.filter(yorder=orderlist,yzydh=zydh,yzw=startsite)
    if endsite:
        query = query.filter(zrwz=endsite)
    for obb in query:
        r['finishendnum']+=obb.ywznum
        r['bfnum']+=obb.bfnum
        r['ysnum']+=obb.ysnum

        if not r['finishenddate'] or r['finishenddate']<obb.lsh.lsh.split('-')[0]:
            r['finishenddate']=obb.lsh.lsh.split('-')[0]
    if r['finishstartnum']==0:
        r['planfinish']=u'未投'
        r['planfinish_i']=0
    elif r['finishstartnum']>=r['finishendnum']+r['bfnum']+r['ysnum']:
        r['planfinish']=u'完成'
        r['planfinish_i']=1
    else:
        r['planfinish']=u'在线'
        r['planfinish_i']=2
    return r

def queryPlanDetailItem(request,id,zydh,orderlist,startsite,endsite=None):

    return getResult(queryPlanDetailComputer(id,zydh,orderlist,startsite,endsite))

@login_required
@permission_required('ztmanage.plan_daily')
def queryPlanDaily(request,startdate,enddate):
    '''
    日计划完成情况
    1.根据日期，查找计划
    2.根据日期，查找日报表
    3.根据日报表，逆推计划
    '''
    datelist=[]
    datamap={}
    for bb in OrderBB.objects.filter(lsh__in=OrderBBNo.objects.filter(lsh__gte=startdate,lsh__lte=enddate)):
        d=bb.lsh.lsh.split('-')[0]
        if d not in datelist:
            datelist.append(d)
            datamap[d]={'date':d,'bzxiangjh':0,'bzxiangsj':0,'bzjianjh':0,'bzjiansj':0,'qqxingsj':0,'qqjiansj':0,'tqxiangsj':0,'tqjiansj':0,'jianri':0,'xiangri':0}
        datamap[d]




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

    query = query.order_by('-updateTime')

    resultlist=[]
    for plan in query:
        r={'id':plan.pk,'lsh':plan.lsh,'shenhe':getattr(getattr(plan,"shenhe",{}),"last_name",""),'bianzhi':getattr(getattr(plan,"bianzhi",{}),"last_name",""),'updateTime':plan.updateTime.strftime('%Y/%m/%d'),'status':plan.status}
        r['lastcheckTime']=''
        if plan.lastcheckTime:
            r['lastcheckTime']=plan.lastcheckTime.strftime('%Y/%m/%d')
        resultlist.append(r)
    return getResult(resultlist)



@login_required
def queryPlanByUser(request,status=1):
    return queryPlanBy(request,request.user,None,None,None,None,None,status)

@login_required
@permission_required('ztmanage.plan_all')
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

def getZYDHByOrderList(request,orderlistids):
    '''
    根据订单，查询出 使用过的 作业单号
    '''
    zybhlist = []
    if isinstance(orderlistids,int):
        query =Zydh.objects.filter(orderlist=orderlistids)
    elif len(orderlistids)>0:
        query =Zydh.objects.filter(orderlist__in=orderlistids)
    else:
        return getResult({'orderlist%s'%orderlistids:zybhlist})
    for zydh in query:

        if zydh.zydh not in zybhlist:
            zybhlist.append({'txt':zydh.zydh})
    return getResult({'orderlist%s'%orderlistids:zybhlist})

def getZYDHByCode(request,codeListids):
    '''
    根据订单，查询出 使用过的 作业单号
    '''
    zydhdict = {}
    for zydh in Zydh.objects.filter(orderlist__in=OrderList.objects.filter(code__in=codeListids)):
        k='orderlist%s'%zydh.orderlist_id
        if not zydhdict.has_key(k):
            zydhdict[k]=set()
        if zydh.zydh not in  zydhdict[k]:
            zydhdict[k].add(zydh.zydh)
    return getResult(zydhdict)


@transaction.commit_on_success
def initZYDH(request):
    zybhset=set()
    for zydh in Zydh.objects.all():
        zybhset.add((zydh.orderlist_id,zydh.zydh))
    zybhlist=[]
    for bb in OrderBB.objects.all():
        if (bb.yorder_id,bb.yzydh.strip().upper()) not in zybhset:
            zybhset.add((bb.yorder_id,bb.yzydh.strip().upper()))
            zybhlist.append((bb.yorder_id,bb.yzydh.strip().upper()))
    for oid,zy in zybhlist:
        try:
            zydh=Zydh()
            zydh.orderlist_id=oid
            zydh.zydh =zy
            zydh.save()
        except Exception,e:
            print e

    url='http://'+request.META['HTTP_HOST']+'/static/swf/'
    return render_to_response('zt/index.html',{'url':url,'p':datetime.datetime.now()})







