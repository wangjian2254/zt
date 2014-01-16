#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Permission
from django.http import HttpResponse
from django.shortcuts import render_to_response
from zt.settings import MEDIA_ROOT
from zt.ztmanage.models import OrderBBNo, Scx, Code, ProductSite, OrderNo, OrderList, OrderBBLock, OrderBB, OrderGenZong, Zydh
from zt.ztmanage.errors import  CompluteNumError
from django.db import transaction
from zt.ztmanage.models import Ztperm
from django.core.cache import cache
from zt import xlwt
from zt.xlwt.Formatting import Font, Alignment
from zt.ztmanage.tools import getResult, newLSHNoByUser, delFile, getPickleObj, savePickle,  getCodeByList, getOrderNoByList,getOrderByOrderlistid,getCodeNameById

__author__ = u'王健'



def login_required1(login=False):
    def islogin(func):
        def test(request, *args, **kwargs):
            if request.user.is_authenticated():
                return func(request, *args, **kwargs)
            else:
                return getResult(False,False,'需要登录后才能操作。')
            return test
    return islogin


def permission_required(code):
    def permission(func):
        def test(request, *args, **kwargs):
            if request.user.has_perm(code):
                return func(request, *args, **kwargs)
            else:
                return getResult(False,False,u'权限不够,需要具有：%s 权限'%Ztperm.perm[code])
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

@login_required
def getUser(request):
    return getResult(request.user)
@login_required
def getAllUser(request):
    return getResult(User.objects.all())
    pass
@login_required
def userhaschange(request):
    if not request.user.is_superuser and request.user.has_perm('ztmanage.order_zhuizong'):
        return getResult(True)
    else:
        return getResult(False)
    pass

@login_required
@permission_required('ztmanage.user_manager')
@transaction.commit_on_success
def saveUser(request,obj):
    # raise 'sdf'
    u=User()
    if obj.has_key('id'):
        u=User.objects.get(pk=obj['id'])
#        u.pk=obj['id']
        if obj.has_key('password'):
            u.set_password(obj['password'])
#        u.is_staff=User.objects.get(pk=obj['id']).is_staff
            
    else:
        u.set_password(obj['password'])
    u.username=obj['username']
    u.last_name=obj['last_name']
    u.is_active=obj['is_active']
#    u.first_name=obj['first_name']

#    u.is_active=True
    u.save()
    u.user_permissions=set()
    for p in Permission.objects.filter(codename__in=obj['permissions']):
        u.user_permissions.add(p)
    
    u.save()

    return getResult(True)
    pass
@login_required
@transaction.commit_on_success
def changeUserPassword(request,obj):
    u=request.user
    if u.username==obj['username']:
        if u.check_password(obj['oldpassword']):
            u.set_password(obj['password'])
            u.save()
            return getResult(True)

    return getResult(False,False,u'修改密码失败')
    pass



@login_required
def getUserById(request,id):
    return getResult(User.objects.filter(pk=id)[:1])
    pass

@login_required
@permission_required('ztmanage.scx_manager')
@transaction.commit_on_success
def saveScx(request,scxlist):
    for s in scxlist:
        scx=Scx()
        if s.has_key('id'):
            scx.pk=s['id']
            cache.delete('scx'+str(s['id']))
        scx.name=s['name']
        try:
            scx.save()
        except :
            pass

    cache.delete('allscx')
    return getResult(True)
    pass

@login_required
@permission_required('ztmanage.scx_manager')
@transaction.commit_on_success
def delScx(request,scxlist):
    l=[]
    for s in scxlist:
        l.append(s['id'])
        cache.delete('scx'+str(s['id']))
    sc=Scx.objects.filter(pk__in=l).delete()

    cache.delete('allscx')
    return getResult(True)
    pass

@login_required
def getAllScx(request):
    result=cache.get('allscx')
    if result:
        return getResult(result)
    scxlist=[]
    for scx in Scx.objects.all().order_by('id'):
        scxlist.append(scx)
    result=scxlist
    cache.set('allscx',result,3600*24*10)
    return getResult(result)
    pass


@login_required
def getScxById(request,id):
    return getResult(Scx.objects.filter(pk=id)[:1])
    pass
@login_required
def getAllCode(request):
    result=cache.get('allcode')
    if result:
        return getResult(result)
    codelist=[]
    for code in Code.objects.all():
        if code.ismain==None or code.ismain:
            codelist.append({'id':code.pk,'code':code.code,'name':code.name,'scx':code.scx_id,'gg':code.gg,'dj':code.dj,'ismain':True})
        else:
            codelist.append({'id':code.pk,'code':code.code,'name':code.name,'scx':code.scx_id,'gg':code.gg,'dj':code.dj,'ismain':False})
#        codelist.append(code)
    result=codelist
    cache.set('allcode',result,3600*24*10)
    return getResult(result)
    pass
@login_required
@permission_required('ztmanage.code_manager')
@transaction.commit_on_success
def delCode(request,idlist):
    l=[]
    for s in idlist:
        l.append(s['id'])
    sc=Code.objects.filter(pk__in=l).delete()
    for i in l:
        cache.delete('code'+str(i))
    cache.delete('allcode')
    return getResult(True)
    pass
@login_required
@permission_required('ztmanage.code_manager')
@transaction.commit_on_success
def saveCode(request,obj):
    code=Code()
    if obj.has_key('id'):
        code.pk=obj['id']
    code.code=obj['code'].upper()
    code.name=obj['name']
    code.gg=obj['gg']
    if obj['ismain']==False:
        code.ismain=False
    else:
        code.ismain=True
    code.dj=float(obj['dj'])
    code.scx=Scx.objects.get(pk=obj['scx'])
    try:
        code.save()
    except :
        pass
    cache.delete('allcode')
    cache.delete('code'+str(code.pk))
    return getResult(True)
    pass
@login_required
def getCodeByCode(request,code):
    return getResult(Code.objects.filter(code=code)[:1])
    pass
@login_required
def getCodeById(request,id):
    return getResult(Code.objects.filter(pk=id)[:1])
    pass
@login_required
def getAllProductSite(request):
    result=cache.get('allsite')
    if result:
        return getResult(result)
    sitelist=[]
    for site in ProductSite.objects.all():
        sitelist.append(site)
    result=sitelist
    cache.set('allsite',result,3600*24*10)
    return getResult(result)

@login_required
def getAllOpenProductSite(request):
    sitelist=[]
    for site in ProductSite.objects.filter(isaction=True).all().order_by('index'):
        sitelist.append(site)
    result=sitelist
    return getResult(result)

