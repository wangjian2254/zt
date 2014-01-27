#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime, json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render_to_response
from models import OrderList, OrderNo, OrderBB, PlanNo, PlanRecord, PlanDetail, ProductSite, Ztperm, Zydh, OrderBBNo, Code, PlanChangeLog
from tools import planchange_required, permission_required, getResult, newPlanLSHNoByUser, getOrderByOrderlistid, getCodeNameById, str2date, str2date2, PLANSTATUS, date2str
from errors import PlanRecordError

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


@login_required
@planchange_required('ztmanage.plan_update')
@transaction.commit_on_success
def updatePlan(request, sitelist, unsitelist, planrecordlist, lsh=None):
    '''
    编制保存主计划，没有经过审核的主计划可以任意修改。
    审核状态的主计划，不可以修改，
    '''
    try:
        with transaction.commit_on_success():
            if lsh:
                planno = PlanNo.objects.get(lsh=lsh)
                planno.updateTime = datetime.datetime.now()
                if '2' == planno.status:
                    return getResult(planno, False, u'计划修改失败,流水号：%s，已经审核过了' % planno.lsh)
                for delsite in unsitelist:
                    PlanDetail.objects.filter(
                        planrecord__in=PlanRecord.objects.filter(planno=planno).filter(isdel=False)).filter(
                        startsite=getattr(delsite, 'id')).filter(isdel=False).update(isdel=True)
            else:
                planno = PlanNo()
                planno.updateTime = datetime.datetime.now()
                planno.lsh = newPlanLSHNoByUser(request.user)
                planno.status = '1'
            planno.updateTime = datetime.datetime.now()
            planno.bianzhi = request.user
            planno.save()

            for planrecordobj in planrecordlist:
                if hasattr(planrecordobj, 'id'):
                    planrecord = PlanRecord.objects.get(pk=getattr(planrecordobj, 'id'))
                else:
                    planrecord = PlanRecord()
                    planrecord.planno = planno
                planrecord.orderlist = OrderList.objects.get(pk=getattr(planrecordobj, 'yddbh'))
                planrecord.zydh = getattr(planrecordobj, 'zydh', '').strip().upper()
                planrecord.plannum = int(getattr(planrecordobj, 'plannum', 0))
                planrecord.level = int(getattr(planrecordobj, 'level', 0))
                planrecord.planbz = getattr(planrecordobj, 'planbz', '')
                planrecord.ordergongyi = getattr(planrecordobj, 'ordergongyi', '')
                planrecord.save()
                for site in sitelist:
                    psite = ProductSite.objects.get(pk=getattr(site, 'id'))
                    plandetail = PlanDetail.objects.filter(planrecord=planrecord).filter(startsite=psite)[:1]
                    if len(plandetail):
                        plandetail = plandetail[0]
                    else:
                        plandetail = PlanDetail()
                        plandetail.planrecord = planrecord
                        plandetail.startsite = psite
                    plandetail.isdel = False
                    if not getattr(planrecordobj, 'startdate%s' % psite.id, None):
                        plandetail.isdel = True
                        if plandetail.pk:
                            plandetail.save()
                        continue
                    plandetail.startdate = str2date(getattr(planrecordobj, 'startdate%s' % psite.id))
                    if not hasattr(planrecordobj, 'enddate%s' % psite.id) or getattr(planrecordobj,
                                                                                     'enddate%s' % psite.id,
                                                                                     None) == u'永久':
                        plandetail.enddate = None
                    else:
                        plandetail.enddate = str2date(getattr(planrecordobj, 'enddate%s' % psite.id))
                    plandetail.startsite = psite
                    if getattr(planrecordobj, 'zrwz%s' % psite.id, None):
                        plandetail.endsite = ProductSite.objects.get(pk=getattr(planrecordobj, 'zrwz%s' % psite.id))
                    else:
                        plandetail.endsite = None

                    errorquery = PlanDetail.objects.filter(
                        planrecord__in=PlanRecord.objects.filter(orderlist=planrecord.orderlist,
                                                                 zydh=planrecord.zydh)).filter(
                        startsite=plandetail.startsite)
                    if plandetail.planrecord.zydh and not plandetail.pk and 0 < errorquery.count():
                        error = errorquery[0]
                        raise PlanRecordError(error.planrecord.planno_id, error.planrecord.orderlist_id,
                                              error.planrecord.zydh, error.startsite_id, error.endsite_id)
                    plandetail.save()
            return getResult(planno, True, u'计划制定成功,流水号：%s' % planno.lsh)
    except PlanRecordError, e:
        plan = PlanNo.objects.get(pk=e.planno)
        orderlist = OrderList.objects.get(pk=e.order)
        zydh = e.zydh
        startsite = ProductSite.objects.get(pk=e.startsite)
        if e.endsite:
            endsite = ProductSite.objects.get(pk=e.endsite)
        else:
            endsite = {}
        msg = u'订单号为：%s ,物料号为：%s ,作业单号为：%s ,投入位置为：%s ，去向位置为：%s ，这条计划和流水号：%s 主计划中的一条计划重复。' % (
            orderlist.ddbh.ddbh, orderlist.code.code, zydh, startsite.name, getattr(endsite, 'name', u'无'), plan.lsh)
        return getResult(False, False, msg)


