#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import base64
import urllib
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
import json
from django.views.decorators.csrf import  csrf_exempt
from zt.settings import MEDIA_ROOT
from zt import xlwt
from zt.xlwt import Font, Alignment
from PIL import Image
import uuid
__author__ = u'王健'

def gsdate(date):
    return u'%s月%s日'%(date[4:6],date[6:8])


@login_required
@csrf_exempt
def uploadImage(request):

    data = request.read()
    if data:
        data = json.loads(data)
    else:
        raise Http404()
    img1name=MEDIA_ROOT+'/excel/'+str(uuid.uuid4())
    img2name=MEDIA_ROOT+'/excel/'+str(uuid.uuid4())
    img1=img1name+'.png'
    img2=img2name+'.png'
    img1bmp=img1name+'.bmp'
    img2bmp=img2name+'.bmp'



    s=str(data.get('img1','').replace(' ','+'))
    with open(img1,'wb') as f:
        f.write(base64.decodestring(s))



    s=str(data.get('img2','').replace(' ','+'))
    with open(img2,'wb') as f:
        f.write(base64.decodestring(s))
    try:
        Image.open(img1).convert("RGB").save(img1bmp)
        Image.open(img2).convert("RGB").save(img2bmp)
    except:
        import os
        command ='c:/python27/python.exe %s/img.py '%MEDIA_ROOT
        os.system(command)

    response = HttpResponse(mimetype=u'application/ms-excel')
    excelname = data.get('excelname','')
    sheetname = data.get('sheetname','')
    scx = data.get('scx','')
    site = data.get('site','')
    code = data.get('ismain','')

    filename = u'%s.xls'%urllib.quote(excelname.encode('utf-8'))
    if hasattr(request,'META') and request.META.has_key('HTTP_USER_AGENT'):
        if request.META['HTTP_USER_AGENT'].find("Firefox")!=-1:
            filename = u'%s.xls'%excelname

    response['Content-Disposition'] = ('attachment;filename=%s' % filename).encode('utf-8')


    style1=xlwt.XFStyle()
    font1=Font()
    font1.height=220
    style1.font=font1
    algn=Alignment()
    algn.horz=Alignment.HORZ_CENTER
    algn.vert=Alignment.VERT_CENTER
    style1.alignment=algn
    style0=xlwt.XFStyle()
    algn0=Alignment()
    algn0.horz=Alignment.HORZ_CENTER
    algn0.vert=Alignment.VERT_CENTER
    font=Font()
    font.height=280
    font.bold=True
    style0.alignment=algn0
    style0.font=font

    wb = xlwt.Workbook()
    ws = wb.add_sheet(u"%s"%sheetname, cell_overwrite_ok=True)
    ws.write_merge(0,1,0,2,u'作者：%s'%request.user.last_name,style0)
    ws.write_merge(2,3,0,1,u'数据',style0)
    ws.write_merge(4,5,0,1,u'项目',style0)
    ws.write_merge(6,7,0,1,u'本期应达成项数',style0)
    ws.write_merge(8,9,0,1,u'本期应达成件数',style0)
    ws.write_merge(10,11,0,1,u'前期应追项数',style0)
    ws.write_merge(12,13,0,1,u'前期应追件数',style0)
    ws.write_merge(14,15,0,1,u'提前完成项数',style0)
    ws.write_merge(16,17,0,1,u'提前完成件数',style0)
    ws.write_merge(18,19,0,1,u'件数日达成率',style0)
    ws.write_merge(20,21,0,1,u'项数日达成率',style0)
    ws.write_merge(22,26,0,1,u'计划\n\t未完成分析\n\t以及解决措施',style0)
    ws.write_merge(27,30,0,1,u'计划员总结',style0)
    ws.col(0).width = 256 * 12
    ws.col(1).width = 256 * 12



    rownum=2
    datadict={"bzxiangjh":0,'bzxiangsj':0,'bzjianjh':0,'bzjiansj':0,'xiangdc':'0%','jiandc':'0%'}
    arrdata=json.loads(data.get('data',''))
    for row,d in enumerate(arrdata):

        ws.write_merge(2, 3, rownum+row*2, rownum+row*2+1, gsdate(d.get("date","")), style1)
        ws.write_merge(4, 5, rownum+row*2, rownum+row*2, u'计划', style1)
        ws.write_merge(4, 5, rownum+row*2+1, rownum+row*2+1, u'实际', style1)
        ws.write_merge(6, 7, rownum+row*2, rownum+row*2, d.get("bzxiangjh",""), style1)
        ws.write_merge(6, 7, rownum+row*2+1, rownum+row*2+1, d.get("bzxiangsj",""), style1)
        ws.write_merge(8, 9, rownum+row*2, rownum+row*2, d.get("bzjianjh",""), style1)
        ws.write_merge(8, 9, rownum+row*2+1, rownum+row*2+1, d.get("bzjiansj",""), style1)
        ws.write_merge(10, 11, rownum+row*2+1, rownum+row*2+1, d.get("qqxiangsj",""), style1)
        ws.write_merge(12,13, rownum+row*2+1, rownum+row*2+1, d.get("qqjiansj",""), style1)
        ws.write_merge(14,15, rownum+row*2+1, rownum+row*2+1, d.get("tqxiangsj",""), style1)
        ws.write_merge(16,17, rownum+row*2+1, rownum+row*2+1, d.get("tqjiansj",""), style1)
        ws.write_merge(18,19, rownum+row*2, rownum+row*2+1, '%s%%'%d.get("jianri",""), style1)
        ws.write_merge(20,21, rownum+row*2, rownum+row*2+1, '%s%%'%d.get("xiangri",""), style1)

        ws.write_merge(22,26, rownum+row*2, rownum+row*2+1, '', style1)
        ws.write_merge(27,30, rownum+row*2, rownum+row*2+1, '', style1)
        datadict['bzxiangjh']+=d.get('bzxiangjh')
        datadict['bzxiangsj']+=d.get('bzxiangsj')
        datadict['bzjianjh']+=d.get('bzjianjh')
        datadict['bzjiansj']+=d.get('bzjiansj')
        ws.col(rownum+row*2).width = 256 * 12
        ws.col(rownum+row*2+1).width = 256 * 12
    if datadict['bzxiangjh']>0:
        datadict['xiangdc']='%.2f%%'%((float(datadict['bzxiangsj'])/datadict['bzxiangjh'])*100,)
    if datadict['bzjianjh']>0:
        datadict['jiandc']='%.2f%%'%((float(datadict['bzjiansj'])/datadict['bzjianjh'])*100,)
    length=len(arrdata)*2
    ws.write_merge(0,1,3,rownum+length,u'生产线:%s   作业区:%s  主配件:%s    %s'%(scx,site,code,excelname),style0)
    ws.write_merge(0,1,rownum+length+1,rownum+length+3,u'考核期：%s——%s'%(gsdate(excelname.split('-')[1]),gsdate(excelname.split('-')[2])),style0)
    ws.write_merge(2, 3, rownum+length, rownum+length+1, u'合计', style1)
    ws.write_merge(2, 5, rownum+length+2, rownum+length+3, u'累计达成率', style1)
    ws.write_merge(4, 5, rownum+length, rownum+length, u'计划', style1)
    ws.write_merge(4, 5, rownum+length+1, rownum+length+1, u'实际', style1)
    ws.write_merge(6, 7, rownum+length, rownum+length, datadict['bzxiangjh'], style1)
    ws.write_merge(6, 7, rownum+length+1, rownum+length+1, datadict['bzxiangsj'], style1)
    ws.write_merge(6, 7, rownum+length+2, rownum+length+3, datadict['xiangdc'], style1)
    ws.write_merge(8, 9, rownum+length, rownum+length, datadict['bzjianjh'], style1)
    ws.write_merge(8, 9, rownum+length+1, rownum+length+1, datadict['bzjiansj'], style1)
    ws.write_merge(8, 9, rownum+length+2, rownum+length+3, datadict['jiandc'], style1)

    ws.col(rownum+length).width = 256 * 12
    ws.col(rownum+length+1).width = 256 * 12
    ws.col(rownum+length+2).width = 256 * 12*2
    ws.col(rownum+length+3).width = 256 * 12*2

    ws.write_merge(10, 21, rownum+length, rownum+length+3, '', style1)
    ws.insert_bitmap(img1bmp, 10, rownum+length, 21, rownum+length+3, scale_x=1, scale_y=1)
    ws.write_merge(22, 30, rownum+length, rownum+length+3, '', style1)
    ws.insert_bitmap(img2bmp, 22, rownum+length, 30, rownum+length+3, scale_x=1, scale_y=1)

    wb.save(response)
    return response

