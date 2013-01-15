#coding=utf-8
#author:u'王健'
#Date: 12-8-16
#Time: 下午9:28
__author__ = u'王健'


import xlrd
import MySQLdb


def getXCL():
    fname = "zzb.xls"
    bk = xlrd.open_workbook(fname)
    sh=bk.sheet_by_name(bk.sheet_names()[-1])
    return sh

def compere(row,row2,c):
    change=True
    for i in range(2,8):
        if row[i]!=row2[i]:
            change=False
    if change:

        c.execute('select * from ztmanage_orderbb where ywz_id=%s and yorder_id=%s '%(row[3],row[2]))
#        c.execute('select id,lsh_id,yorder,yzydh,ywz,ywznum,zrorder,zrwz,zrwznum,bfnum,ysnum from ztmanage_orderbb where ywz_id=%s and yorder_id=%s '%(row[3],row[2]))
        rows=c.fetchall()
        c.execute('select * from ztmanage_orderbb where zrwz_id=%s and zrorder_id=%s '%(row[3],row[2]))
        rows2=c.fetchall()
        if len(rows)>0 or len(rows2)>0:
            c.execute('select id,date,order_id,wz_id,ywznum,zcnum,bfnum,ysnum,is_last from ztmanage_ordergenzong where id in(%s,%s) order by id'%(row[0],row2[0]))
            genzong=c.fetchall()
            print 'genzong',genzong[0]
            print '***************'
            c.execute('select * from ztmanage_orderbb where ywz_id=%s and yorder_id=%s '%(row[3],row[2]))
            rows=c.fetchall()
            print 'orderbb',rows
            print '---------------'
            c.execute('select * from ztmanage_orderbb where zrwz_id=%s and zrorder_id=%s '%(row[3],row[2]))
            rows2=c.fetchall()
            print 'orderbb',rows2
            print '++++++++++++++'
            print 'genzong',genzong[1]
            print '///////////////'
            print '开始!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            #print ',',row[0],',',row2[0],
    pass
def tiaozheng():
    datestr='20120810'
    db=MySQLdb.connect(host="192.168.1.105",user="root",passwd="123456",db="zt1",charset='utf8')
    c=db.cursor()
#    num2=c.execute('select id from ztmanage_ordergenzong ')
#    print num2
#    num1=c.execute('select id from ztmanage_ordergenzong where date in ("20120811","20120812","20120813","20120814","20120815","20120816","20120817")')
#    print num1
##    num=c.execute('delete  from ztmanage_ordergenzong where date in ("20120811","20120812","20120813","20120814","20120815","20120816","20120817")')
##    print num
##    num=c.execute('delete  from ztmanage_orderbb where id in (689,691,697,1673,1838,1839,1840,2072,2073,2142,2143,2144,2149,2150,2151,2190,2193,2212,2349,2352,2382)')
##    print num
#    num3=c.execute('select id from ztmanage_orderbb where id in (689,691,697,1673,1838,1839,1840,2072,2073,2142,2143,2144,2149,2150,2151,2190,2193,2212,2349,2352,2382) ')
#    print num3
#    count=c.fetchone()
#    db.commit()
#    return
#    c.execute('select id,code from ztmanage_code where scx_id=2')
#    codes=c.fetchall()
#    codeids=[]
#    for code in codes:
#        codeids.append(str(code[0]))
#    codearr=','.join(codeids)
##    print codearr
##    c.execute('select id from ztmanage_orderlist where code_id in ('+codearr+')')
#    c.execute('select id from ztmanage_orderno where ddbh="ZCG1232001"')
#    ddbhs=c.fetchall()
#    ddbhids=[]
#    for ddbh in ddbhs:
#        ddbhids.append(str(ddbh[0]))
#    ddbharr=','.join(ddbhids)
#    print codearr
#    c.execute('select id from ztmanage_orderlist where code_id in ('+codearr+')')
#    orderlists=c.fetchall()
#    orderlistids=[]
#    for l in orderlists:
#        orderlistids.append(str(l[0]))
#    print len(orderlistids)
#    orderlistarr=','.join(orderlistids)
#    print orderlistarr
#    num5=c.execute('select id  from ztmanage_ordergenzong where order_id in ('+orderlistarr+')')
#    print num5
#    db.commit()
#    return
    c.execute('select id,date,order_id,wz_id,ywznum,zcnum,bfnum,ysnum,is_last from ztmanage_ordergenzong order by id')
    rows=c.fetchall()
    rowmap={}
    for row in rows:
        if not rowmap.has_key(str(row[2])+'r'+str(row[3])):
            rowmap[str(row[2])+'r'+str(row[3])]=[]
        rowmap[str(row[2])+'r'+str(row[3])].append(row)
    for k in rowmap.keys():
        if len(rowmap[k])!=1:
            for i in range(1,len(rowmap[k])):
                compere(rowmap[k][i-1],rowmap[k][i],c)

def getChongFu():

    sql='select * from ztmanage_ordergenzong where id in (8740 , 28793 , 7786 , 28774 , 1869 , 28520 , 7809 , 28772 , 7100 , 29161 , 7677 , 28773 , 7021 , 29160 , 24107 , 27948 , 1019 , 28485 , 7209 , 29157 , 2075 , 28523 , 8807 , 28791 , 10672 , 28805 , 4154 , 28447 , 1900 , 28521 , 10434 , 28804 , 1904 , 28524 , 6313 , 28351 , 3739 , 28537 , 6237 , 28354 , 10351 , 28802 , 1979 , 28522 , 8758 , 28794 , 4178 , 28711 , 1884 , 28519 , 7343 , 29150 , 9203 , 28792 , 10439 , 28803 , 7619 , 28769 , 10229 , 28453 , 301 , 27949 , 9077 , 28787 , 9215 , 28790 , 6240 , 28353 , 10396 , 28806 , 7735 , 28771 , 7532 , 29149 , 10640 , 28807 , 240 , 28965 , 8724 , 28786 , 9181 , 28788 , 6349 , 28350 , 6348 , 28352 , 562 , 28492 , 7685 , 28770 , 6496 , 28745 , 9019 , 28789 , 4851 , 28441 , 7703 , 28768 , 7498 , 29152 , 4484 , 28440) order by order_id asc,date asc'
    db=MySQLdb.connect(host="192.168.1.105",user="root",passwd="123456",db="zt1",charset='utf8')
    c=db.cursor()

    c.execute(sql)
    rows=c.fetchall()

    for row in rows:
        print row


if __name__=="__main__":
    tiaozheng()
#    getChongFu()

