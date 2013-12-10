#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

__author__ = u'王健'


@login_required
def downloadTrue(request):
    response = HttpResponse(mimetype=u'application/ms-excel')
    excelname = request.POST.get('excelname','')
    filename = u'订单执行情况汇总表-%s.xls'%excelname
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
    ws = wb.add_sheet(u"订单执行情况汇总表", cell_overwrite_ok=True)
    rownum = 0
    ws.write_merge(rownum, rownum, 0, 0, u'手机号', style1)
    ws.write_merge(rownum, rownum, 1, 1, u'姓名', style1)
    ws.write_merge(rownum, rownum, 2, 2, u'身份证号', style1)
    ws.write_merge(rownum, rownum, 3, 3, u'地址', style1)
    ws.write_merge(rownum, rownum, 4, 4, u'错误原因', style1)

    rownum += 1
    for o in Truename.objects.filter(status=2).order_by('datetime'):
        ws.write_merge(rownum, rownum, 0, 0, o.tel, style1)
        ws.write_merge(rownum, rownum, 1, 1,o.name , style1)
        ws.write_merge(rownum, rownum, 2, 2,o.number, style1)
        ws.write_merge(rownum, rownum, 3, 3, o.address, style1)
        ws.write_merge(rownum, rownum, 4, 4, o.help, style1)

        rownum += 1
    for i in range(5):
        ws.col(i).width = 256 * 20
    wb.save(response)
    return response