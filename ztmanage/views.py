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
    orderidstr='5989,6794,6795,6792,6790,6791,6798,279,279,12014,4843,4721,4722,5842,5202,9752,9751,697,3533,3537,3537,154,156,2722,812,8738,6430,2531,2531,2537,2537,5384,5387,791,791,4974,2886,2889,5800,2705,4881,4887,3471,3471,6415,5010,5011,4417,911,911,910,910,1444,1444,2005,2005,2005,5824,5827,854,855,5223,5225,1306,1300,1309,1309,4432,10126,5594,5200,5200,1320,1321,1325,11853,11853,11855,1667,2822,2822,5417,3382,339,2010,2010,4865,5008,450,4467,4461,2461,2463,1420,4868,5551,5880,4801,2073,4395,4395,4397,1363,1999,1999,5530,6570,6571,6577,3837,6653,2052,13190,2422,2422,2427,2427,1909,1909,6517,6169,4510,4511,4516,5209,4474,431,431,4981,4983,4982,2150,4984,4987,4986,4989,4988,3241,5498,5491,4375,8664,6645,2397,4963,5129,5915,5913,4940,4943,2117,666,4122,4127,4125,4124,5689,5689,5689,888,888,2589,2589,4336,4331,3131,5186,2354,2354,3739,3739,3739,4693,2131,4805,649,4480,2489,703,703,5312,5317,4714,4710,2339,2339,4718,4679,4676,4903,4905,4671,4671,2481,2481,124,6825,6825,8745,8743,8742,8740,4241,2673,2673,3176,3176,4684,4685,4737,2318,2318,1757,1757,1757,685,681,2699,4759,4754,4757,4757,168,6195,5606,5181,4772,5816,4889,147,2710,4405,4402,13,6407,6407,2522,2522,5394,5398,2893,1452,1452,4690,4920,4794,4794,4695,5835,2130,2130,4696,5839,4699,4899,4890,4890,4897,4896,4895,9721,9729,845,845,3464,3464,3462,5003,5002,5001,5000,5007,5006,5005,5004,5009,1453,1453,903,903,4420,1696,2287,4820,186,187,187,2024,1315,2564,2564,5022,3092,3092,3092,3092,1676,4498,306,4416,6614,4412,5402,5408,5544,5544,5899,4915,328,6139,6137,4875,4874,4877,4871,4873,4878,2065,2065,3184,2477,4485,12153,9647,1982,1982,1983,2816,2816,1186,5426,5422,5526,5527,42,6541,6541,6540,6154,4520,2046,4810,4385,4384,1374,2452,2452,4985,5191,2879,3358,5503,541,366,901,901,5291,1394,1394,1394,1391,4715,2334,2334,4711,4713,2438,2438,2435,4719,4996,4997,4994,4995,4992,4993,4990,4991,4998,4999,3251,3332,3338,3338,528,6501,4673,4673,4907,5920,5923,1002,1002,1001,1001,4348,4348,4494,4492,1822,1822,2419,2419,4975,4977,2149,2149,4973,4220,5486,5482,630,6524,5904,2385,2385,2386,1276,2594,2594,1043,1043,4707,4706,6675,4709,4708,2367,2367,2362,2362,4933,4682,4683,4680,4688,4689,2497,2497,6028,712,712,5303,1358,3709,3709,1881,1881,4916,4917,4917,4661,4910,4911,5174,5178,6581,6009,2930,2930,4703,4701,4700,2494,119,1742,1568'
    idlist=[]
    for id in orderidstr.split(','):
        idlist.append(int(id))
    errorordergzlist=[]

    result=getOrderGenZongRow(request,datetime.now().strftime("%Y%m%d"),'open')
    sitelist=[]
    for site in ProductSite.objects.all():
        sitelist.append(site)
    for row in result['result']['query']:
        if row['orderlist_id'] not in idlist:
            continue
        for site in sitelist:
            if row.has_key('wz'+str(site.id)+'synum'):
                yzydhlist=getZYOrderGenZongByOrderAndSite_fn(request,row['orderlist_id'],site.id)
                yzydhsynum=0
                for yzydh in yzydhlist['result']['result']:
                    yzydhsynum+=yzydh['synum']
                if row['wz'+str(site.id)+'synum']!=yzydhsynum:
                    errorordergzlist.append({'orderlist_id':row['orderlist_id'],'ddbh':row['order'],'code':row['code'],'site':site.name,'synum':row['wz'+str(site.id)+'synum'],'zysynum':yzydhsynum,'countnum':row['wz'+str(site.id)+'synum']-yzydhsynum})
    return render_to_response('zt/errororderlist.html',{'rows':errorordergzlist})








