#coding=utf-8
from django.db import models
from django.contrib.auth.models import User, Permission

# Create your models here.

class Ztperm(models.Model):
    #
    perm={}
    class Meta:

        permissions=(
            ('user_add',u'日报表录人'),
            ('user_update',u'日报表修改'),
            ('user_view',u'日报表查询'),

            ('user_manager',u'人员管理'),
            ('scx_manager',u'生产线管理'),
            ('code_manager',u'物料管理'),
            ('site_manager',u'位置管理'),
            ('order_manager',u'订单管理'),


            ('plan_update',u'主计划编制'),
            ('plan_check',u'主计划审核'),
            ('plan_uncheck',u'主计划退审'),
            ('plan_all',u'主计划汇总'),
            ('plan_query',u'主计划查询'),
            ('plan_detail_close',u'主计划强制关闭'),
            ('plan_changerecord',u'主计划修改记录'),
            ('plan_daily',u'生产情况日报表'),

            ('order_zhuizong',u'订单追踪'),
            ('orderruning',u'订单执行情况汇总表'),

        )
    for code,codename in Meta.permissions:
        perm['ztmanage.'+code]=codename
    # for p in Permission.objects.all():
    #     perm['%s.%s'%(p.content_type.app_label,p.codename)]=p.codename
class Scx(models.Model):
    name=models.CharField(max_length=40,verbose_name='名称',unique=True,help_text='生产线名称')
#    name=models.CharField(max_length=40,verbose_name='名称',help_text='产品名称')
#    gg=models.CharField(max_length=100,verbose_name='规格',help_text='产品规格')

    class Admin():
        pass
    class Meta():
        verbose_name='生产线'
#        verbose_name_plural='项目组'
    def __unicode__(self):
        return self.name

    
class Code(models.Model):
    scx=models.ForeignKey(Scx,verbose_name='生产线',help_text='生产线')
    code=models.CharField(max_length=40,verbose_name='代码',unique=True,help_text='产品代码')
    name=models.CharField(max_length=40,verbose_name='名称',help_text='产品名称')
    gg=models.CharField(max_length=100,verbose_name='规格',help_text='产品规格')
    dj=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='单价',help_text='单价')
    ismain=models.NullBooleanField(default=True,verbose_name='主配件',null=True,blank=True)

    class Admin():
        pass
    class Meta():
        verbose_name='产品代码'
#        verbose_name_plural='项目组'
    def __unicode__(self):
        return self.code



class ProductSite(models.Model):
    TYPE=(
        ('1','前序'),
        ('2','后序'),
        ('3','扫描出库'),
    )
    name=models.CharField(max_length=40,verbose_name='名称',unique=True,help_text='生产线名称')
    type=models.CharField(max_length=10,choices=TYPE,verbose_name='流程类型',help_text='流程类型')
    isaction=models.NullBooleanField(default=True,verbose_name='启用',null=True,blank=True)
    index=models.IntegerField(verbose_name='排序',null=True,blank=True)
#    name=models.CharField(max_length=40,verbose_name='名称',help_text='产品名称')
#    gg=models.CharField(max_length=100,verbose_name='规格',help_text='产品规格')

    class Admin():
        pass
    class Meta():
        verbose_name='产品位置'
        ordering=['index','id']
#        verbose_name_plural='项目组'
    def __unicode__(self):
        return self.name
class OrderNo(models.Model):
    ddbh=models.CharField(max_length=40,unique=True,verbose_name='订单编号',help_text='源订单编号')
    bzname=models.CharField(max_length=200,verbose_name='订单描述',help_text='订单描述')

    class Admin():
        pass
    class Meta():
        verbose_name='订单编号'
#        verbose_name_plural='项目组'
    def __unicode__(self):
        return self.ddbh
class OrderList(models.Model):
    ddbh=models.ForeignKey(OrderNo,verbose_name='订单编号',help_text='源订单编号')
    code=models.ForeignKey(Code,verbose_name='产品编号')
    num=models.IntegerField(verbose_name='数量',help_text='订单数量')
    dj=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='单价',help_text='单价')
    cz=models.DecimalField(max_digits=14,decimal_places=2,verbose_name='产值',help_text='产值')
    createDate=models.DateTimeField(auto_now_add=True)
    closeDate=models.CharField(max_length=20,blank=True,null=True,verbose_name='订单关闭日期')
    is_open=models.BooleanField(default=True,db_index=True,verbose_name='订单开关',help_text='订单是否关闭')

    #    name=models.CharField(max_length=40,verbose_name='名称',help_text='产品名称')