@login_required
@planchange_required('ztmanage.plan_update')
@transaction.commit_on_success
def updatePlanZYDH(request, zydhlist):
    '''
    只有审核状态的主计划项的作业单号，可以修改，
    '''
    planidlist = []
    for obj in zydhlist:
        planidlist.append(getattr(obj, "recordid", 0))
        try:
            planrecord = PlanRecord.objects.get(pk=getattr(obj, "recordid", 0))
            if planrecord.planno.status != '2':
                return getResult(False, False, u'只有审核过的计划才需要单独使用 作业单号修改，其他情况正常修改即可。')
            planrecord.zydh = getattr(obj, 'zydh', '').strip().upper()
            planrecord.save()
            if 0 == Zydh.objects.filter(orderlist=planrecord.orderlist_id, zydh=planrecord.zydh).count():
                try:
                    zydh = Zydh()
                    zydh.zydh = planrecord.zydh
                    zydh.orderlist_id = planrecord.orderlist_id
                    zydh.save()
                except:
                    pass
        except:
            return getResult(False, False, u'只有审核过的计划才需要单独使用 作业单号修改，其他情况正常修改即可。')

    return getResult(True, True, u'作业单号修改成功')


@login_required
def getPlanDetailByIdOrLsh(request, obj):
    lsh = None
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
        return getResult(False, False, u'主计划不存在')

    resultlist = []
    for record in PlanRecord.objects.filter(planno=planno):
        orderlist = getOrderByOrderlistid(record.orderlist_id)
        code = getCodeNameById(orderlist.get('code'))
        planrecord = {"id": record.pk, 'yddbh': record.orderlist_id, 'code': code.get('id'),
                      'codestr': code.get('code'), 'codename': code.get('name'), 'codegg': code.get('gg'),
                      'scx': code.get('scx')}
        planrecord['zydh'] = record.zydh
        planrecord['plannum'] = record.plannum
        planrecord['planbz'] = record.planbz
        planrecord['ordergongyi'] = record.ordergongyi
        planrecord['level'] = record.level
        planrecord['isdel'] = record.isdel
        if record.oldData:
            planrecord['oldDataDict'] = json.loads(record.oldData)
        else:
            planrecord['oldDataDict'] = {}

        for plandetail in PlanDetail.objects.filter(planrecord=record):
            planrecord['startdate%s' % plandetail.startsite_id] = plandetail.startdate.strftime('%Y/%m/%d')
            if plandetail.enddate:
                planrecord['enddate%s' % plandetail.startsite_id] = plandetail.enddate.strftime('%Y/%m/%d')
            else:
                planrecord['enddate%s' % plandetail.startsite_id] = u'永久'
            planrecord['zrwz%s' % plandetail.startsite_id] = plandetail.endsite_id
            if plandetail.oldData:
                planrecord['oldDataDict'].update(json.loads(plandetail.oldData))
            planrecord['isdel%s' % plandetail.startsite_id] = plandetail.isdel
        if not planrecord['oldDataDict']:
            del planrecord['oldDataDict']
        resultlist.append(planrecord)
    return getResult({"list": resultlist, 'plan': planno})


@login_required
@planchange_required('ztmanage.plan_update')
@transaction.commit_on_success
def updatePlanDelete(request, recordids):
    '''
    1.判断 计划是否审核过，退审的可以 删除记录，审核的 不可以删除，退审的可以恢复，其他不可以
    '''
    planrecordquery = PlanRecord.objects.filter(pk__in=recordids)
    for record in planrecordquery:
        if '2' == record.planno.status:
            return getResult(False, False, u'主计划记录删除失败,流水号：%s，已经审核过了' % record.planno.lsh)
        if '1' == record.planno.status:
            PlanDetail.objects.filter(planrecord=record).delete()
            record.delete()
        else:
            record.isdel = True
            record.save()
            PlanDetail.objects.filter(planrecord=record).update(isdel=True)
    return getResult(recordids, True, u'删除主计划记录成功')


@login_required
@planchange_required('ztmanage.plan_update')
@transaction.commit_on_success
def updatePlanUNDelete(request, recordids):
    '''
    1.判断 计划是否审核过，退审的可以 删除记录，审核的 不可以删除，退审的可以恢复，其他不可以
    '''
    planrecordquery = PlanRecord.objects.filter(pk__in=recordids)
    for record in planrecordquery:
        if '3' != record.planno.status:
            return getResult(False, False, u'主计划记录恢复失败,流水号：%s，不是退审状态' % record.planno.lsh)
    planrecordquery.update(isdel=False)
    PlanDetail.objects.filter(planrecord__in=planrecordquery).update(isdel=False)
    return getResult(recordids, True, u'删除主计划记录成功')