@login_required
@permission_required('ztmanage.site_manager')
@transaction.commit_on_success
def saveSite(request,obj):
    s=ProductSite()
    if obj.has_key('id'):
        s.pk=obj['id']
    s.name=obj['name']
    s.type=obj['type']
    s.isaction=obj['isaction']
    s.index=obj['index']
    s.save()
    cache.delete('allsite')
    date=datetime.datetime.now().strftime("%Y%m%d")
    delFile(date,True)
    delFile(date,False)
    return getResult(True)
    pass
@login_required
@permission_required('ztmanage.site_manager')
@transaction.commit_on_success
def delSite(request,idlist):
    l=[]
    for obj in idlist:
        l.append(obj['id'])
    for p in ProductSite.objects.filter(pk__in=l):
        p.isaction=False
        p.save()
    cache.delete('allsite')
    return getResult(True)
    pass
@login_required
@permission_required('ztmanage.site_manager')
@transaction.commit_on_success
def openSite(request,idlist):
    l=[]
    for obj in idlist:
        l.append(obj['id'])
    for p in ProductSite.objects.filter(pk__in=l):
        p.isaction=True
        p.save()
    cache.delete('allsite')
    return getResult(True)
    pass
@login_required
def getProductSiteById(request):
    return getResult(ProductSite.objects.filter(pk=id)[:1])
    pass
@login_required
def getAllOrderNo(request):
    result=cache.get('allorderno')
    if result:
        return getResult(result)
    sitelist=[]
    for site in OrderNo.objects.all():
        sitelist.append(site)
    result=sitelist
    cache.set('allorderno',result,3600*24*10)
    return getResult(result)
#    return getResult(OrderNo.objects.all())
    pass
@login_required
def getOrderNoById(request,id):
    return getResult(OrderNo.objects.filter(pk=id)[:1])
    pass
@login_required
def getOrderNoByBH(request,bh):
    return getResult(OrderNo.objects.filter(ddbh=bh)[:1])
    pass
@login_required
def getOrderByBH(request,bh):
    orderno=OrderNo.objects.filter(ddbh=bh.upper())[:1]
    if len(orderno)>0:
        return getResult({'list':OrderList.objects.filter(ddbh=orderno[0].pk),'ddbh':orderno[0].ddbh,'bzname':orderno[0].bzname})
    return getResult(None)
    pass
@login_required
def getAllOrderList(request):
    return getResult(OrderList.objects.all())
    pass
@login_required
def getOrderIsOpen(request):
    result=cache.get('getOrderIsOpen')
    if result:
        return getResult(result)
    oset=set()
    orderlist=[]
    for o in OrderList.objects.filter(is_open=True).order_by('-id'):
        oset.add(o.ddbh_id)
#        orderlist.append(o)
        orderlist.append({'id':o.pk,'ddbh':o.ddbh_id,'code':o.code_id,'num':o.num,'dj':o.dj,'cz':o.cz,'createDate':o.createDate,'closeDate':o.closeDate,'is_open':o.is_open})
    ordernolist=[]
    for n in OrderNo.objects.filter(pk__in=list(oset)):
#        ordernolist.append(n)
        ordernolist.append({'id':n.pk,'ddbh':n.ddbh,'bzname':n.bzname})
    result={'orderlist':orderlist,'orderddbh':ordernolist}
    cache.set('getOrderIsOpen',result,3600*24*10)
#    ddbhmap={}
#    for ddbh in OrderNo.objects.filter(pk__in=list(oset)):
#        ddbhmap['ddbh'+str(ddbh.pk)]=ddbh.ddbh

    return getResult(result)
    pass

@login_required
@permission_required('ztmanage.order_zhuizong')
@transaction.commit_on_success
def setOrderListClose(request,orderlistid):
    try:
        date=datetime.datetime.now().strftime("%Y%m%d")
        closeorderlistid=[]
        closeorderlist=[]
        for o in OrderList.objects.filter(pk__in=orderlistid):
            o.is_open=False
            o.closeDate=date
            o.save()
            cache.delete('orderlist'+str(o.pk))
            closeorderlist.append(o)
            closeorderlistid.append(o.pk)
        closeordergenzongmap={}

        delordergenzongid=[]
        for o in OrderGenZong.objects.filter(order__in=closeorderlist).order_by('-date'):
            if closeordergenzongmap.has_key('o'+str(o.order_id)+'w'+str(o.wz_id)):
                delordergenzongid.append(o.pk)
            else:
                o.is_last=True
                closeordergenzongmap['o'+str(o.order_id)+'w'+str(o.wz_id)]=o
        OrderGenZong.objects.filter(pk__in=delordergenzongid).delete()
        for o in closeordergenzongmap.values():
            o.save()
        #opendata=None
        closedata=None

        #if hasFile(date,True):
        opendata=getPickleObj(date,True)
            #if hasFile(date,False):
        if opendata:
            closedata=getPickleObj(date,False)
        if opendata :
            closerow=[]
            for row in opendata['result']['query']:
                if row['orderlist_id'] in closeorderlistid:
                    row['closedate']=date
                    closerow.append(row)
                    if closedata:
                        closedata['result']['query'].append(row)
            for crow in closerow:
                opendata['result']['query'].remove(crow)
            savePickle(date,True,opendata)
            if closedata:
                savePickle(date,False,closedata)
        cache.delete('getOrderIsOpen')
        return getResult(closeorderlistid)
    except :
        return getResult(False,False,'关闭订单失败。')

@login_required
@permission_required('ztmanage.order_manager')
@transaction.commit_on_success
def delOrder(request,idlist):
    l=[]
    for obj in idlist:
        l.append(obj['id'])
    OrderList.objects.filter(pk__in=l).delete()
    for i in l:
        cache.delete('orderlist'+str(i))
    cache.delete('getOrderIsOpen')
    return getResult(True)
    pass
@login_required
@permission_required('ztmanage.order_manager')
@transaction.commit_on_success
def saveOrder(request,orderlist,ddbh,bhname):
    orderNo=OrderNo.objects.filter(ddbh=ddbh)[:1]
    if len(orderNo)>0:
        orderNo=orderNo[0]
    else:
        orderNo=OrderNo()
        orderNo.ddbh=ddbh.upper()
        orderNo.bzname=bhname
        orderNo.save()
        cache.delete('allorderno')

        
    for obj in orderlist:

        if getattr(obj,'id',''):
            o=OrderList.objects.get(pk=obj['id'])
        else:
            o=OrderList()
            o.code=Code.objects.get(pk=obj['code'])

        o.ddbh=orderNo
        o.num=obj['num']
        o.dj=obj['dj']
        o.cz=o.num*o.dj
        o.save()
        cache.delete('orderlist'+str(o.pk))
    cache.delete('getOrderIsOpen')
    '''
    删除缓存
    '''
    date=datetime.datetime.now().strftime("%Y%m%d")
    delFile(date,True)
    delFile(date,False)

