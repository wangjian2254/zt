#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from models import *
__author__ = u'王健'

class PlanDetailView(models.Model):
    '''
    sql:

    CREATE
        /*[ALGORITHM = {UNDEFINED | MERGE | TEMPTABLE}]
        [DEFINER = { user | CURRENT_USER }]
        [SQL SECURITY { DEFINER | INVOKER }]*/
        VIEW `zt2`.`ztmanage_view_plandetail`
        AS
        (SELECT
        ztmanage_plandetail.id
        , ztmanage_plandetail.planrecord_id
        , ztmanage_plandetail.startdate
        , ztmanage_plandetail.enddate
        , ztmanage_plandetail.startsite_id
        , ztmanage_plandetail.endsite_id
        , ztmanage_plandetail.isdel
        , ztmanage_plandetail.isclose
        , ztmanage_plandetail.isonline
        , ztmanage_planrecord.planno_id
        , ztmanage_planrecord.orderlist_id
        , ztmanage_planrecord.zydh
        , ztmanage_planrecord.plannum
        , ztmanage_planrecord.planbz
        , ztmanage_planrecord.ordergongyi
        , ztmanage_planrecord.level
        , ztmanage_planno.lsh
        , ztmanage_planno.updateTime
        , ztmanage_planno.firstcheckTime
        , ztmanage_planno.lastcheckTime
        , ztmanage_planno.bianzhi_id
        , ztmanage_planno.shenhe_id
        , ztmanage_planno.status
        , ztmanage_orderlist.ddbh_id
        , ztmanage_orderlist.code_id
        , ztmanage_orderlist.num
        , ztmanage_orderlist.cz
        , ztmanage_orderlist.createDate
        , ztmanage_orderlist.closeDate
        , ztmanage_orderlist.is_open
        , ztmanage_code.scx_id
        , ztmanage_code.code
        , ztmanage_code.name as codename
        , ztmanage_code.gg
        , ztmanage_code.ismain
        , ztmanage_scx.name as scxname
        , ztmanage_orderno.ddbh

    FROM
        zt2.ztmanage_plandetail
        INNER JOIN zt2.ztmanage_planrecord
            ON (ztmanage_plandetail.planrecord_id = ztmanage_planrecord.id)

        INNER JOIN zt2.ztmanage_planno
            ON (ztmanage_planrecord.planno_id = ztmanage_planno.id)
        INNER JOIN zt2.ztmanage_orderlist
            ON (ztmanage_planrecord.orderlist_id = ztmanage_orderlist.id)
        INNER JOIN zt2.ztmanage_code
            ON (ztmanage_orderlist.code_id = ztmanage_code.id)
        INNER JOIN zt2.ztmanage_orderno
            ON (ztmanage_orderlist.ddbh_id = ztmanage_orderno.id)
        INNER JOIN zt2.ztmanage_scx
            ON (ztmanage_code.scx_id = ztmanage_scx.id));
    '''

    planno_id=models.IntegerField(verbose_name='主计划id')
    lsh = models.CharField(max_length=20,unique=True,verbose_name=u'主计划流水号',help_text=u'主计划流水号')
    updateTime = models.DateField(db_index=True,verbose_name=u'编制日期',help_text=u'每修改一次，改变一次')
    firstcheckTime = models.DateField(auto_now=True,blank=True,null=True,db_index=True,verbose_name=u'第一次审核日期',help_text=u'第一次审核')
    lastcheckTime = models.DateField(auto_now=True,blank=True,null=True,db_index=True,verbose_name=u'最后一次审核日期',help_text=u'最后一次审核')
    bianzhi = models.ForeignKey(User,related_name='bianzhi',db_index=True,verbose_name=u'编制人',help_text=u'编制计划的用户')
    shenhe = models.ForeignKey(User,related_name='shenhe',blank=True,null=True,db_index=True,verbose_name=u'审核人',help_text=u'审核计划的用户')
    status = models.CharField(choices=PlanNo.TYPE,max_length=5,db_index=True,verbose_name=u'状态',help_text=u'主计划的状态')

    orderlist=models.ForeignKey(OrderList,related_name='orderlist',verbose_name=u'订单项',help_text=u'订单中的一个物料')
    zydh = models.CharField(max_length=100,blank=True,null=True,db_index=True,verbose_name=u'作业单号',help_text=u'作业单号可以为空，新投的物料是没有作业单号的，需要在物料投产后再补充')
    plannum= models.IntegerField(verbose_name=u'计划数量',help_text=u'计划投入数量')
    planbz = models.TextField(verbose_name=u'订单要求说明')
    ordergongyi = models.TextField(verbose_name=u'订单要求工艺')
    level = models.IntegerField(choices=PlanRecord.TYPE,verbose_name=u'紧急程度',help_text=u'计划的紧急程度')

    startdate=models.DateField(db_index=True,verbose_name=u'计划投入日期',help_text=u'物料计划投入生产的日期')
    enddate=models.DateField(db_index=True,blank=True,null=True,verbose_name=u'计划完成日期',help_text=u'物料计划完成生产的日期,为空则是永久停留')
    startsite = models.ForeignKey(ProductSite,db_index=True,related_name='startsite',verbose_name=u'起始作业区',help_text=u'生产的作业区')
    endsite = models.ForeignKey(ProductSite,db_index=True,blank=True,null=True,related_name='endsite',verbose_name=u'去向作业区',help_text=u'去向位置')
    isdel = models.BooleanField(default=False,db_index=True,verbose_name=u'是否删除',help_text=u'是否废弃')
    isclose=models.NullBooleanField(default=False,verbose_name=u'强制关闭',null=True,blank=True)
    isonline=models.NullBooleanField(default=False,verbose_name=u'重置在线',null=True,blank=True)

    ddbh_id=models.IntegerField(verbose_name='订单编号id')
    ddbh=models.CharField(max_length=40,unique=True,verbose_name='订单编号',help_text='源订单编号')
    # code=models.ForeignKey(Code,verbose_name='产品编号')
    num=models.IntegerField(verbose_name='数量',help_text='订单数量')
    cz=models.DecimalField(max_digits=14,decimal_places=2,verbose_name='产值',help_text='产值')
    createDate=models.DateTimeField(auto_now_add=True)
    closeDate=models.CharField(max_length=20,blank=True,null=True,verbose_name='订单关闭日期')
    is_open=models.BooleanField(default=True,db_index=True,verbose_name='订单开关',help_text='订单是否关闭')

    scx_id=models.IntegerField(verbose_name='生产线id')
    scxname=models.CharField(max_length=40,verbose_name='名称',unique=True,help_text='生产线名称')
    code_id=models.IntegerField(verbose_name='代码id')
    code=models.CharField(max_length=40,verbose_name='代码',unique=True,help_text='产品代码')
    codename=models.CharField(max_length=40,verbose_name='名称',help_text='产品名称')
    gg=models.CharField(max_length=100,verbose_name='规格',help_text='产品规格')
    ismain=models.NullBooleanField(default=True,verbose_name='主配件',null=True,blank=True)

    class Meta:
        db_table = 'ztmanage_view_plandetail'