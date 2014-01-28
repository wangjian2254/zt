#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import json

from tools import PLANSTATUS, permission_required, str2date2, date2str, getResult
from view_models import PlanDetailView
from models import OrderBB, PlanDetail
from django.core.cache import cache

__author__ = u'王健'


@permission_required('ztmanage.plan_query')
def queryPlanDetail2(request, obj):
    query = PlanDetailView.objects.filter(status='2')
        # planrecord__in=PlanRecord.objects.filter(planno__in=PlanNo.objects.filter(status='2')))
    if getattr(obj, 'trstart', '') and getattr(obj, 'trend', ''):
        query = query.filter(startdate__gte=str2date2(getattr(obj, 'trstart')),
                             startdate__lte=str2date2(getattr(obj, 'trend')))
    if getattr(obj, 'wcstart', '') and getattr(obj, 'wcend', ''):
        query = query.filter(enddate__gte=str2date2(getattr(obj, 'wcstart')),
                             enddate__lte=str2date2(getattr(obj, 'wcend')))
    if getattr(obj, 'site', ''):
        query = query.filter(startsite_id=getattr(obj, 'site'))
    if getattr(obj, 'zydh', ''):
        query = query.filter(zydh=getattr(obj, 'zydh'))
    if getattr(obj, 'planid', ''):
        query = query.filter(planno_id=getattr(obj, 'planid'))
            # planrecord__in=PlanRecord.objects.filter(planno=PlanNo.objects.get()))
    if getattr(obj, 'orderbhid', ''):
        query = query.filter(ddbh_id=getattr(obj, 'orderbhid'))
            # planrecord__in=PlanRecord.objects.filter(
            # orderlist__in=OrderList.objects.filter())))
    if getattr(obj, 'codeid', ''):
        query = query.filter(code_id=getattr(obj, 'codeid'))
            # planrecord__in=PlanRecord.objects.filter(
            # orderlist__in=OrderList.objects.filter(code=getattr(obj, 'codeid'))))
    foreverl = []
    l = []
    cachel = []
    for pd in query:
        if pd.finishData :
            cachel.append(json.loads(pd.finishData))
            continue
        r = {'id': pd.pk, 'planfinish': u'未投', 'planfinish_i': 0, 'orderlistid': pd.orderlist_id, 'code': pd.code_id,
             'codestr': pd.code, 'codename': pd.codename, 'codegg': pd.gg, 'scx': pd.scx_id, 'scxstr': pd.scxname,
             'qxddbh': pd.qxddbh, 'qxddbh_id': pd.qxddbh_id, 'ddbh': pd.ddbh, 'ddbh_id': pd.ddbh_id,
             'isclose': pd.isclose, 'isonline': pd.isonline, 'finishstartdate': '', 'finishstartnum': 0,
             'finishenddate': '', 'finishendnum': 0, 'bfnum': 0, 'ysnum': 0, 'startsite': pd.startname,
             'startsite_id': pd.startsite_id}
        if pd.endsite_id:
            r['endsite'] = pd.endname
            r['endsite_id'] = pd.endsite_id
        else:
            r['endsite'] = ''
            r['endsite_id'] = ''
            foreverl.append(r)

        r['zydh'] = pd.zydh
        r['level'] = PLANSTATUS[pd.level]
        r['plannum'] = pd.plannum
        r['startdate'] = date2str(pd.startdate)
        r['enddate'] = date2str(pd.enddate)
        r['planlsh'] = pd.lsh
        r['ordergongyi'] = pd.ordergongyi
        r['planbz'] = pd.planbz

        l.append(r)
        # for r in l:
    #     r.update(queryPlanDetailComputer(r.get('id'),r.get('zydh'),r.get('orderlistid'),r.get('startsite_id'),r.get('endsite_id',None)))
    lm = {}
    lsm={}
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
        lm['z%(zydh)so%(orderlistid)ss%(startsite_id)sq%(qxddbh_id)se%(endsite_id)s' % r] = r
        if not lsm.has_key('z%(zydh)so%(orderlistid)ss%(startsite_id)s' % r):
            lsm['z%(zydh)so%(orderlistid)ss%(startsite_id)s' % r]=set()
        lsm['z%(zydh)so%(orderlistid)ss%(startsite_id)s' % r].add(r)
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
        k = (obb.yzydh, obb.zrorder_id, obb.zrwz_id)
        if lsm.has_key('z%so%ss%s' % k):
            for rdict in lsm['z%so%ss%s' % k]:
                rdict['finishstartnum']+= obb.zrwznum
            #lsm['z%so%ss%s' % k]['finishstartnum'] += obb.zrwznum
            if not rdict['finishstartdate'] or rdict['finishstartdate'] < obb.lsh.lsh.split('-')[0]:
                rdict['finishstartdate'] = obb.lsh.lsh.split('-')[0]


    for obb in OrderBB.objects.filter(yorder__in=hasendzrorderlist, yzydh__in=hasendzydhlist,
                                ywz__in=hasendstartsitelist, zrwz__in=hasendendsitelist):
        ks = 'z%so%ss%sq%se%s'
        k = (obb.yzydh, obb.yorder_id, obb.ywz_id, obb.zrorder_id, obb.zrwz_id)
        if lm.has_key(ks%k):
            lm[ks%k]['finishendnum'] += obb.zrwznum
            lm[ks%k]['bfnum'] += obb.bfnum
            lm[ks%k]['ysnum'] += obb.ysnum
            if not lm[ks%k]['finishenddate'] or  lm[ks%k]['finishenddate'] <  obb.lsh.lsh.split('-')[0]:
                lm[ks%k]['finishenddate'] =  obb.lsh.lsh.split('-')[0]
    for r in l:
        if r in foreverl:
            for obb in OrderBB.objects.filter(yorder=r.get('orderlistid',0), yzydh=r.get('zydh',''), ywz=r.get('startsite_id',0)):
                r['finishendnum']+=obb.zrwznum
                r['bfnum']+=obb.bfnum
                r['ysnum']+=obb.ysnum
                if not r['finishenddate'] or  r['finishenddate'] <  obb.lsh.lsh.split('-')[0]:
                    r['finishenddate'] =  obb.lsh.lsh.split('-')[0]
        if r['finishstartnum'] == 0:
            r['planfinish'] = u'未投'
            r['planfinish_i'] = 1
        elif r['finishstartnum'] == r['finishendnum'] + r['bfnum'] + r['ysnum'] or r['plannum'] == r['finishendnum'] + r['bfnum'] + r['ysnum']:
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
            r['finishenddate'] = str2date2(PlanDetail.objects.get(pk = r['id']))
        if r['isonline']==True:
            if r['plannum'] == r['finishendnum'] :
                r['planfinish'] = u'完成'
                r['planfinish_i'] = 2
            else:
                r['planfinish'] = u'在线'
                r['planfinish_i'] = 3
        if r['planfinish_i'] == 2 :
            PlanDetail.objects.filter(pk = r.get('id',0)).filter(finishData=None).update(finishdate=str2date2(r['finishenddate']),finishData=json.dumps(r))
        else:
            PlanDetail.objects.filter(pk = r.get('id',0)).filter(finishData=None).update(finishData=json.dumps(r))
    l.extend(cachel)
    return getResult(l)