#    ss=Order.objects.filter(pk__in=l).delete()
    return getResult(True)
    pass
@login_required
def getOrderByBHAndCode(request,bh,code):
    orderno=OrderNo.objects.filter(ddbh=bh)[:1]
    code=Code.objects.filter(code=code)[:1]

    if len(orderno)>0 and len(code)>0:
        return getResult(OrderList.objects.filter(ddbh=orderno[0].pk,code=code[0].pk))
    return getResult(None)
    pass
@login_required
def getOrderAllBBNo(request,date,is_user):
    if date:
        qs=OrderBBNo.objects.filter(lsh__startswith=date)
        if is_user:
            qs=qs.filter(user=request.user)
        return getResult(qs)
    return getResult([])
    pass
@login_required
def getOrderBBNoByUser(request,user,limit=20,page=0):
    return getResult({'orderbbnolist':OrderBBNo.objects.filter(user=user)[limit*page:limit*page+limit],'limit':limit,'page':page})
    pass
@login_required
def getOrderBBNoByDate(request,date):
    return getResult({'orderbbnolist':OrderBBNo.objects.filter(lsh__startswith=date),'date':date})
    pass
@login_required
@permission_required('ztmanage.user_view')
def getOrderBBNoByDateQJ(request,date,dateend=None,code=None,user=None):
    if code and  type(code) is not int:
        return getResult(False,False,'物料选择错误')
    query=OrderBB.objects
    if code:
        query=query.filter(yorder__in=OrderList.objects.filter(code=code))
    if dateend:
        lshlist=OrderBBNo.objects.filter(lsh__gte=date).filter(lsh__lte=dateend+'9')

    else:
        lshlist=OrderBBNo.objects.filter(lsh__gte=date)
    if user:
        lshlist=lshlist.filter(user=user)
    query=query.filter(lsh__in=lshlist)

#    query1=OrderBB.objects.all()
#    orderlist=[]
#    for ol in query1:
#        if ol.yorder==ol.zrorder and ol.ywz==ol.zrwz:
#            orderlist.append(ol.id)
#    OrderBB.objects.filter(id__in=orderlist).delete()
#    query=OrderBB.objects.filter(id__in=[9041, 9407, 9433, 9434, 9435])
#    query.delete()

    orderBBlist=[]
    for orderbb in query:
#    for orderbb in orderlist:
        yorderlistmap=getOrderByOrderlistid(orderbb.yorder_id)
        zorderlistmap=getOrderByOrderlistid(orderbb.zrorder_id)
        codemap=getCodeNameById(yorderlistmap['code'])
        orderBBlist.append({'yddbh':yorderlistmap['ddbh'],'code':codemap['code'],'codename':codemap['name'],'codegg':codemap['gg'],'scx':codemap['scx'],'yzydh':orderbb.yzydh,'ywz':(orderbb.ywz and [orderbb.ywz.name] or [''])[0],'ywznum':orderbb.ywznum,'zrwz':(orderbb.zrwz and [orderbb.zrwz.name] or [''])[0],'zrddbh':zorderlistmap['ddbh'],'zrwznum':orderbb.zrwznum,'bfnum':orderbb.bfnum,'ysnum':orderbb.ysnum,'bztext':orderbb.bztext,'lsh':orderbb.lsh.lsh,'user':orderbb.lsh.user.last_name+orderbb.lsh.user.first_name})



    return getResult(orderBBlist)
    pass
@login_required
def getNewOrderBBNoByUser(request):
    return getResult(newLSHNoByUser(request.user))

    pass


@login_required
@permission_required('ztmanage.user_add')
@orderbbdel_required('ztmanage.user_update')
def delOrderBB(request,idlist):
    try:
        with transaction.commit_on_success():
            date=datetime.datetime.now().strftime("%Y%m%d")
            l=[]
            for obj in idlist:
                l.append(obj['id'])
            if len(l)>0:
                lsh=OrderBB.objects.get(pk=l[0])

                if lsh.lsh.lsh.find(date)!=0:
                    return getResult(False,False,'只能修改当天的报表。')
            else:
                return getResult(True)
            qs=OrderBB.objects.filter(pk__in=l)
            computeOrderMonitorByLsh(lsh.lsh.lsh.split('-')[0],qs,'jian')
            qs.delete()
            delFile(date,True)
            return getResult(l)
    except CompluteNumError,e:
        order=OrderList.objects.get(pk=e.order)
        if order:
            orderbh=order.ddbh.ddbh
            codestr=order.code.code
        else:
            orderbh=''
            codestr=''
        wz=ProductSite.objects.get(pk=e.wz)
        result={'order':e.order,'wz':e.wz}
        msg='订单编号: %s 物料编号:%s 位置: %s ，剩余数量计算错误。'%(orderbh.encode('utf-8'),codestr.encode('utf-8'),wz.name.encode('utf-8'))
        return getResult(result,False,msg)
    except Exception,e:
        return getResult(False,False,'日报表保存错误，请检查数据。')

#        for k in computeOrder:
#            del settings.DDGENZONG[k]

    pass
@login_required
@permission_required('ztmanage.user_add')
@orderbbchange_required('ztmanage.user_update')#@transaction.commit_manually
def saveOrderBB(request,orderbblist,lsh=None):
    try:
        with transaction.commit_on_success():
            date=datetime.datetime.now().strftime("%Y%m%d")
            if not lsh:
                lsh=OrderBBNo()
                lsh.lsh=newLSHNoByUser(request.user)
                lsh.user=request.user
                lsh.save()
            else:
                lsh=OrderBBNo.objects.get(lsh=lsh)

                if lsh.lsh.find(date)!=0:
                    return getResult(False,False,'只能修改当天的报表。')
                computeOrderMonitorByLsh(lsh.lsh.split('-')[0],OrderBB.objects.filter(lsh=lsh),'jian')
            orderBBList=[]
            for obj in orderbblist:
                o=OrderBB()
                if obj.has_key('id'):
                    o.pk=obj['id']
                o.lsh=lsh
                o.yorder=OrderList.objects.get(pk=obj['yorder'])
                o.yzydh=obj['yzydh'].strip()
                if obj.has_key('ywz'):
                    o.ywz=ProductSite.objects.get(pk=obj['ywz'])
                    o.ywznum=obj['ywznum']
                o.zrorder=OrderList.objects.get(pk=obj['zrorder'])
                if obj.has_key('zrwz'):
                    o.zrwz=ProductSite.objects.get(pk=obj['zrwz'])
                    o.zrwznum=obj['zrwznum']
                o.bfnum=obj['bfnum']
                o.ysnum=obj['ysnum']
                o.ywzsynum=obj['ywzsynum']
                o.bztext=obj['bztext']
                o.save()
                orderBBList.append(o)
            computeOrderMonitorByLsh(lsh.lsh.split('-')[0],orderBBList)
            delFile(date,True)
            for o in orderBBList:
                if 0==Zydh.objects.filter(orderlist=o.yorder_id,zydh=o.yzydh).count():
                    try:
                        zydh=Zydh()
                        zydh.zydh=o.yzydh
                        zydh.orderlist_id=o.yorder_id
                        zydh.save()
                    except:
                        pass
            return getResult(lsh.lsh)
    except CompluteNumError,e:
        order=OrderList.objects.get(pk=e.order)
        if order:
            orderbh=order.ddbh.ddbh
            codestr=order.code.code
        else:
            orderbh=''
            codestr=''
        wz=ProductSite.objects.get(pk=e.wz)
        result={'order':e.order,'wz':e.wz}
        msg='订单编号: %s 物料编号:%s 位置: %s ，剩余数量计算错误。'%(orderbh.encode('utf-8'),codestr.encode('utf-8'),wz.name.encode('utf-8'))
        return getResult(result,False,msg)
    except Exception,e:
        return getResult(False,False,'日报表保存错误，请检查数据。')
    finally:
        pass
