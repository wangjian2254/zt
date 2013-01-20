#coding=utf-8
# Create your views here.
from datetime import datetime
import time
from django.contrib.auth.models import User
from django.template.context import RequestContext

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from zt.ztmanage.models import Code, Scx, ProductSite, OrderList, OrderBB, OrderNo, OrderBBNo


@login_required
def index(request):
    url='http://'+request.META['HTTP_HOST']+'/static/swf/'
    return render_to_response('zt/index.html',{'url':url,'p':datetime.now()})
#    return render_to_response('zt/workframe.html',{})
@login_required
def top(request):
    user=request.user
    return render_to_response('zt/topnav.html',locals())
@login_required
def menu(request):
    return render_to_response('zt/menu.html',{})
@login_required
def welcome(request):
    return render_to_response('zt/welcome.html',{})

def noperm(request):
    return render_to_response('zt/noperm.html',{})

def user_is_adder(user):
    return user.has_perm("ztmanage.user_add")

@login_required
@user_passes_test(user_is_adder,login_url='/zt/noperm')
def dataadd(request):
    return render_to_response('zt/dataadd.html',{},context_instance=RequestContext(request))


@login_required
@user_passes_test(user_is_adder,login_url='/zt/noperm')
def codeupload(request):
    code_list_str=request.POST.get('codelist','')
    codemaplist=[]
    codemap={}
    num=1
    if code_list_str:

        for code in code_list_str.split():
            codeobj=getCodeByBH(codemap,code)
            obj={}
            obj['codeindex']=gsIndex(num)
            obj['code']=code
            if codeobj:
                obj['codename']=codeobj.name
                obj['codegg']=codeobj.gg
                obj['scx']=codeobj.scx.name
            else:
                continue
            obj['bfnum']=0
            codemaplist.append(obj)
            num+=1
    return render_to_response('zt/dataadd.html',{'num':len(codemaplist),'nowdate':datetime.now(),'codelist':codemaplist,'scxlist':Scx.objects.all(),'productsitelist':ProductSite.objects.all()},context_instance=RequestContext(request))

def getCodeByBH(codemap,code):
    if not codemap.has_key(code):
        listcode=Code.objects.filter(code=code)[:1]
        if len(listcode)==1:
            codemap[code]=listcode[0]
    if not codemap.has_key(code):
        return None
    return codemap[code] or None
def getScxById(codemap,code):
    if not codemap.has_key(code):
        listcode=Scx.objects.filter(pk=code)[:1]
        if len(listcode)==1:
            codemap[code]=listcode[0]
    if not codemap.has_key(code):
        return None
    return codemap[code] or None
def getProductSiteById(codemap,code):
    if not codemap.has_key(code) and code:
        listcode=ProductSite.objects.filter(pk=code)[:1]
        if len(listcode)==1:
            codemap[code]=listcode[0]
    if not codemap.has_key(code):
        return None
    return codemap[code] or None
def gsIndex(num):
    return ('0000'+str(num))[-4:]

def orderbbsave(request):
    is_val=True
    num=request.POST.get('num',0)
    try:
        num=int(num)
    except :
        num=0
    date=request.POST.get('date','')
    if date:
        t = time.strptime(date, "%Y-%m-%d %H:%M")
        y,m,d,h,M = t[0:5]
        date= datetime(y,m,d,hour=t[3],minute=t[4])