#    gg=models.CharField(max_length=100,verbose_name='规格',help_text='产品规格')

    class Admin():
        pass
    class Meta():
        verbose_name='订单明细'
        unique_together = (('ddbh', 'code'),)
#        verbose_name_plural='项目组'
    def __unicode__(self):
        return self.ddbh

class OrderBBNo(models.Model):
    lsh=models.CharField(max_length=40,db_index=True,verbose_name='日报表流水号',help_text='日报表流水号')
    user=models.ForeignKey(User,verbose_name='录入员',help_text='录入人员')

    class Admin():
        pass
    class Meta():
        verbose_name='日报表流水号'
#        verbose_name_plural='项目组'
    def __unicode__(self):
        return self.lsh


class OrderBBLock(models.Model):
    date=models.CharField(max_length=20,verbose_name='日期',help_text='日期')
    is_lock=models.BooleanField(default=True,verbose_name='是否锁定',help_text='是否锁定')

    class Admin():
        pass
    class Meta():
        verbose_name='日报表锁'
#订单追踪锁定

class OrderBB(models.Model):
    lsh=models.ForeignKey(OrderBBNo,verbose_name='日报表流水号',help_text='日报表流水号')
#    ddbh=models.ForeignKey(OrderNo,related_name='bbddbh',verbose_name='源订单编号',help_text='源订单编号')
    yorder=models.ForeignKey(OrderList,related_name='yuanorder',verbose_name='源订单')
    yzydh=models.CharField(max_length=40,db_index=True,verbose_name='源作业单编号',help_text='源订单编号')
    ywz=models.ForeignKey(ProductSite,related_name='ywz',null=True,blank=True,verbose_name='源位置')
    ywznum=models.IntegerField(null=True,blank=True,verbose_name='源位置流出数量')
    zrorder=models.ForeignKey(OrderList,related_name='zrorder',verbose_name='转入订单编号')
#    zrddbh=models.ForeignKey(OrderNo,related_name='zrddbh',verbose_name='转入订单编号',help_text='转入订单编号')
    zrwz=models.ForeignKey(ProductSite,related_name='zrwz',null=True,blank=True,verbose_name='转入位置')
    zrwznum=models.IntegerField(default=0,verbose_name='转入数量')
    bfnum=models.IntegerField(default=0,verbose_name='报废数量',help_text='报废数量')
    ysnum=models.IntegerField(default=0,verbose_name='遗失数量',help_text='遗失数量')
    ywzsynum=models.IntegerField(default=0,verbose_name='源位置剩余数量',help_text='源位置剩余数量')
    bztext=models.CharField(max_length=50,verbose_name='备注',help_text='备注')
#    createDate=models.DateTimeField(verbose_name='订单日期',help_text='订单日期')
    #    name=models.CharField(max_length=40,verbose_name='名称',help_text='产品名称')
#    gg=models.CharField(max_length=100,verbose_name='规格',help_text='产品规格')

    class Admin():
        pass
    class Meta():
        verbose_name='订单日报表'
#        verbose_name_plural='项目组'
    def __unicode__(self):
        return '%s--%s'%(self.ddbh,self.code.code)

class OrderGenZong(models.Model):
    date=models.CharField(max_length=20,db_index=True,verbose_name='日期',help_text='日期')
#    ddbh=models.ForeignKey(OrderNo,related_name='genzongddbh',verbose_name='源订单编号',help_text='源订单编号')
#    code=models.ForeignKey(Code,verbose_name='产品编号')
    order=models.ForeignKey(OrderList,related_name='ddgz',verbose_name='订单编号')
    
    wz=models.ForeignKey(ProductSite,related_name='genzongywz',null=True,blank=True,verbose_name='位置')
    ywznum=models.IntegerField(default=0,verbose_name='流入数量')
    zcnum=models.IntegerField(default=0,verbose_name='转出数量')
    bfnum=models.IntegerField(default=0,verbose_name='报废数量')
    ysnum=models.IntegerField(default=0,verbose_name='遗失数量')
    is_last=models.BooleanField(default=False,db_index=True,verbose_name='是否最后一次计算')

    class Admin():
        pass

    class Meta():
        verbose_name='日报表订单跟踪'
        unique_together=[('date','order','wz')]


#class AutoComplete(models.Model):
#    date=models.CharField(max_length=20,verbose_name='日期',help_text='日期')
#    data=models.TextField(verbose_name='缓存数据',help_text='缓存数据')
#    data=models.Blo
#    is_open=models.BooleanField(default=True)
#
#    class Admin():
#        pass
#    class Meta():
#        verbose_name='订单追踪缓存'
#        unique_together = (('date', 'is_open'),)
##        verbose_name_plural='项目组'
#    def __unicode__(self):
#        return '%s--%s'%(self.date,self.is_open)

