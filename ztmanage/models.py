#coding=utf-8
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Ztperm(models.Model):
    #
    perm={}
    class Meta:

        permissions=(
            ('user_add',u'日报表录人'),
            ('user_update',u'日报表修改'),
            ('user_view',u'查询人员'),
            ('user_change',u'维护人员'),
        )
    for code,codename in Meta.permissions:
        perm['ztmanage.'+code]=codename
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
    isaction=models.BooleanField(default=True,verbose_name='启用',null=True,blank=True)
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
    is_open=models.BooleanField(default=True,verbose_name='订单开关',help_text='订单是否关闭')

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
    lsh=models.CharField(max_length=40,verbose_name='日报表流水号',help_text='日报表流水号')
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
    yzydh=models.CharField(max_length=40,verbose_name='源作业单编号',help_text='源订单编号')
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
    date=models.CharField(max_length=20,verbose_name='日期',help_text='日期')
#    ddbh=models.ForeignKey(OrderNo,related_name='genzongddbh',verbose_name='源订单编号',help_text='源订单编号')
#    code=models.ForeignKey(Code,verbose_name='产品编号')
    order=models.ForeignKey(OrderList,related_name='ddgz',verbose_name='订单编号')
    
    wz=models.ForeignKey(ProductSite,related_name='genzongywz',null=True,blank=True,verbose_name='位置')
    ywznum=models.IntegerField(default=0,verbose_name='流入数量')
    zcnum=models.IntegerField(default=0,verbose_name='转出数量')
    bfnum=models.IntegerField(default=0,verbose_name='报废数量')
    ysnum=models.IntegerField(default=0,verbose_name='遗失数量')
    is_last=models.BooleanField(default=False,verbose_name='是否最后一次计算')

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