#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction

__author__ = u'王健'
'''
('plan_update',u'主计划编制'),
('plan_check',u'主计划审核'),
('plan_uncheck',u'主计划退审'),
('plan_all',u'主计划汇总'),
('plan_query',u'主计划查询'),
('plan_changerecord',u'主计划修改记录'),
'''

@login_required
@permission_required('ztmanage.plan_update')
@transaction.commit_on_success
def updatePlan(request,obj):
    '''
    编制保存主计划，没有经过审核的主计划可以任意修改。
    审核状态的主计划，不可以修改，
    '''
    pass


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
def queryPlan(request,obj):
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




