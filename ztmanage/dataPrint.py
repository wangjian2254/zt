#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
import json
from django.views.decorators.csrf import  csrf_exempt

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
    filename = u'%s.xls'%excelname
    response['Content-Disposition'] = (u'attachment;filename=%s' % filename).encode('utf-8')
    import xlwt
    from xlwt import Font, Alignment

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
        ws.col(i).width = 256 * 15
    rownum+=1
    for row,d in enumerate(data.get('data',[])):
        for i,index in enumerate(data.get('index',[])):
            ws.write_merge(rownum+row, rownum+row, i, i, d.get(index,""), style1)
        rownum+=1
    wb.save(response)
    return response