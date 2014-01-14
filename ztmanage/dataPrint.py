#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import urllib
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
import json
from django.views.decorators.csrf import  csrf_exempt
from zt import xlwt
from zt.xlwt import Font, Alignment
__author__ = u'王健'


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
    filename = '%s.xls'%urllib.quote(excelname.encode('utf-8'))
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