class PlanNo(models.Model):
    TYPE=(
        ('1','未审核'),
        ('2','审核'),
        ('3','退审'),

    )

    lsh = models.CharField(max_length=20,unique=True,verbose_name=u'主计划流水号',help_text=u'主计划流水号')
    updateTime = models.DateField(db_index=True,verbose_name=u'编制日期',help_text=u'每修改一次，改变一次')
    firstcheckTime = models.DateField(auto_now=True,blank=True,null=True,db_index=True,verbose_name=u'第一次审核日期',help_text=u'第一次审核')
    lastcheckTime = models.DateField(auto_now=True,blank=True,null=True,db_index=True,verbose_name=u'最后一次审核日期',help_text=u'最后一次审核')
    bianzhi = models.ForeignKey(User,related_name='bianzhi',db_index=True,verbose_name=u'编制人',help_text=u'编制计划的用户')
    shenhe = models.ForeignKey(User,related_name='shenhe',blank=True,null=True,db_index=True,verbose_name=u'审核人',help_text=u'审核计划的用户')
    status = models.CharField(choices=TYPE,max_length=5,db_index=True,verbose_name=u'状态',help_text=u'主计划的状态')
    isdel = models.BooleanField(default=False,db_index=True,verbose_name=u'是否删除',help_text=u'是否废弃')


class PlanRecord(models.Model):
    TYPE=(
        (0,'非常紧急'),
        (1,'一般紧急'),
        (2,'标准生产'),
        (3,'库备'),

    )

    planno = models.ForeignKey(PlanNo,verbose_name=u'流水号',help_text=u'主计划流水号')
    orderlist=models.ForeignKey(OrderList,related_name='orderlist',verbose_name=u'订单项',help_text=u'订单中的一个物料')
    zydh = models.CharField(max_length=100,blank=True,null=True,db_index=True,verbose_name=u'作业单号',help_text=u'作业单号可以为空，新投的物料是没有作业单号的，需要在物料投产后再补充')
    plannum= models.IntegerField(verbose_name=u'计划数量',help_text=u'计划投入数量')

    planbz = models.TextField(verbose_name=u'订单要求说明')
    ordergongyi = models.TextField(verbose_name=u'订单要求工艺')
    level = models.IntegerField(choices=TYPE,verbose_name=u'紧急程度',help_text=u'计划的紧急程度')
    isdel = models.BooleanField(default=False,db_index=True,verbose_name=u'是否删除',help_text=u'是否废弃')
    oldData = models.TextField(blank=True,null=True,verbose_name=u'退审时修改前的数据',help_text=u'用来在审核时，和修改的数据做比较，将其他数据用json方式保存')



class PlanDetail(models.Model):
    planrecord = models.ForeignKey(PlanRecord,verbose_name=u'主计划',help_text=u'主计划的条目')
    startdate=models.DateField(db_index=True,verbose_name=u'计划投入日期',help_text=u'物料计划投入生产的日期')
    enddate=models.DateField(db_index=True,blank=True,null=True,verbose_name=u'计划完成日期',help_text=u'物料计划完成生产的日期,为空则是永久停留')
    startsite = models.ForeignKey(ProductSite,db_index=True,related_name='startsite',verbose_name=u'起始作业区',help_text=u'生产的作业区')
    endsite = models.ForeignKey(ProductSite,db_index=True,blank=True,null=True,related_name='endsite',verbose_name=u'去向作业区',help_text=u'去向位置')
    isdel = models.BooleanField(default=False,db_index=True,verbose_name=u'是否删除',help_text=u'是否废弃')
    oldData = models.TextField(blank=True,null=True,verbose_name=u'退审时修改前的数据',help_text=u'用来在审核时，和修改的数据做比较，将其他数据用json方式保存')
    isclose=models.NullBooleanField(default=False,verbose_name=u'强制关闭',null=True,blank=True)



class PlanChangeLog(models.Model):
    user = models.ForeignKey(User,verbose_name=u'操作人',unique_for_date='date')
    date = models.DateField(auto_now=True,verbose_name=u'发生日期')
    count = models.IntegerField(default=0,verbose_name=u'退审次数',help_text=u'每一条planrecord算一条，一日内多次修改算一天的。')

class Zydh(models.Model):
    orderlist=models.ForeignKey(OrderList,db_index=True,verbose_name=u'订单项')
    zydh = models.CharField(max_length=40,verbose_name=u'作业单号')
    # planrecord = models.ForeignKey(PlanRecord,null=True,blank=True,verbose_name=u'创建作业单号的计划')

    class Meta():
        unique_together=[('orderlist','zydh')]


