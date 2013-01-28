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

def tiaozheng():
    datestr='20120810'
    db=MySQLdb.connect(host="192.168.1.105",user="root",passwd="123456",db="zt1",charset='utf8')
    c=db.cursor()
    sh=getXCL()
    row_data=sh.row_values(2,9)
    type='1'
    l=[]
    siteid=1
    siteidmap={}
    value=[]
    for i,d in enumerate(row_data):
        if d==u'前序合计':
            type='1'
        if d==u'后序合计':
            type='2'
        if d and d!=u'前序合计' and d!=u'后序合计':
            l.append((type,d.split('-')[0],i+9,siteid))
            value.append((siteid,d.split('-')[0],type))
#            siteidmap[d.split('-')[0]]=siteid
            siteid+=1
            print d.split('-')[0]
    l.append(('3',u'扫描出库',i+9,siteid))
    value.append((siteid,u'扫描出库','3'))
    siteidmap[u'扫描出库']=siteid
    fname = "tiaozheng.xls"
    bk = xlrd.open_workbook(fname)
    sh=bk.sheet_by_name(bk.sheet_names()[0])

    nrows=sh.nrows
    scx=[]
    scxmap={}
    code=[]
    codemap={}
    order=set()
    orderlist={}
    ordergenzong={}
    scxid=1
    scxvalue=[]
    codeid=1
    codeidmap={}
    codevalue=[]
    orderid=1
    orderidmap={}
    ordervalue=[]
    orderlistid=1
    orderlistidmap={}
    orderlistvalue=[]
    ordergenzongid=1
    ordergenzongidmap={}
    ordergenzongvalue=[]
    orderlistset=set()
    c.execute('select id from ztmanage_ordergenzong order by id desc')
    rows=c.fetchone()
    ordergenzongid=rows[0]
    ordergenzongid+=1
    for i in range(0,3):
        row_data = sh.row_values(i,0)
#        if row_data[0].strip() not in scx:
#            scx.append(row_data[0].strip())
#            scxvalue.append((scxid,row_data[0].strip()))
#            scxmap[row_data[0].strip()]=scxid
#            scxid+=1

#        if row_data[2].strip().upper() and not codemap.has_key(row_data[2].strip().upper()):
#            if row_data[3].strip():
#                if row_data[4] is not unicode:
#                    row_data[4]=unicode(row_data[4])
#                codemap[row_data[2].strip().upper()]=(row_data[0].strip(),row_data[3].strip(),row_data[4].strip())
#                code.append(row_data[2].strip().upper())
#                codevalue.append((codeid,scxmap[row_data[0].strip()],row_data[2].strip().upper(),row_data[3].strip().upper(),row_data[4].strip().upper(),0))
        c.execute('select id from ztmanage_code where code="%s"'%(row_data[2].strip().upper(),))
        rows=c.fetchone()

        codeid=rows[0]
                #continue
#                codeid+=1
#            else:
#                continue


#        if row_data[1].strip() and not orderidmap.has_key(row_data[1].strip().upper()):
        c.execute('select id from ztmanage_orderno where ddbh="%s"'%(row_data[1].strip().upper(),))
        rows=c.fetchone()
        ddbhid=rows[0]
        if not ddbhid or not codeid:
            print row_data
            continue

        c.execute('select id from ztmanage_orderlist where ddbh_id=%s and code_id=%s'%(ddbhid,codeid))
        rows=c.fetchone()
        orderlistitemid=rows[0]

#        print 'delete from ztmanage_orderbb where yorder_id=%s'%(orderlistitemid,)
#        n=c.execute('delete from ztmanage_orderbb where yorder_id=%s'%(orderlistitemid,))
#        print n
#        print 'delete from ztmanage_orderbb where zrorder_id=%s'%(orderlistitemid,)
#        n=c.execute('delete from ztmanage_orderbb where zrorder_id=%s'%(orderlistitemid,))
#        print n
#        print 'delete from ztmanage_ordergenzong where order_id=%s'%(orderlistitemid,)
#        n=c.execute('delete from ztmanage_ordergenzong where order_id=%s'%(orderlistitemid,))
#        print n