@transaction.commit_on_success
def tiaozhengOrderBB(request):
    '''
    调整日报表，使数据重新规范化
    '''
    count=OrderGenZong.objects.filter(date__gt='20120810').count()
    OrderGenZong.objects.filter(date__gt='20120810').delete()
    orderbblist=[]
    for lsh in OrderBBNo.objects.all().order_by('id'):
        date=lsh.lsh.split('-')[0]
        orderBBList=OrderBB.objects.filter(lsh=lsh)
        initOrderMonitorByLsh(date,orderBBList,orderbblist)
    html=str(orderbblist)
    return HttpResponse(html)
#    return getResult(lsh.lsh)



@login_required
def isOrderBBNoUnlock(request,orderBBNo):
    date=orderBBNo.split('-')[0]
    orderBBLock=OrderBBLock.objects.filter(date=date)[:1]
    if len(orderBBLock)>0 and orderBBLock[0].is_lock:
        return getResult(False)
    else:
        return getResult(True)
    pass
@login_required
def getOrderBBByLsh(request,lshstr):
    lsh=OrderBBNo.objects.get(lsh=lshstr)
    return getResult({'list':OrderBB.objects.filter(lsh=lsh),'lsh':lshstr})
    pass

@login_required
@permission_required('ztmanage.order_zhuizong')
@transaction.commit_on_success
def getOrderGenZongToday(request,datestart,is_open,ddbh=None,code=None):

    return getOrderGenZongByDate(request,datestart,is_open,None,None,True)

@login_required
@permission_required('ztmanage.order_zhuizong')
@transaction.commit_on_success
def getOrderGenZongCache(request,datestart,is_open,ddbh=None,code=None):
    if is_open=='open':
        is_open=True
    else:
        is_open=False

    #if hasFile(datestart,is_open):
    r= getPickleObj(datestart,is_open)
    if r:
        return r
    return getResult(False,True,u'没有已经缓存好的数据，如需查询，请点击“同步数据”')

@login_required
@permission_required('ztmanage.order_zhuizong')
@transaction.commit_on_success
def getOrderGenZongByDate(request,datestart,is_open,ddbh=None,code=None,allsite=False):
    if is_open=='open':
        is_open=True
    else:
        is_open=False
    if not ddbh and not code and allsite:
        #if hasFile(datestart,is_open):
        r= getPickleObj(datestart,is_open)
        if r:
            return r


    result=getOrderGenZongRow(request,datestart,(is_open and ['open'] or ['close'])[0],ddbh,code,allsite)
    if not ddbh and not code and allsite:
        savePickle(datestart,is_open,result)
    return result

@transaction.commit_on_success
def autoCompleteGenZong(request):
    datestr=datetime.datetime.now().strftime("%Y%m%d")
    #if not hasFile(datestr,True):
    data=getOrderGenZongRow(request,datestr,'open')
    savePickle(datestr,True,data)
    #if not hasFile(datestr,False):
    data=getOrderGenZongRow(request,datestr,'close')
    savePickle(datestr,False,data)

    url='http://'+request.META['HTTP_HOST']+'/static/swf/'
    return render_to_response('zt/index.html',{'url':url,'p':datetime.datetime.now()})


@login_required
@permission_required('ztmanage.order_zhuizong')
def getZYOrderGenZongByOrderAndSite(request,orderlist_id,site_id):
    return getZYOrderGenZongByOrderAndSite_fn(request,orderlist_id,site_id)


@login_required
@permission_required('ztmanage.order_zhuizong')
def getZYOrderGenZongByOrderAndSite2(request,orderlist_id,site_id):
    result = getZYOrderGenZongByOrderAndSite_fn(request,orderlist_id,site_id)
    result['result']['orderlist_id']=orderlist_id
    result['result']['site_id']=site_id
    result['result']['len']=len(result['result']['result'])
    return result

def getZYOrderGenZongByOrderAndSite_fn(request,orderlist_id,site_id):
    result=[]
    genzongmap={}
    for orderbb in OrderBB.objects.filter(yorder=orderlist_id).filter(ywz=site_id):
        if not genzongmap.has_key(orderbb.yzydh.strip()):
            genzongmap[orderbb.yzydh.strip()]={'zydh':orderbb.yzydh.strip(),'zrnum':0,'zcnum':0,'ysnum':0,'bfnum':0}
        genzongmap[orderbb.yzydh.strip()]['zcnum']+=orderbb.ywznum-orderbb.ysnum-orderbb.bfnum
        genzongmap[orderbb.yzydh.strip()]['ysnum']+=orderbb.ysnum
        genzongmap[orderbb.yzydh.strip()]['bfnum']+=orderbb.bfnum
    for orderbb in OrderBB.objects.filter(zrorder=orderlist_id).filter(zrwz=site_id):
        if not genzongmap.has_key(orderbb.yzydh.strip()):
            genzongmap[orderbb.yzydh.strip()]={'zydh':orderbb.yzydh.strip(),'zrnum':0,'zcnum':0,'ysnum':0,'bfnum':0}
        genzongmap[orderbb.yzydh.strip()]['zrnum']+=orderbb.zrwznum
    for genzong in genzongmap.values():
        genzong['synum']=genzong['zrnum']-genzong['zcnum']-genzong['ysnum']-genzong['bfnum']
    k=list(genzongmap.keys())
    k.sort()
    for key in k:
        result.append(genzongmap[key])
    orderlist=OrderList.objects.get(pk=orderlist_id)

    sitename=ProductSite.objects.get(pk=site_id)
    resultmap={'result':result,'title':u'订单：%s 物料：%s 位置：%s'%(orderlist.ddbh.ddbh,orderlist.code.name,sitename.name)}
    return getResult(resultmap)