@login_required
@csrf_exempt
def getExcelByData(request):
    data = request.read()
    if data:
        data = json.loads(data)
    else:
        raise Http404()

    response = HttpResponse(mimetype=u'application/ms-excel')
    excelname = data.get('excelname','')
    sheetname = data.get('sheetname','')

    filename = u'%s.xls'%urllib.quote(excelname.encode('utf-8'))
    if hasattr(request,'META') and request.META.has_key('HTTP_USER_AGENT'):
        if request.META['HTTP_USER_AGENT'].find("Firefox")!=-1:
            filename = u'%s.xls'%excelname

    response['Content-Disposition'] = ('attachment;filename=%s' % filename).encode('utf-8')


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

    wb = xlwt.Workbook()
    ws = wb.add_sheet(u"%s"%sheetname, cell_overwrite_ok=True)
    rownum = 0
    for i,index in enumerate(data.get('index',[])):
        ws.write_merge(rownum, rownum, i, i, data.get('head',{}).get(index,""), style0)
        ws.col(i).width = 256 * 17
    rownum+=1
    for row,d in enumerate(data.get('data',[])):
        for i,index in enumerate(data.get('index',[])):
            ws.write_merge(rownum+row, rownum+row, i, i, d.get(index,""), style1)
    rownum+=1
    wb.save(response)
    return response

@login_required
@csrf_exempt
def getExcelByGroupData(request):
    data = request.read()
    if data:
        data = json.loads(data)
    else:
        raise Http404()

    response = HttpResponse(mimetype=u'application/ms-excel')
    excelname = data.get('excelname','')
    sheetname = data.get('sheetname','')

    filename = u'%s.xls'%urllib.quote(excelname.encode('utf-8'))
    if hasattr(request,'META') and request.META.has_key('HTTP_USER_AGENT'):
        if request.META['HTTP_USER_AGENT'].find("Firefox")!=-1:
            filename = u'%s.xls'%excelname

    response['Content-Disposition'] = ('attachment;filename=%s' % filename).encode('utf-8')


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

    wb = xlwt.Workbook()
    ws = wb.add_sheet(u"%s"%sheetname, cell_overwrite_ok=True)
    rownum = 0
    for i,head in enumerate(data.get('head',[])):
        ws.write_merge(rownum+head.get('top',0), rownum+head.get('height',0)+head.get('top',0), head.get('left',0), head.get('left',0)+head.get('width',0), head.get('text',''), style0)
        ws.col(i).width = 256 * 17
    rownum+=3
    for row,d in enumerate(data.get('data',[])):
        for i,index in enumerate(data.get('index',[])):
            ws.write_merge(rownum+row, rownum+row, i, i, d.get(index,""), style1)
        rownum+=1
    wb.save(response)
    return response