#        is_last=sh.cell_value(i,7)
#        is_open=1
#        if is_last==1:
#            is_open=0
#        if orderlist.has_key(row_data[1].strip().upper()):
#            if row_data[1].strip().upper()+'l'+row_data[2].strip().upper() not in orderlistset:
#                orderlist[row_data[1].strip().upper()].append((row_data[2].strip().upper(),row_data[5] or 0))
#                if is_open:
#                    orderlistvalue.append((orderlistid,orderidmap[row_data[1].strip().upper()],codeidmap[row_data[2].strip().upper()],row_data[5] or 0,0,0,'2012-07-05','',is_open))
#                else:
#                    orderlistvalue.append((orderlistid,orderidmap[row_data[1].strip().upper()],codeidmap[row_data[2].strip().upper()],row_data[5] or 0,0,0,'2012-07-05','2012-07-05',is_open))
#                orderlistidmap[row_data[1].strip().upper()+'c'+row_data[2].strip().upper()]=orderlistid
#                orderlistid+=1
#                orderlistset.add(row_data[1].strip().upper()+'l'+row_data[2].strip().upper())
#            else:
#                continue
#        else:
#            orderlist[row_data[1].strip()]=[(row_data[2].strip().upper(),row_data[5] or 0)]
#            if is_open:
#                orderlistvalue.append((orderlistid,orderidmap[row_data[1].strip().upper()],codeidmap[row_data[2].strip().upper()],row_data[5] or 0,0,0,'2012-07-05','',is_open))
#            else:
#                orderlistvalue.append((orderlistid,orderidmap[row_data[1].strip().upper()],codeidmap[row_data[2].strip().upper()],row_data[5] or 0,0,0,'2012-07-05','2012-07-05',is_open))
#            orderlistidmap[row_data[1].strip().upper()+'c'+row_data[2].strip().upper()]=orderlistid
#            orderlistid+=1
#            orderlistset.add(row_data[1].strip().upper()+'l'+row_data[2].strip().upper())
        for k,site in enumerate(l):
            blank=False
            jr=sh.cell_value(i,site[2]+0) or 0
            if jr:
                blank=True
            if k!=len(l)-1:
                zc=sh.cell_value(i,site[2]+1) or 0
                if zc:
                    blank=True
                bf=sh.cell_value(i,site[2]+2) or 0
                if bf:
                    blank=True
                ys=sh.cell_value(i,site[2]+3) or 0
                if ys:
                    blank=True
            if blank:
                if k!=len(l)-1:
                    jr=int(jr)
                    zc=int(zc)
                    bf=int(bf)
                    ys=int(ys)
                    if jr-zc-bf-ys>=0:
#                    ordergenzong[row_data[1].strip().upper()+'g'+row_data[2].strip().upper()+'s'+site[1]]=(jr,zc,bf,ys)
                        ordergenzongvalue.append((ordergenzongid,datestr,orderlistitemid,site[3],jr,zc,bf,ys,0))
                        ordergenzongid+=1
                    else:
                        print jr,zc,bf,ys
                else:
                    jr=int(jr)
                    zc=int(zc)
                    bf=int(bf)
                    ys=int(ys)
                    if jr-zc-bf-ys>=0:
#                    ordergenzong[row_data[1].strip().upper()+'g'+row_data[2].strip().upper()+'s'+site[1]]=(jr,0,0,0)
                        ordergenzongvalue.append((ordergenzongid,datestr,orderlistitemid,site[3],jr,0,0,0,0))
                        ordergenzongid+=1

    for item in ordergenzongvalue:
        print "insert into ztmanage_ordergenzong (id,date,order_id,wz_id,ywznum,zcnum,bfnum,ysnum,is_last) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"%item

#    c.executemany(
#        """insert into ztmanage_ordergenzong (id,date,order_id,wz_id,ywznum,zcnum,bfnum,ysnum,is_last) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
#        """,ordergenzongvalue[:10]
#    )
#
#    c.executemany(
#        """insert into ztmanage_ordergenzong (id,date,order_id,wz_id,ywznum,zcnum,bfnum,ysnum,is_last) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
#        """,ordergenzongvalue[10:]
#    )
#    db.commit()


if __name__=="__main__":
    tiaozheng()