def getOrderGenZongRow(request,datestart,is_open,ddbh=None,code=None,allsite=False):
    if code and  type(code) is not int:
        return getResult(False,False,'物料选择错误')

    if is_open=='open':
        is_open=True
    else:
        is_open=False

    query=OrderGenZong.objects
#    if not ddbh and not code:
#        query=query.filter(is_last=is_last)
    orderlistquery=OrderList.objects.filter(is_open=is_open)
#    logging.error(str(is_open))
#    if not ddbh and not code:
#        orderlistquery=orderlistquery.filter(is_open=is_open)
    if ddbh:
#        query=query.filter(order__in=OrderList.objects.filter(ddbh__in=ddbh))
        orderlistquery=orderlistquery.filter(ddbh__in=ddbh)

    if code:
#        query=query.filter(order__in=OrderList.objects.filter(code=code))
        orderlistquery=orderlistquery.filter(code=code)
    if is_open:
#        query=query.filter(date__lte=datestart)ZCG1232001
        orderlistquery=orderlistquery.filter(createDate__lte=datetime.datetime.strptime(datestart,'%Y%m%d')+datetime.timedelta(hours =24))

#    orderlistquery=OrderList.objects.filter(id__in=[3525,3821,3822,3823,3824,3526,3892,3893,3894,3527,3895,3896,3897,3528,3530,3818,3529,3898,3899,3900,3901,3902,3903,3531,3996,3997,3998,3999,4000,4001,4002,3532,3837,3838,3533,3839,3840,3534,3864,3865,3866,3535,3991,3992,3993,3994,3995,10146,3536,4020,4021,4022,4023,4024,4025,4026,3537,4013,4014,4015,4016,4017,4018,4019,3538,4033,4034,4035,4036,3539,3985,3986,3987,3988,3989,3990,3540,3979,3980,3981,3982,3983,3984,3541,3819,3820,3542,3815,3816,3817,3543,3973,3974,3975,3976,3977,10145,3544,3545,3546,3547,3548,3549,3550,3551,3552,3553,3554,3555,3556,3557,3558,3559,3560,3561,3562,3563,3564,3565,3566,3567,3568,3569,10147,3570,3571,3572,3573,3574,3575,3576,3577,3578,3579,3580,3581,3582,3583,3584,3585,3586,3587,3588,3589,3590,10155,3591,3592,3593,3594,3595,3596,3597,3598,3599,3600,3601,3602,3603,3604,3605,3606,3607,3608,3609,3610,3611,3612,3613,3614,3615,3616,3617,3618,3619,3620,10151,3621,3622,3623,3624,3625,3626,3627,3628,10154,3629,3630,3631,3632,3633,3634,3635,3636,3637,3638,3639,3640,3641,3642,3643,3644,3645,3646,3647,3648,3649,3650,3651,3652,3653,3654,3655,3656,3657,3658,3659,3660,3661,3662,3663,3664,3665,3666,3667,3668,3669,3670,3671,3672,3673,3674,3675,3676,3677,3678,3679,3680,3681,10144,3682,3683,3684,3685,3686,3687,3688,3689,3690,3691,3692,3693,3694,3695,3696,3697,3698,3699,3700,3701,3702,3703,3704,3705,3706,3707,3708,3709,3710,3711,3712,3713,3714,3715,3716,3717,3718,3719,3720,3721,3722,3723,3724,3725,3726,3727,3728,3729,3730,3731,3732,3733,3734,3735,3736,3737,3738,3739,3740,3741,3742,3743,3744,3745,3746,3747,3748,3749,3750,3751,3752,3753,3754,3755,3756,3757,3758,3759,3760,3761,3762,3763,3764,3765,3766,3767,3768,3769,3770,3771,3772,3773,3774,3775,3776,3777,3778,3779,3780,3781,3782,3783,3784,3785,3786,3787,3788,3789,3790,3791,3792,3793,3794,3795,3796,3797,3798,3799,3800,3801,3802,3803,3804,3805,3806,3807,3808,10152,3809,3810,10142,3811,3812,3813,3814,3825,3826,3827,3828,3829,3830,3831,3832,3833,3834,3835,3836,3841,3842,3843,3844,3845,3846,3847,3848,3849,3850,3851,3852,3853,3854,3855,10139,3856,3857,3858,3859,3860,3861,3862,3863,3867,3868,10149,3869,3870,3871,3872,3873,3874,3875,3876,3877,3878,3879,3880,3881,3882,3883,3884,3885,3886,3887,3888,3889,3890,3891,3904,3905,3906,3907,3908,3909,3910,3911,3912,3913,10140,3914,3915,3916,3917,3918,3919,3920,3921,3922,3923,3924,10141,3925,3926,3927,3928,3929,3930,3931,3932,3933,3934,3935,10150,3936,3937,3938,3939,3940,3941,3942,3943,3944,3945,3946,3947,3948,3949,3950,3951,3952,3953,3954,3955,3956,3957,3958,3959,3960,3961,3962,3963,3964,3965,3966,3967,3968,3969,3970,3971,3972,10153,3978,4003,4004,4005,4006,4007,4008,4009,4010,4011,4012,10143,4027,4028,4029,4030,4031,4032,10148,10156,10157])

    head={'scx':'生产线','order':'订单编号','code':'代码','codename':'名称','codegg':'规格','ordernum':'物流需求数量','ckddcy':'出库订单差异','ddwczt':'订单完成状态','ddmzyf':'订单满足与否','qianxu':{'group':'前序','qiannum':'前序合计','index':['qiannum']},'houxu':{'group':'后序','hounum':'后序合计','index':['hounum']},'chukunum':'扫描出库','dj':'单价','cz':'产值','ddwcl':'订单完成率','closedate':'订单关闭日期'}
    head['index']=['scx','order','code','codename','codegg','ordernum','ckddcy','ddwczt','ddmzyf','qianxu','houxu','chukunum','dj','cz','ddwcl','closedate']
    sitequery=ProductSite.objects
    if allsite:
        sitequery=sitequery.filter(isaction=True)
    for site in sitequery.all():
        if site.type=='1':
            key='qianxu'
        elif site.type=='2':
            key='houxu'
        else:
            continue

        head[key]['wz'+str(site.pk)+'group']=site.name
        head[key]['wz'+str(site.pk)+'ywznum']='进入'
        head[key]['wz'+str(site.pk)+'zcnum']='转出'
        head[key]['wz'+str(site.pk)+'bfnum']='报废'
        head[key]['wz'+str(site.pk)+'ysnum']='遗失'
        head[key]['wz'+str(site.pk)+'synum']='剩余'
        head[key]['index'].append('wz'+str(site.pk)+'group')
        head[key]['index'].append('wz'+str(site.pk)+'ywznum')
        head[key]['index'].append('wz'+str(site.pk)+'zcnum')
        head[key]['index'].append('wz'+str(site.pk)+'bfnum')
        head[key]['index'].append('wz'+str(site.pk)+'ysnum')
        head[key]['index'].append('wz'+str(site.pk)+'synum')
    m={}
    includeorder=set()
    includecode=set()
    for o in orderlistquery:
        includeorder.add(o.ddbh_id)
        includecode.add(o.code_id)
