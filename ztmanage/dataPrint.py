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

    data = request.POST.get('data','')
    data = json.loads(data)
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
    data = request.POST.get('data','')
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
    data = request.POST.get('data','')
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


imgstr='''/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkz
ODdASFxOQERXRTc4UG1RV19iZ2hnPk1xeXBkeFxlZ2MBERISGBUYLxoaL2NCOEJjY2NjY2NjY2Nj
Y2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY2NjY//AABEIANABkAMBEQACEQED
EQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAE
EQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZH
SElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1
tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAA
AAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGh
scEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlq
c3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV
1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/AO2lv7aG5W3kkIkOBwpIGeBkgYGe
2etC1B6EsdxFLNLEjhniwHA/hyMijpcPIloAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgA
oAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKACgAoAKAK1xfW1rIEmk2sRkDaTx+FY1
K9Om7SZpClOavFBb31tdSFIZNzAZI2kcfjRTr06jtFhOlOCvJFmtjMTI9aADNABQAtAGbd2t5Pfo
dkDWilW2+YVYsD1I2nOOwyOevsIGO03TnsZpSZvMR1XqoDFskkn1JzQtFb+uguty+QCMEZBoGRSx
RrE7KighSQQOlNMTRnJcOrq0krbActknpVSajFtkxu2kjURkdQyFWB5BFZppq6NGraMdgelMQYHp
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
Yr6AxyD6H0pNJ7jTa2KGkeH7fTXLj52PQntTEbFAC0AFABQAUAFABQAUAFABQAUAFADJuYX5x8p5
/CmtxMzYUUTJ+9Q/MOMH1+lW9iEatZmgUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUA
FABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFAEc/+ok/3T/K
mtxPYy4P9fH/ALw/nWj2IW5sVkaBQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFA
BQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAZ19A7apYTqZWVHYMo+6o2N
zj1zgZ/xoXX0/VB0Kuhxx/appYrea2UoF2SROpfB++7EYLH8eP0a2/r+vUT3/r+vQ2jyOuPekMil
RhE5MjMAp4OOf0poTKELqZkAjQfMOQTx+tW9iEaeD/eNZmgYP940AGD/AHjQAYP940AGD/eNABg/
3jQAYP8AeNABg/3jQAYP940AGD/eNABg/wB40AGD/eNABg/3jQAYP940AGD/AHjQAYP940AGD/eN
ABg/3jQAYP8AeNABg/3jQAYP940AGD/eNABg/wB40AGD/eNABg/3jQAYP940AGD/AHjQAYP940AG
D/eNABg/3jQAYP8AeNABg/3jQAYP940AGD/eNABg/wB40AGD/eNABg/3jQAYP940AGD/AHjQAYP9
40AKB7k0ALQAUAFABQAUAFABQBHP/qJP90/yprcT2MuD/Xx/7w/nWj2IW5sVkaBQAUAFABQAUAFA
BQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAF
ABQAUAFABQAUAFABQAUAMmJELkHBCn+VNbiZmwyyGZAZHILD+I+tW0rEJmrWZoFABQAUAFABQAUA
FABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAUAFABQAU
AFABQAUAFABQAUAZOnanNdX7wyKojIkKYRlxtfb948PkHOR0oWqv6fiD0djVJwM0ARSyK0TgBslS
OVIppCZQhjYTISU4YdHFW3oQkae4e/5VmaBuHv8AlQAbh7/lQAbh7/lQAbh7/lQAbh7/AJUAG4e/
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'''