@login_required
def checkPlanDetail(request,orderbblist,lsh=None):
    '''
    计算投入数量 是否 超过 计划数量
    1. 区分是保存 还是 修改。修改则排除这一条，计算是否超出计划数量

    '''
    messagelist=[]
    for i,obj in enumerate(orderbblist) :
        zrwz = obj.get('zrwz',None)
        if not zrwz:
            continue
        orderlistid = obj.get('zrorder',None)
        orderbbid = obj.get('id',None)
        zydh = obj.get('yzydh','').strip()
        num = obj.get('zrwznum',0)
        totalnum = num
        for orderbb in OrderBB.objects.filter(zrorder=orderlistid,yzydh=zydh,zrwz=zrwz):
            if orderbb.pk != orderbbid:
                totalnum+=orderbb.zrwznum
        plandetailquery = PlanDetail.objects.filter(startsite=zrwz,planrecord__in=PlanRecord.objects.filter(orderlist=orderlistid,zydh=zydh).filter(planno__in=PlanNo.objects.filter(status='2')))
        for detail in plandetailquery:
            if detail.planrecord.plannum < totalnum:
                messagelist.append(u'第 %s 条数据，订单号：%s ,物料号：%s ,作业单号：%s ,超过了主计划流水号 %s 的计划数\n\t'%(i+1,detail.planrecord.orderlist.ddbh.ddbh,detail.planrecord.orderlist.code.name,detail.planrecord.zydh,detail.planrecord.planno.lsh))
    if messagelist:
        return getResult(False,True,''.join(messagelist))
    else:
        return getResult(True)


    #orderBBList=[]
    #for obj in orderbblist:
    #    o=OrderBB()
    #    if obj.has_key('id'):
    #        o.pk=obj['id']
    #    o.lsh=lsh
    #    o.yorder=OrderList.objects.get(pk=obj['yorder'])
    #    o.yzydh=obj['yzydh'].strip()
    #    if obj.has_key('ywz'):
    #        o.ywz=ProductSite.objects.get(pk=obj['ywz'])
    #        o.ywznum=obj['ywznum']
    #    o.zrorder=OrderList.objects.get(pk=obj['zrorder'])
    #    if obj.has_key('zrwz'):
    #        o.zrwz=ProductSite.objects.get(pk=obj['zrwz'])
    #        o.zrwznum=obj['zrwznum']
    #    o.bfnum=obj['bfnum']
    #    o.ysnum=obj['ysnum']
    #    o.ywzsynum=obj['ywzsynum']
    #    o.bztext=obj['bztext']
    #    o.save()

@login_required
@permission_required('ztmanage.plan_check')
@transaction.commit_on_success
def checkPlan(request, obj):
    lsh = None
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
        return getResult(False, False, u'主计划不存在')
    if planno.bianzhi_id == request.user.id:
        return getResult(False, False, u'不能 审核 自己编制的主计划')
    if planno.status == "2":
        return getResult(False, False, u'已经审核过的主计划 不能 再次 审核')

    planno.status = '2'
    planno.shenhe = request.user
    planno.save()
    PlanDetail.objects.filter(planrecord__in=PlanRecord.objects.filter(planno=planno)).filter(isdel=True).delete()
    PlanRecord.objects.filter(planno=planno).filter(isdel=True).delete()
    PlanDetail.objects.filter(planrecord__in=PlanRecord.objects.filter(planno=planno)).filter(isdel=False).update(
        oldData=None)
    PlanRecord.objects.filter(planno=planno).filter(isdel=False).update(oldData=None)
    for planrecord in PlanRecord.objects.filter(planno=planno).filter(isdel=False):
        if 0 == Zydh.objects.filter(orderlist=planrecord.orderlist_id, zydh=planrecord.zydh).count():
            try:
                zydh = Zydh()
                zydh.zydh = planrecord.zydh
                zydh.orderlist_id = planrecord.orderlist_id
                zydh.save()
            except:
                pass
    return getResult(True, True, u'审核 主计划成功，流水号为：%s' % planno.lsh)


@login_required
@permission_required('ztmanage.plan_uncheck')
@transaction.commit_on_success
def uncheckPlan(request, obj):
    lsh = None
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
        return getResult(False, False, u'主计划不存在')

    if planno.bianzhi_id == request.user.id:
        return getResult(False, False, u'不能 退审 自己编制的主计划')
    planno.status = '3'
    planno.shenhe = request.user
    planno.save()
    pclogb = False
    for pclog in PlanChangeLog.objects.filter(user=planno.bianzhi,date=datetime.datetime.now()):
        pclog.count+=1
        pclog.save()
        pclogb = True
    if not pclogb:
        pclog=PlanChangeLog()
        pclog.user=planno.bianzhi
        pclog.count=1
        pclog.save()
    PlanDetail.objects.filter(planrecord__in=PlanRecord.objects.filter(planno=planno)).filter(isdel=True).delete()
    PlanRecord.objects.filter(planno=planno).filter(isdel=True).delete()
    for planrecord in PlanRecord.objects.filter(planno=planno):
        oldData = {"yddbh": planrecord.orderlist_id}
        oldData['zydh'] = planrecord.zydh
        oldData['plannum'] = planrecord.plannum
        oldData['planbz'] = planrecord.planbz
        oldData['ordergongyi'] = planrecord.ordergongyi
        oldData['level'] = planrecord.level
        oldData['isdel'] = planrecord.isdel
        PlanRecord.objects.filter(pk=planrecord.pk).update(oldData=json.dumps(oldData))

    for plandetail in PlanDetail.objects.filter(
            planrecord__in=PlanRecord.objects.filter(planno=planno).filter(isdel=False)).filter(isdel=False):
        oldData = {}
        oldData['startdate%s' % plandetail.startsite_id] = plandetail.startdate.strftime('%Y/%m/%d')
        if plandetail.enddate:
            oldData['enddate%s' % plandetail.startsite_id] = plandetail.enddate.strftime('%Y/%m/%d')
        else:
            oldData['enddate%s' % plandetail.startsite_id] = u'永久'
        oldData['zrwz%s' % plandetail.startsite_id] = plandetail.endsite_id
        PlanDetail.objects.filter(pk=plandetail.pk).update(oldData=json.dumps(oldData))

    return getResult(True, True, u'退审 主计划成功，流水号为：%s' % planno.lsh)


def getAllPlanNo(request):
    l = []
    for plan in PlanNo.objects.filter(status='2').filter(isdel=False):
        l.append({'id': plan.pk, 'lsh': plan.lsh})
    return getResult(l)