#        orderno=getOrderNoByOrderList(o.ddbh_id)
#        codemap=getCodeNameById(o.code_id)
        row={'orderlist_id':o.pk,'dj':o.dj,'cz':o.cz,'code_id':o.code_id,'ddbh_id':o.ddbh_id,'ordernum':o.num,'qiannum':0,'hounum':0,'chukunum':0,'closedate':o.closeDate or '未关闭'}
        m[str(o.pk)]=row
    query=query.filter(order__in=orderlistquery)
    query=query.filter(date__lte=datestart)
    query=query.order_by('-order').order_by('-date')
    orderwzset=set()

    for o in query:
        if not m.has_key(str(o.order_id)):
            orderlistmap=getOrderByOrderlistid(o.order_id)
            codemap=getCodeNameById(orderlistmap['code'])

            row={'scx':codemap['scx'],'orderlist_id':o.order_id,'order':orderlistmap['ddbh'],'dj':orderlistmap['dj'],'cz':orderlistmap['cz'],'code':codemap['code'],'codename':codemap['name'],'codegg':codemap['gg'],'ordernum':orderlistmap['ordernum'],'qiannum':0,'hounum':0,'chukunum':0,'closedate':orderlistmap['closedate'] or '未关闭'}
            m[str(o.order_id)]=row
        else:
            row=m[str(o.order_id)]
        if str(o.order_id)+'wz'+str(o.wz_id) not in orderwzset:
            orderwzset.add(str(o.order_id)+'wz'+str(o.wz_id))
        else:
            continue
        row['wz'+str(o.wz_id)+'ywznum']=o.ywznum
        row['wz'+str(o.wz_id)+'zcnum']=o.zcnum
        row['wz'+str(o.wz_id)+'bfnum']=o.bfnum
        row['wz'+str(o.wz_id)+'ysnum']=o.ysnum
        row['wz'+str(o.wz_id)+'synum']=o.ywznum-o.zcnum-o.bfnum-o.ysnum
        if o.wz.type=='1':
            row['qiannum']+=row['wz'+str(o.wz_id)+'synum']
        elif o.wz.type=='2':
            row['hounum']+=row['wz'+str(o.wz_id)+'synum']
        elif o.wz.type=='3':
            row['chukunum']+=row['wz'+str(o.wz_id)+'synum']
    #####
#    print orderset
    codemap=getCodeByList(list(includecode))
    ddbhmap=getOrderNoByList(list(includeorder))

    for row in m.values():
        if ddbhmap.has_key('orderno'+str(row['ddbh_id'])):
            row['order']=ddbhmap['orderno'+str(row['ddbh_id'])]['ddbh']
        if codemap.has_key('code'+str(row['code_id'])):
            row['code']=codemap['code'+str(row['code_id'])]['code']
            row['codename']=codemap['code'+str(row['code_id'])]['name']
            row['codegg']=codemap['code'+str(row['code_id'])]['gg']
            row['scx']=codemap['code'+str(row['code_id'])]['scx']
        row['ckddcy']=row['ordernum']-row['chukunum']
        if row['ckddcy']>0:
            row['ddwczt']='0'
        else:
            row['ddwczt']='1'
#        row['dj']=
        row['ddmzyf']=row['qiannum']+row['hounum']-row['ordernum']+row['chukunum']
        if row['ordernum']:
            row['ddwcl']='%.2f%%'%(row['chukunum']/float(row['ordernum'])*100)
        else:
            row['ddwcl']=''
    result={'query':m.values(),'head':head}
#    cache.set(cachekey,result,60*10)
    resultdata= getResult(result)

    return resultdata

            
    #####计算其他值
    pass





#@login_required
def getOrderBBNo(request,date=None,userid=None):
    qs=OrderBBNo.objects
    if userid:
        qs=qs.filter(user=userid)
    if date:
        qs=qs.filter(lsh__startswith=date)
    if not userid and not date:
        return qs.all()[:20]
    return qs.all()

def addOrderBBNo(request):
    pass




def computeOrderMonitorByLsh(date,orderBBList,flag='add'):
    for orderBB in orderBBList:
        if orderBB.ywz_id:
            yorderGenZong=getOrderGenZong(orderBB.yorder,orderBB.ywz,date)
            if flag=='add':
                yorderGenZong.zcnum+=orderBB.ywznum-orderBB.bfnum-orderBB.ysnum
                yorderGenZong.bfnum+=orderBB.bfnum
                yorderGenZong.ysnum+=orderBB.ysnum
            else:
                yorderGenZong.zcnum-=orderBB.ywznum-orderBB.bfnum-orderBB.ysnum
                yorderGenZong.bfnum-=orderBB.bfnum
                yorderGenZong.ysnum-=orderBB.ysnum
            if yorderGenZong.ywznum-yorderGenZong.zcnum-yorderGenZong.ysnum-yorderGenZong.bfnum<0:
                    raise CompluteNumError(yorderGenZong.order_id,yorderGenZong.wz_id)
            else:
                if not yorderGenZong.id:
                    yorderGenZong.save()
                else:
                    OrderGenZong.objects.filter(pk=yorderGenZong.id).update(zcnum=yorderGenZong.zcnum,bfnum=yorderGenZong.bfnum,ysnum=yorderGenZong.ysnum)
        if orderBB.zrwz_id:
            zrorderGenZong=getOrderGenZong(orderBB.zrorder,orderBB.zrwz,date)
            #raise CompluteNumError(zrorderGenZong.order_id,zrorderGenZong.wz_id)
            if flag=='add':
                zrorderGenZong.ywznum+=orderBB.zrwznum
            else:
                zrorderGenZong.ywznum-=orderBB.zrwznum
            if zrorderGenZong.ywznum-zrorderGenZong.zcnum-zrorderGenZong.ysnum-zrorderGenZong.bfnum<0:
                    raise CompluteNumError(zrorderGenZong.order_id,zrorderGenZong.wz_id)
            else:
                if not zrorderGenZong.id:
                    zrorderGenZong.save()
                else:
                    OrderGenZong.objects.filter(pk=zrorderGenZong.id).update(ywznum=zrorderGenZong.ywznum)