#        date.hour=t[3]
#        date.minute=t[4]
    else:
        date=datetime.no

    codemaplist=[]
    codemap={}
    scxmap={}
    productmap={}
    for i in range(1,num+1):
        id=request.POST.get('id'+gsIndex(i),'')
        ddbh=request.POST.get('ddbh'+gsIndex(i),'')
        code=request.POST.get('code'+gsIndex(i),'')
        yzydh=request.POST.get('yzydh'+gsIndex(i),'')
        ywzname=request.POST.get('ywzname'+gsIndex(i),'')
        ywznum=request.POST.get('ywznum'+gsIndex(i),'')
        zrwzname=request.POST.get('zrwzname'+gsIndex(i),'')
        zrwznum=request.POST.get('zrwznum'+gsIndex(i),'')
        bfnum=request.POST.get('bfnum'+gsIndex(i),'')
        bztext=request.POST.get('bztext'+gsIndex(i),'')
        codeobj=getCodeByBH(codemap,code)
        obj={}
        obj['codeindex']=gsIndex(i)
        obj['code']=code
        obj['id']=id
        if codeobj:
            obj['codename']=codeobj.name
            obj['codegg']=codeobj.gg
            obj['scx']=codeobj.scx.name
        else:
            obj['codeerr']='代码不存在'
            is_val=False
        obj['ddbh']=ddbh
        obj['yzydh']=yzydh
        obj['ywzname']=ywzname

        try:
            ywznum=int(ywznum)
        except :
            obj['ywznumerr']='必须是数字'
            is_val=False
        obj['ywznum']=ywznum
        obj['zrwzname']=zrwzname

        try:
            zrwznum=int(zrwznum)
        except :
            obj['zrwznumerr']='必须是数字'
            is_val=False
        obj['zrwznum']=zrwznum

        obj['bztext']=bztext
        try:
            bfnum=int(bfnum)
        except :
            obj['bfnumerr']='必须是数字'
            is_val=False

        obj['bfnum']=bfnum
        codemaplist.append(obj)
    if not is_val:
        return render_to_response('zt/dataadd.html',{'num':len(codemaplist),'nowdate':date,'message':'有数据格式不正确。','codelist':codemaplist,'scxlist':Scx.objects.all(),'productsitelist':ProductSite.objects.all()},context_instance=RequestContext(request))
    else:
        for m in codemaplist:
            o=OrderBB()
            if m.has_key('id') and m['id']:
                o.pk=m['id']
            o.ddbh=m['ddbh']
            o.code=getCodeByBH(codemap,m['code'])
            o.yzydh=m['yzydh']
            o.ywz=getProductSiteById(productmap,m['ywzname'])
            if o.ywz:
                m['ywzname']=o.ywz.pk
            o.ywznum=m['ywznum']
            o.zrwz=getProductSiteById(productmap,m['zrwzname'])
            if o.zrwz:
                m['zrwzname']=o.zrwz.pk
            o.zrwznum=m['zrwznum']
            o.bfnum=m['bfnum']
            o.bztext=m['bztext']
            o.createDate=date
            o.save()
            m['id']=o.pk
        return render_to_response('zt/dataadd.html',{'num':len(codemaplist),'nowdate':date,'message':'保存成功。','codelist':codemaplist,'scxlist':Scx.objects.all(),'productsitelist':ProductSite.objects.all()},context_instance=RequestContext(request))

@login_required
@user_passes_test(user_is_adder,login_url='/zt/noperm')
def orderbblist(request):
#    code_list_str=request.POST.get('codelist','')
    codemaplist=[]
    codemap={}
    num=1
#    if code_list_str:
    i=1
    for order in OrderBB.objects.all():
        obj={}
        obj['codeindex']=gsIndex(i)
        obj['code']=order.code.code
        obj['id']=order.pk
        obj['codename']=order.code.name
        obj['codegg']=order.code.gg
        obj['scx']=order.code.scx.name
        obj['ddbh']=order.ddbh
        obj['yzydh']=order.yzydh
        if order.ywz:
            obj['ywzname']=order.ywz.pk

        obj['ywznum']=order.ywznum
        if order.zrwz:
            obj['zrwzname']=order.zrwz.pk

        obj['zrwznum']=order.zrwznum

        obj['bztext']=order.bztext

        obj['bfnum']=order.bfnum
        codemaplist.append(obj)
        i+=1
    return render_to_response('zt/dataadd.html',{'num':len(codemaplist),'nowdate':datetime.now(),'codelist':codemaplist,'scxlist':Scx.objects.all(),'productsitelist':ProductSite.objects.all()},context_instance=RequestContext(request))

def checkZZB(request):
    from zt.ztmanage.flexview import getOrderGenZongRow,getZYOrderGenZongByOrderAndSite_fn

    errorordergzlist=[]

    result=getOrderGenZongRow(request,datetime.now().strftime("%Y%m%d"),'open')
    sitelist=[]
    for site in ProductSite.objects.all().filter(type__in=[1,2]):
        sitelist.append(site)
    for row in result['result']['query']:
        for site in sitelist:
            if row.has_key('wz'+str(site.id)+'synum'):
                yzydhlist=getZYOrderGenZongByOrderAndSite_fn(request,row['orderlist_id'],site.id)
                yzydhsynum=0
                for yzydh in yzydhlist['result']['result']:
                    yzydhsynum+=yzydh['synum']
                if row['wz'+str(site.id)+'synum']!=yzydhsynum:
                    errorordergzlist.append({'orderlist_id':row['orderlist_id'],'ddbh':row['order'],'code':row['code'],'site':site.name,'synum':row['wz'+str(site.id)+'synum'],'zysynum':yzydhsynum,'countnum':row['wz'+str(site.id)+'synum']-yzydhsynum})
    return render_to_response('zt/errororderlist.html',{'rows':errorordergzlist})