@permission_required('ztmanage.plan_detail_close')
@transaction.commit_on_success
def closePlanDetail(request,idarr):

    num = PlanDetail.objects.filter(pk__in=idarr).update(isclose=True)
    PlanDetail.objects.filter(pk__in=idarr).update(isonline=False)

    return getResult(num,True,u'强制关闭了%s条计划，请重新查询，获取最新数据'%num)

@permission_required('ztmanage.plan_detail_online')
@transaction.commit_on_success
def onlinePlanDetail(request,idarr):

    PlanDetail.objects.filter(pk__in=idarr).update(isclose=False)
    num = PlanDetail.objects.filter(pk__in=idarr).update(isonline=True)

    return getResult(num,True,u'重置在线了%s条计划，请重新查询，获取最新数据'%num)

@permission_required('ztmanage.plan_query')
def queryPlanDetail(request, obj):
    query = PlanDetail.objects.filter(
        planrecord__in=PlanRecord.objects.filter(planno__in=PlanNo.objects.filter(status='2')))
    if getattr(obj, 'trstart', '') and getattr(obj, 'trend', ''):
        query = query.filter(startdate__gte=str2date2(getattr(obj, 'trstart')),
                             startdate__lte=str2date2(getattr(obj, 'trend')))
    if getattr(obj, 'wcstart', '') and getattr(obj, 'wcend', ''):
        query = query.filter(enddate__gte=str2date2(getattr(obj, 'wcstart')),
                             enddate__lte=str2date2(getattr(obj, 'wcend')))
    if getattr(obj, 'site', ''):
        query = query.filter(startsite=getattr(obj, 'site'))
    if getattr(obj, 'zydh', ''):
        query = query.filter(planrecord__in=PlanRecord.objects.filter(zydh=getattr(obj, 'zydh')))
    if getattr(obj, 'planid', ''):
        query = query.filter(
            planrecord__in=PlanRecord.objects.filter(planno=PlanNo.objects.get(pk=getattr(obj, 'planid'))))
    if getattr(obj, 'orderbhid', ''):
        query = query.filter(planrecord__in=PlanRecord.objects.filter(
            orderlist__in=OrderList.objects.filter(ddbh=getattr(obj, 'orderbhid'))))
    if getattr(obj, 'codeid', ''):
        query = query.filter(planrecord__in=PlanRecord.objects.filter(
            orderlist__in=OrderList.objects.filter(code=getattr(obj, 'codeid'))))

    l = []
    for pd in query:
        r = {'id': pd.pk, 'planfinish': u'未投', 'planfinish_i': 0, 'orderlistid': pd.planrecord.orderlist_id,
             'code': pd.planrecord.orderlist.code_id, 'codestr': pd.planrecord.orderlist.code.code,
             'codename': pd.planrecord.orderlist.code.name, 'codegg': pd.planrecord.orderlist.code.gg,
             'scx': pd.planrecord.orderlist.code.scx_id, 'scxstr': pd.planrecord.orderlist.code.scx.name,
             'ddbh': pd.planrecord.orderlist.ddbh.ddbh, 'ddbh_id': pd.planrecord.orderlist.ddbh_id, 'isclose':pd.isclose, 'isonline':pd.isonline,
             'finishstartdate': '', 'finishstartnum': 0, 'finishenddate': '', 'finishendnum': 0, 'bfnum': 0, 'ysnum': 0}
        r['startsite'] = pd.startsite.name
        r['startsite_id'] = pd.startsite_id
        if pd.endsite_id:
            r['endsite'] = pd.endsite.name
            r['endsite_id'] = pd.endsite_id
        else:
            r['endsite'] = ''
            r['endsite_id'] = ''

        r['zydh'] = pd.planrecord.zydh
        r['level'] = PLANSTATUS[pd.planrecord.level]
        r['plannum'] = pd.planrecord.plannum
        r['startdate'] = date2str(pd.startdate)
        r['enddate'] = date2str(pd.enddate)
        r['planlsh'] = pd.planrecord.planno.lsh
        r['ordergongyi'] = pd.planrecord.ordergongyi
        r['planbz'] = pd.planrecord.planbz

        l.append(r)
        # for r in l:
    #     r.update(queryPlanDetailComputer(r.get('id'),r.get('zydh'),r.get('orderlistid'),r.get('startsite_id'),r.get('endsite_id',None)))
    lm = {}
    zrorderlist = []
    zydhlist = []
    startsitelist = []
    hasendzrorderlist = []
    hasendzydhlist = []
    hasendstartsitelist = []
    hasendendsitelist = []

    noendzrorderlist = []
    noendzydhlist = []
    noendstartsitelist = []

    for r in l:
        lm['z%(zydh)so%(orderlistid)ss%(startsite_id)se%(endsite_id)s' % r] = r
        lm['z%(zydh)so%(orderlistid)ss%(startsite_id)s' % r] = r
        zrorderlist.append(r['orderlistid'])
        zydhlist.append(r['zydh'])
        startsitelist.append(r['startsite_id'])
        if r.get('endsite_id', ''):
            hasendendsitelist.append(r['endsite_id'])
            hasendzrorderlist.append(r['orderlistid'])
            hasendzydhlist.append(r['zydh'])
            hasendstartsitelist.append(r['startsite_id'])
        else:
            noendzrorderlist.append(r['orderlistid'])
            noendzydhlist.append(r['zydh'])
            noendstartsitelist.append(r['startsite_id'])

    for obb in OrderBB.objects.filter(zrorder__in=zrorderlist, yzydh__in=zydhlist, zrwz__in=startsitelist):
        if lm.has_key('z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.zrwz_id)):
            lm['z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.zrwz_id)]['finishstartnum'] += obb.zrwznum
            if not lm['z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.zrwz_id)]['finishstartdate'] or \
                            lm['z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.zrwz_id)]['finishstartdate'] < \
                            obb.lsh.lsh.split('-')[0]:
                lm['z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.zrwz_id)]['finishstartdate'] = obb.lsh.lsh.split('-')[
                    0]

    for obb in OrderBB.objects.filter(yorder__in=noendzrorderlist, yzydh__in=noendzydhlist, ywz__in=noendstartsitelist,
                                      zrwz=None):
        if lm.has_key('z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id)):
            lm['z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id)]['finishendnum'] += obb.zrwznum
            lm['z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id)]['bfnum'] += obb.bfnum
            lm['z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id)]['ysnum'] += obb.ysnum
            if not lm['z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id)]['finishenddate'] or \
                            lm['z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id)]['finishenddate'] < \
                            obb.lsh.lsh.split('-')[0]:
                lm['z%so%ss%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id)]['finishenddate'] = obb.lsh.lsh.split('-')[0]
    for obb in OrderBB.objects.filter(yorder__in=hasendzrorderlist, yzydh__in=hasendzydhlist,
                                      ywz__in=hasendstartsitelist, zrwz__in=hasendendsitelist):
        if lm.has_key('z%so%ss%se%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id, obb.zrwz_id)):
            lm['z%so%ss%se%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id, obb.zrwz_id)]['finishendnum'] += obb.zrwznum
            lm['z%so%ss%se%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id, obb.zrwz_id)]['bfnum'] += obb.bfnum
            lm['z%so%ss%se%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id, obb.zrwz_id)]['ysnum'] += obb.ysnum
            if not lm['z%so%ss%se%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id, obb.zrwz_id)]['finishenddate'] or \
                            lm['z%so%ss%se%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id, obb.zrwz_id)]['finishenddate'] < \
                            obb.lsh.lsh.split('-')[0]:
                lm['z%so%ss%se%s' % (obb.yzydh, obb.zrorder_id, obb.ywz_id, obb.zrwz_id)]['finishenddate'] = \
                    obb.lsh.lsh.split('-')[0]
    for r in l:
        if r['finishstartnum'] == 0:
            r['planfinish'] = u'未投'
            r['planfinish_i'] = 1
        elif r['finishstartnum'] == r['finishendnum'] + r['bfnum'] + r['ysnum']:
            r['planfinish'] = u'完成'
            r['planfinish_i'] = 2
        elif r['finishstartnum'] > r['finishendnum'] + r['bfnum'] + r['ysnum']:
            r['planfinish'] = u'在线'
            r['planfinish_i'] = 3
        else:
            r['planfinish'] = u'异常'
            r['planfinish_i'] = 4

        if r['isclose']==True:
            r['planfinish'] = u'强制关闭'
            r['planfinish_i'] = 5
        if r['isonline']==True:
            if r['plannum'] == r['finishendnum'] :
                r['planfinish'] = u'完成'
                r['planfinish_i'] = 2
            else:
                r['planfinish'] = u'在线'
                r['planfinish_i'] = 3
    return getResult(l)


def queryPlanDetailComputer(id, zydh, orderlist, startsite, endsite=None):
    r = {'id': id, 'finishstartdate': '', 'finishstartnum': 0, 'finishenddate': '', 'finishendnum': 0, 'bfnum': 0,
         'ysnum': 0}

    for obb in OrderBB.objects.filter(zrorder=orderlist, yzydh=zydh, zrwz=startsite):
        r['finishstartnum'] += obb.zrwznum
        if not r['finishstartdate'] or r['finishstartdate'] < obb.lsh.lsh.split('-')[0]:
            r['finishstartdate'] = obb.lsh.lsh.split('-')[0]

    query = OrderBB.objects.filter(yorder=orderlist, yzydh=zydh, yzw=startsite)
    if endsite:
        query = query.filter(zrwz=endsite)
    for obb in query:
        r['finishendnum'] += obb.ywznum
        r['bfnum'] += obb.bfnum
        r['ysnum'] += obb.ysnum

        if not r['finishenddate'] or r['finishenddate'] < obb.lsh.lsh.split('-')[0]:
            r['finishenddate'] = obb.lsh.lsh.split('-')[0]
    if r['finishstartnum'] == 0:
        r['planfinish'] = u'未投'
        r['planfinish_i'] = 0
    elif r['finishstartnum'] >= r['finishendnum'] + r['bfnum'] + r['ysnum']:
        r['planfinish'] = u'完成'
        r['planfinish_i'] = 1
    else:
        r['planfinish'] = u'在线'
        r['planfinish_i'] = 2
    return r


def queryPlanDetailItem(request, id, zydh, orderlist, startsite, endsite=None):
    return getResult(queryPlanDetailComputer(id, zydh, orderlist, startsite, endsite))


@login_required
@permission_required('ztmanage.plan_daily')
def queryPlanDaily(request, startdate, enddate, scxid, siteid, ismain):
    '''
    日计划完成情况
    1.根据日期，查找计划
    2.根据日期，查找日报表
    3.根据日报表，逆推计划
    '''
    if startdate > enddate:
        return getResult(None, False, u'开始日期必须小于结束日期')
    datelist = []
    datamap = {}

    startdatetime = str2date2(startdate)
    enddatetimestr = (str2date2(enddate) + datetime.timedelta(hours =24)).strftime('%Y%m%d')
    running = True
    while running:
        if startdatetime.strftime('%Y%m%d') not in datelist:
            datelist.append(startdatetime.strftime('%Y%m%d'))
            datamap[startdatetime.strftime('%Y%m%d')] = {'date': startdatetime.strftime('%Y%m%d'), 'bzxiangjh': 0,
                                                         'bzxiangsj': 0, 'bzjianjh': 0, 'bzjiansj': 0, 'qqxiangsj': 0,
                                                         'qqjiansj': 0, 'tqxiangsj': 0, 'tqjiansj': 0, 'jianri': 0,
                                                         'xiangri': 0}
        startdatetime += datetime.timedelta(hours=24)
        if startdatetime.strftime('%Y%m%d') > enddate:
            break
    projectdict = {}#本期完成
    projectdicttq = {}#提前期完成
    projectdictqq = {}#追前期完成
    # projectkey = '%s_%s_%s_%s'

    precordquery = PlanRecord.objects.filter(planno__in=PlanNo.objects.filter(status='2'))
    if scxid:
        if ismain == 1 or ismain == '1':
            cq = Code.objects.filter(scx=scxid).exclude(ismain=False)
        elif ismain == 2 or ismain == '2':
            cq = Code.objects.filter(scx=scxid, ismain=False)
        else:
            cq = Code.objects.filter(scx=scxid)
        precordquery = precordquery.filter(orderlist__in=OrderList.objects.filter(code__in=cq))
    else:
        cq = None
        if ismain == 1 or ismain == '1':
            cq = Code.objects.exclude(ismain=False)
        elif ismain == 2 or ismain == '2':
            cq = Code.objects.filter(ismain=False)
        if cq != None:
            precordquery = precordquery.filter(orderlist__in=OrderList.objects.filter(code__in=cq))
    pqurey = PlanDetail.objects.filter(
        planrecord__in=precordquery,
        enddate__gte=str2date2(startdate), enddate__lte=str2date2(enddate))
    if siteid:
        pqurey = pqurey.filter(startsite=siteid)

    for plan in pqurey:
        d = str(plan.enddate.strftime('%Y%m%d'))
        projectdict[(plan.planrecord.orderlist_id, plan.planrecord.zydh, plan.startsite_id, plan.endsite_id)] = {
            'date': d, 'finishdate': '', 'zrnum': 0, 'zcnum': 0, 'ysnum': 0, 'bfnum': 0}
        datamap[d]['bzxiangjh'] += 1
        datamap[d]['bzjianjh'] += plan.planrecord.plannum

    orderbbquery = OrderBB.objects.filter(lsh__in=OrderBBNo.objects.filter(lsh__gte=startdate, lsh__lt=enddatetimestr))
    if scxid:
        cq = Code.objects.filter(scx=scxid)
        if ismain == 1 or ismain == '1':
            cq = cq.exclude(ismain=False)
        elif ismain == 2 or ismain == '2':
            cq = cq.filter(ismain=False)
        orderbbquery = orderbbquery.filter(yorder__in=OrderList.objects.filter(code__in=cq))
    else:
        cq = None
        if ismain == 1 or ismain == '1':
            cq = Code.objects.exclude(ismain=False)
        elif ismain == 2 or ismain == '2':
            cq = Code.objects.filter(ismain=False)
        if cq != None:
            orderbbquery = orderbbquery.filter(yorder__in=OrderList.objects.filter(code__in=cq))
    if siteid:
        orderbbquery = orderbbquery.filter(ywz=siteid)

    for bb in orderbbquery:
        d = str(bb.lsh.lsh.split('-')[0])
        dictkey = (bb.yorder_id, bb.yzydh, bb.ywz_id, bb.zrwz_id)
        if projectdict.has_key(dictkey):
            datamap[d]['bzjiansj'] += bb.ywznum
            projectdict[dictkey]['finishdate'] = d
        elif bb.zrwz_id == None or bb.ywz_id ==None:
            continue
        else:
            if not (projectdicttq.has_key(dictkey) or projectdictqq.has_key(
                    dictkey)):
                for p in PlanDetail.objects.filter(startsite=bb.ywz_id, endsite=bb.zrwz_id).filter(
                        planrecord__in=PlanRecord.objects.filter(orderlist=bb.yorder_id, zydh=bb.yzydh).filter(
                                planno__in=PlanNo.objects.filter(status='2'))):
                    if not p.enddate:
                        continue
                    if p.enddate.strftime('%Y%m%d') > enddate:
                        projectdicttq[dictkey] = {
                            'date': p.enddate.strftime('%Y%m%d'), 'finishdate': '', 'zrnum': 0, 'zcnum': 0, 'ysnum': 0, 'bfnum': 0}
                    elif p.enddate.strftime('%Y%m%d') < startdate:
                        projectdictqq[dictkey] = {
                            'date': p.enddate.strftime('%Y%m%d'), 'finishdate': '', 'zrnum': 0, 'zcnum': 0, 'ysnum': 0, 'bfnum': 0}

            if projectdicttq.has_key(dictkey):
                datamap[d]['tqjiansj'] += bb.ywznum
                projectdicttq[dictkey]['finishdate'] = d
            elif projectdictqq.has_key(dictkey):
                datamap[d]['qqjiansj'] += bb.ywznum
                projectdictqq[dictkey]['finishdate'] = d

    for orderlistid, zydh, startsiteid, endsiteid in projectdict.keys():
        okey = (orderlistid, zydh, startsiteid, endsiteid)
        if not projectdict[okey]['finishdate']:
            continue
        for obb in OrderBB.objects.filter(zrorder=orderlistid, yzydh=zydh, zrwz=startsiteid).filter(
                lsh__in=OrderBBNo.objects.filter(lsh__lte=enddatetimestr)):
            projectdict[okey]['zrnum'] += obb.zrwznum
        for obb in OrderBB.objects.filter(yorder=orderlistid,yzydh=zydh,ywz=startsiteid,zrwz=endsiteid).filter(lsh__in=OrderBBNo.objects.filter(lsh__lte=enddatetimestr)):
            projectdict[okey]['zcnum'] += obb.zrwznum
            projectdict[okey]['ysnum'] += obb.ysnum
            projectdict[okey]['bfnum'] += obb.bfnum
        if 0 != projectdict[okey]['zrnum'] == projectdict[okey]['zcnum'] + projectdict[okey]['ysnum'] + \
                projectdict[okey]['bfnum']:
            datamap[projectdict[okey]['finishdate']]['bzxiangsj'] += 1

    for orderlistid, zydh, startsiteid, endsiteid in projectdicttq.keys():
        okey = (orderlistid, zydh, startsiteid, endsiteid)
        if not projectdicttq[okey]['finishdate']:
            continue
        for obb in OrderBB.objects.filter(zrorder=orderlistid, yzydh=zydh, zrwz=startsiteid).filter(
                lsh__in=OrderBBNo.objects.filter(lsh__lte=enddatetimestr)):
            projectdicttq[okey]['zrnum'] += obb.zrwznum
        for obb in OrderBB.objects.filter(yorder=orderlistid,yzydh=zydh,ywz=startsiteid,zrwz=endsiteid).filter(lsh__in=OrderBBNo.objects.filter(lsh__lte=enddatetimestr)):
            projectdicttq[okey]['zcnum'] += obb.zrwznum
            projectdicttq[okey]['ysnum'] += obb.ysnum
            projectdicttq[okey]['bfnum'] += obb.bfnum
        if 0 != projectdicttq[okey]['zrnum'] == projectdicttq[okey]['zcnum'] + projectdicttq[okey]['ysnum'] + \
                projectdicttq[okey]['bfnum']:
            datamap[projectdicttq[okey]['finishdate']]['tqxiangsj'] += 1

    for orderlistid, zydh, startsiteid, endsiteid in projectdictqq.keys():
        okey = (orderlistid, zydh, startsiteid, endsiteid)
        if not projectdictqq[okey]['finishdate']:
            continue
        for obb in OrderBB.objects.filter(zrorder=orderlistid, yzydh=zydh, zrwz=startsiteid).filter(
                lsh__in=OrderBBNo.objects.filter(lsh__lte=enddatetimestr)):
            projectdictqq[okey]['zrnum'] += obb.zrwznum
        for obb in OrderBB.objects.filter(yorder=orderlistid,yzydh=zydh,ywz=startsiteid,zrwz=endsiteid).filter(lsh__in=OrderBBNo.objects.filter(lsh__lte=enddatetimestr)):
            projectdictqq[okey]['zcnum'] += obb.zrwznum
            projectdictqq[okey]['ysnum'] += obb.ysnum
            projectdictqq[okey]['bfnum'] += obb.bfnum
        if 0 != projectdictqq[okey]['zrnum'] == projectdictqq[okey]['zcnum'] + projectdictqq[okey]['ysnum'] + \
                projectdictqq[okey]['bfnum']:
            datamap[projectdictqq[okey]['finishdate']]['qqxiangsj'] += 1

    for v in datamap.values():
        if v['bzjianjh'] > 0:
            v['jianri'] = '%.2f' % (float(v['bzjiansj']) / v['bzjianjh'] * 100,)
        if v['bzxiangjh'] > 0:
            v['xiangri'] = '%.2f' % (float(v['bzxiangsj'] )/ v['bzxiangjh'] * 100,)

    rl = []
    kl = list(datamap.keys())
    kl.sort()
    for k in kl:
        rl.append(datamap[k])

    return getResult(rl)


def queryPlanBy(request, planuser, checkuser, startdate, enddate, checkstartdate, checkenddate, status=None):
    '''
    status 0:全部 1:未通过 2:通过
    '''
    query = PlanNo.objects.all()
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
        query = query.filter(status__in=('1', '3'))
    elif status == 2:
        query = query.filter(status='2')

    query = query.order_by('-updateTime')

    resultlist = []
    for plan in query:
        r = {'id': plan.pk, 'lsh': plan.lsh, 'shenhe': getattr(getattr(plan, "shenhe", {}), "last_name", ""),
             'bianzhi': getattr(getattr(plan, "bianzhi", {}), "last_name", ""),
             'updateTime': plan.updateTime.strftime('%Y/%m/%d'), 'status': plan.status}
        r['lastcheckTime'] = ''
        if plan.lastcheckTime:
            r['lastcheckTime'] = plan.lastcheckTime.strftime('%Y/%m/%d')
        resultlist.append(r)
    return getResult(resultlist)


@login_required
def queryPlanByUser(request, status=1):
    return queryPlanBy(request, request.user, None, None, None, None, None, status)


@login_required
@permission_required('ztmanage.plan_all')
def queryPlan(request, planuser, checkuser, startdate, enddate, checkstartdate, checkenddate):
    return queryPlanBy(request, planuser, checkuser, startdate, enddate, checkstartdate, checkenddate)


@login_required
@permission_required('ztmanage.plan_changerecord')
def changerecordPlan(request):
    l=[]
    for p in PlanChangeLog.objects.all().order_by('-date'):
        l.append({'id':p.pk,'date':p.date.strftime('%Y/%m/%d'),'count':p.count,'user':p.user.last_name})
    return getResult(l)


@login_required
@permission_required('ztmanage.plan_changerecord')
@transaction.commit_on_success
def changerecordPlanDelete(request):
    PlanChangeLog.objects.all().delete()
    return getResult(True,True,u'已删除所有主计划退审记录')


@login_required
def getOrderEndDate(request, ddbhid):
    ddbh = OrderNo.objects.get(pk=ddbhid)
    lsh = ''
    for b in OrderBB.objects.filter(yorder__in=OrderList.objects.filter(ddbh=ddbh)).order_by('-id')[:1]:
        lsh = b.lsh.lsh

    if lsh:
        return getResult({'ddbhid': ddbhid, 'date': datetime.datetime.strptime(lsh.split('-')[0], '%Y%m%d')})
    else:
        return getResult({'ddbhid': ddbhid, 'date': datetime.datetime.now()})


@login_required
@permission_required('ztmanage.orderruning')
def getOrderRuningList(request, start, end, ddbh=None):
    orderlistquery = OrderList.objects.all()
    if start and end:
        orderlistquery = orderlistquery.filter(createDate__gte=datetime.datetime.strptime(start, '%Y%m%d')).filter(
            createDate__lte=datetime.datetime.strptime(end, '%Y%m%d') + datetime.timedelta(hours=24))
    if isinstance(ddbh, int):
        orderlistquery = orderlistquery.filter(ddbh=ddbh)
    if isinstance(ddbh, str) or isinstance(ddbh, unicode):
        orderlistquery = orderlistquery.filter(ddbh__in=OrderNo.objects.filter(ddbh__istartswith=ddbh))
    orderbhids = set()
    for ol in orderlistquery:
        orderbhids.add(ol.ddbh_id)
    orderdict = {}
    for o in OrderNo.objects.filter(pk__in=orderbhids):
        orderdict[str(o.pk)] = {'id': o.pk, 'ddbh': o.ddbh, 'xddate': None, 'lr': '', 'orderlistnum': 0,
                                'productnum': 0, 'closeorderlistnum': 0, 'openorderlistnum': 0, 'closeflag': 0}
    for ol in OrderList.objects.filter(ddbh__in=orderbhids).order_by('createDate'):
        orderdict[str(ol.ddbh_id)]['xddate'] = ol.createDate.strftime('%Y/%m/%d')
        orderdict[str(ol.ddbh_id)]['orderlistnum'] += 1
        orderdict[str(ol.ddbh_id)]['productnum'] += ol.num
        if ol.is_open:
            orderdict[str(ol.ddbh_id)]['openorderlistnum'] += 1
        else:
            orderdict[str(ol.ddbh_id)]['closeorderlistnum'] += 1
            #delkeys =[]
    for v in orderdict.values():
        #if isclose == 'open':
        #    if v['openorderlistnum'] ==0:
        #        delkeys.append(str(v['id']))
        #elif isclose == 'close':
        #    if v['openorderlistnum']!=0:
        #        delkeys.append(str(v['id']))
        if v['openorderlistnum'] == 0:
            v['closeflag'] = 1
            #for k in delkeys:
        #    del orderdict[k]
    l = list(orderbhids)
    l.sort()
    resultlist = []
    for k in l:
        if orderdict.has_key(str(k)):
            resultlist.append(orderdict[str(k)])
    return getResult(resultlist)


def getZYDHByOrderList(request, orderlistids):
    '''
    根据订单，查询出 使用过的 作业单号
    '''
    zybhlist = []
    if isinstance(orderlistids, int):
        query = Zydh.objects.filter(orderlist=orderlistids)
    elif len(orderlistids) > 0:
        query = Zydh.objects.filter(orderlist__in=orderlistids)
    else:
        return getResult({'orderlist%s' % orderlistids: zybhlist})
    datadict = {}

    for zydh in query:
        if not datadict.has_key('orderlist%s' % zydh.orderlist_id):
            datadict['orderlist%s' % zydh.orderlist_id] = []

        datadict['orderlist%s' % zydh.orderlist_id].append({'txt': zydh.zydh})

    return getResult(datadict)


def getZYDHByCode(request, codeListids):
    '''
    根据订单，查询出 使用过的 作业单号
    '''
    zydhdict = {}
    for zydh in Zydh.objects.filter(orderlist__in=OrderList.objects.filter(code__in=codeListids)):
        k = 'orderlist%s' % zydh.orderlist_id
        if not zydhdict.has_key(k):
            zydhdict[k] = set()
        if zydh.zydh not in zydhdict[k]:
            zydhdict[k].add(zydh.zydh)
    return getResult(zydhdict)


@transaction.commit_on_success
def initZYDH(request):
    zybhset = set()
    for zydh in Zydh.objects.all():
        zybhset.add((zydh.orderlist_id, zydh.zydh))
    zybhlist = []
    for bb in OrderBB.objects.all():
        if (bb.yorder_id, bb.yzydh.strip().upper()) not in zybhset:
            zybhset.add((bb.yorder_id, bb.yzydh.strip().upper()))
            zybhlist.append((bb.yorder_id, bb.yzydh.strip().upper()))
    for oid, zy in zybhlist:
        try:
            zydh = Zydh()
            zydh.orderlist_id = oid
            zydh.zydh = zy
            zydh.save()
        except Exception, e:
            print e

    url = 'http://' + request.META['HTTP_HOST'] + '/static/swf/'
    return render_to_response('zt/index.html', {'url': url, 'p': datetime.datetime.now()})