## 根据日报表初始化跟踪表
def initOrderMonitorByLsh(date,orderBBList,orderbblist,flag='add'):

    for orderBB in orderBBList:
        yorderGenZong=None
        yorder=True
        zrorderGenZong=None
        zrorder=True
        if orderBB.ywz_id:
            yorderGenZong=getOrderGenZong(orderBB.yorder,orderBB.ywz,date)
            if flag=='add':
                yorderGenZong.zcnum+=orderBB.ywznum-orderBB.bfnum-orderBB.ysnum
                yorderGenZong.bfnum+=orderBB.bfnum
                yorderGenZong.ysnum+=orderBB.ysnum
            else:
                yorderGenZong.zcnum-=orderBB.ywznum-orderBB.bfnum-orderBB.ysnum
                yorderGenZong.bfnum-=orderBB.bfnum
                yorderGenZong.ysnum-=orderBB.ysnum
            if yorderGenZong.ywznum-yorderGenZong.zcnum-yorderGenZong.ysnum-yorderGenZong.bfnum<0:
                yorder=False
        if orderBB.zrwz_id:
            zrorderGenZong=getOrderGenZong(orderBB.zrorder,orderBB.zrwz,date)
            if flag=='add':
                zrorderGenZong.ywznum+=orderBB.zrwznum
            else:
                zrorderGenZong.ywznum-=orderBB.zrwznum
            if zrorderGenZong.ywznum-zrorderGenZong.zcnum-zrorderGenZong.ysnum-zrorderGenZong.bfnum<0:
                zrorder=False
        if yorder and zrorder:
            if yorderGenZong:
                if not yorderGenZong.id:
                    yorderGenZong.save()
                else:
                    OrderGenZong.objects.filter(pk=yorderGenZong.id).update(zcnum=yorderGenZong.zcnum,bfnum=yorderGenZong.bfnum,ysnum=yorderGenZong.ysnum)
            if zrorderGenZong:
                if not zrorderGenZong.id:
                    if zrorderGenZong.order_id==3542 and zrorderGenZong.wz_id==9:
                        print zrorderGenZong.id
                    zrorderGenZong.save()
                else:
                    OrderGenZong.objects.filter(pk=zrorderGenZong.id).update(ywznum=zrorderGenZong.ywznum)
        else:
            orderbblist.append(orderBB.id)
#    return getResult(lsh)

#def setCompluteOrder(key,computeOrder):
#    if settings.DDGENZONG.has_key(key):
#        raise CompluteError,key+'...正在计算'
#    computeOrder.append(key)
#    settings.DDGENZONG[key]=1
def getOrderGenZong(orderid,wzid,date):

    l=OrderGenZong.objects.filter(order=orderid).filter(wz=wzid).order_by('-date')[:2]
    if len(l)==0:
        obj=OrderGenZong()
        obj.order=orderid
        obj.wz=wzid
        obj.date=date
#        setCompluteOrder('o'+str(orderid.pk)+'w'+str(wzid.pk)+'d'+str(date),computeOrder)
        return obj
    elif len(l)==1:
        if l[0].date==date:
#            setCompluteOrder('o'+str(orderid.pk)+'w'+str(wzid.pk)+'d'+str(date),computeOrder)
            return l[0]
        else:
            obj=OrderGenZong()
            obj.order=orderid
            obj.wz=wzid
            obj.date=date
            obj.ywznum=l[0].ywznum
            obj.zcnum=l[0].zcnum
            obj.bfnum=l[0].bfnum
            obj.ysnum=l[0].ysnum
#            setCompluteOrder('o'+str(orderid.pk)+'w'+str(wzid.pk)+'d'+str(date),computeOrder)
            return obj
    elif len(l)==2:
        if l[0].date==date:
#            setCompluteOrder('o'+str(orderid.pk)+'w'+str(wzid.pk)+'d'+str(date),computeOrder)
            return l[0]
        else:
            obj=OrderGenZong()
            obj.order=orderid
            obj.wz=wzid
            obj.date=date
            obj.ywznum=l[0].ywznum
            obj.zcnum=l[0].zcnum
            obj.bfnum=l[0].bfnum
            obj.ysnum=l[0].ysnum
#            setCompluteOrder('o'+str(orderid.pk)+'w'+str(wzid.pk)+'d'+str(date),computeOrder)
            return obj


    pass


@login_required
def getWriteExcel(request,date,headobj,nohead,rows):
    nowritehead=nohead.keys()
    head=headobj._amf_object
    filename=date+'-'+str(uuid.uuid4())+'.xls'
    style1=xlwt.XFStyle()
    font1=Font()
    font1.height=220
    style1.font=font1
    algn=Alignment()
    algn.horz=Alignment.HORZ_RIGHT
    style1.alignment=algn
    style0=xlwt.XFStyle()
    algn0=Alignment()
    algn0.horz=Alignment.HORZ_CENTER
    font=Font()
    font.height=280
    font.bold=True
    style0.alignment=algn0
    style0.font=font
#    font = xlwt.Font() #为样式创建字体
#    font.name = 'Times New Roman'
#    font.bold = True
#    style1.font = font #为样式设置字体
    wb=xlwt.Workbook()
    ws=wb.add_sheet(date,cell_overwrite_ok=True)

    col=0
    for m,filedata in enumerate(head['index']):
        if filedata  in nowritehead:
            continue
        if filedata=='qianxu' or filedata=='houxu':
            subcol=col
            wz=0
            for subfiledata in head[head['index'][m]]['index']:
                if subfiledata  in nowritehead:
                    continue
                if subcol==col:
                    ws.write_merge(1,2,subcol-wz,subcol-wz,head[head['index'][m]][subfiledata],style0)
                else:
                    if (subcol-col)%6==1:
                        wz+=1
                        subcol+=1
                        ws.write_merge(1,1,subcol-wz,subcol-wz+4,head[head['index'][m]][subfiledata],style0)


                        continue
                    ws.write_merge(2,2,subcol-wz,subcol-wz,head[head['index'][m]][subfiledata],style0)
                for i,data in enumerate(rows):
                    if data.has_key(subfiledata):
                        ws.write(i+3,subcol-wz,data[subfiledata],style1)
                subcol+=1
            ws.write_merge(0,0,col,subcol-wz-1,head[head['index'][m]]['group'],style0)
            col=subcol-wz
            continue
        ws.write_merge(0, 2,col,col,head[filedata], style0)
        for i,data in enumerate(rows):
            if data.has_key(filedata):
                ws.write(i+3,col,data[filedata],style1)
        col+=1

    wb.save(MEDIA_ROOT+'/excel/'+filename)
    return getResult('http://'+request.META['HTTP_HOST']+'/static/excel/'+filename)


@login_required
def getWriteExcel2(request,date,headobj,nohead,rows):
    nowritehead=nohead.keys()
    head=headobj._amf_object
    filename=date+'-'+str(uuid.uuid4())+'.xls'
    style1=xlwt.XFStyle()
    font1=Font()
    font1.height=220
    style1.font=font1
    algn=Alignment()
    algn.horz=Alignment.HORZ_RIGHT
    style1.alignment=algn
    style0=xlwt.XFStyle()
    algn0=Alignment()
    algn0.horz=Alignment.HORZ_CENTER
    font=Font()
    font.height=280
    font.bold=True
    style0.alignment=algn0
    style0.font=font
#    font = xlwt.Font() #为样式创建字体
#    font.name = 'Times New Roman'
#    font.bold = True
#    style1.font = font #为样式设置字体
    wb=xlwt.Workbook()
    ws=wb.add_sheet(date,cell_overwrite_ok=True)
    zydhlengthead='maxlength'
    col=0
    for m,filedata in enumerate(head['index']):
        if filedata  in nowritehead:
            continue
        if filedata=='qianxu' or filedata=='houxu':
            subcol=col
            wz=0
            for subfiledata in head[head['index'][m]]['index']:
                if subfiledata  in nowritehead:
                    continue
                if subcol==col:
                    ws.write_merge(1,2,subcol-wz,subcol-wz,head[head['index'][m]][subfiledata],style0)
                else:
                    if (subcol-col)%8==1:
                        wz+=1
                        subcol+=1
                        ws.write_merge(1,1,subcol-wz,subcol-wz+6,head[head['index'][m]][subfiledata],style0)


                        continue
                    ws.write_merge(2,2,subcol-wz,subcol-wz,head[head['index'][m]][subfiledata],style0)
                rownum=3

                for i,data in enumerate(rows):
                    maxlength=data[zydhlengthead]
                    if maxlength>0:
                        if data.has_key(subfiledata):
                            ws.write(rownum,subcol-wz,data[subfiledata],style1)
                            # ws.write_merge(rownum,rownum+maxlength-1,subcol-wz,subcol-wz,data[subfiledata],style1)
                        # else:
                        #     ws.write_merge(rownum,rownum+maxlength-1,subcol-wz,subcol-wz,'',style1)
                        rownum+=maxlength
                    else:
                        if data.has_key(subfiledata):
                            ws.write(rownum,subcol-wz,data[subfiledata],style1)
                        rownum+=1

                subcol+=1
                if subfiledata.find('synum')>-1:
                    ws.write_merge(2,2,subcol-wz,subcol-wz,u'作业单号',style0)
                    ws.col(subcol-wz).width = 256 * 20
                    ws.write_merge(2,2,subcol-wz+1,subcol-wz+1,u'作业剩余',style0)
                    ws.col(subcol-wz+1).width = 256 * 15
                    rownum=3

                    for i,data in enumerate(rows):
                        maxlength=data[zydhlengthead]
                        if maxlength>0:
                            if data.has_key('%s2'%subfiledata):
                                for j,zydata in enumerate(data['%s2'%subfiledata]):
                                    if zydata.has_key('zydh'):
                                        ws.write(rownum+j,subcol-wz,zydata['zydh'],style1)
                                    if zydata.has_key('synum'):
                                        ws.write(rownum+j,subcol-wz+1,zydata['synum'],style1)
                            rownum+=maxlength

                        else:
                            rownum+=1

                    subcol+=2
            ws.write_merge(0,0,col,subcol-wz-1,head[head['index'][m]]['group'],style0)
            col=subcol-wz
            continue
        ws.write_merge(0, 2,col,col,head[filedata], style0)
        rownum=3

        for i,data in enumerate(rows):
            maxlength=data[zydhlengthead]
            if maxlength>0:
                if data.has_key(filedata):
                    ws.write(rownum,col,data[filedata],style1)
                    # ws.write_merge(rownum,rownum+maxlength-1,col,col,data[filedata],style1)
                # else:
                #     ws.write_merge(rownum,rownum+maxlength-1,col,col,'',style1)
                rownum+=maxlength
                # ws.write(i+3,col,data[filedata],style1)
            else:
                if data.has_key(filedata):
                    ws.write(rownum,col,data[filedata],style1)
                rownum+=1
        col+=1

    wb.save(MEDIA_ROOT+'/excel/'+filename)
    return getResult('http://'+request.META['HTTP_HOST']+'/static/excel/'+filename)



@login_required
def getOrderExcel(request,date,headobj,nohead,rows):
    '''
    订单导出excel
    '''
    return getOrderBBExcel(request,date,headobj,nohead,rows)

@login_required
def getCodeExcel(request,date,headobj,nohead,rows):
    '''
    物料导出excel
    '''
    return getOrderBBExcel(request,date,headobj,nohead,rows)

######
@login_required
def getOrderBBExcel(request,date,headobj,nohead,rows):#日报表导出
    """
    日报表导出excel
    """
    nowritehead=nohead.keys()
    head=headobj
    filename=date+'-'+str(uuid.uuid4())+'.xls'
    style1=xlwt.XFStyle()
    font1=Font()
    font1.height=220
    style1.font=font1
    algn=Alignment()
    algn.horz=Alignment.HORZ_RIGHT
    style1.alignment=algn
    style0=xlwt.XFStyle()
    algn0=Alignment()
    algn0.horz=Alignment.HORZ_CENTER
    font=Font()
    font.height=280
    font.bold=True
    style0.alignment=algn0
    style0.font=font
    wb=xlwt.Workbook()
    ws=wb.add_sheet(date,cell_overwrite_ok=True)

    col=0
    for m,filedata in enumerate(head['index']):
        if filedata  in nowritehead:
            continue
        if filedata.find('group')!=-1 :
            ws.write_merge(0,0,col,col+len(head[head['index'][m]]['index'])-1,head[head['index'][m]]['group'],style0)
            for subfiledata in head[head['index'][m]]['index']:
                if subfiledata  in nowritehead:
                    continue


                ws.write_merge(1,1,col,col,head[head['index'][m]][subfiledata],style0)




                for i,data in enumerate(rows):
                    if data.has_key(subfiledata):
                        ws.write(i+2,col,data[subfiledata],style1)
                col+=1
            continue
        ws.write_merge(0, 1,col,col,head[filedata], style0)
        for i,data in enumerate(rows):
            if data.has_key(filedata):
                ws.write(i+2,col,data[filedata],style1)
        col+=1

    wb.save(MEDIA_ROOT+'/excel/'+filename)
    return getResult('http://'+request.META['HTTP_HOST']+'/static/excel/'+filename)


