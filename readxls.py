#coding=utf-8
#author:u'王健'
#Date: 12-7-4
#Time: 下午8:42
__author__ = u'王健'




import xlrd
import MySQLdb
 
#fname = "zzb.xls"
#bk = xlrd.open_workbook(fname)
##shxrange = range(bk.nsheets)
#try:
##    sh = bk.sheet_by_name("Sheet1")
#    for n in bk.sheet_names():
#        print '%s'%(n,)
#    sh=bk.sheet_by_name(bk.sheet_names()[-1])
#except:
#    print "no sheet in %s named Sheet1" % fname
##    return None
#nrows = sh.nrows
#ncols = sh.ncols
#print "nrows %d, ncols %d" % (nrows,ncols)
#
#cell_value = sh.cell_value(1,1)
#print cell_value
#
#row_list = []
#scx=[]
#code=[]
#codemap={}
#for i in range(4,nrows):
#    row_data = sh.row_values(i,0,5)
#
#    if row_data[0] not in scx:
#        scx.append(row_data[0])
#    if row_data[2].upper() not in code:
#        code.append(row_data[2].upper())
#    if not codemap.has_key(row_data[2].upper()):
#        if row_data[3] and row_data[4]:
#            codemap[row_data[2].upper()]=(row_data[0],row_data[3],row_data[4])
#
#for s in scx:
#    print s
#codenomap=[]
#for s in code:
#    if codemap.has_key(s):
#        print '%s:%s---%s---%s'%(s,codemap[s][1],codemap[s][2],codemap[s][0])
#    else:
#        codenomap.append(s)
#for s in codenomap:
#    print s
#print '%s:%d----%s:%d----%s:%d----%s:%d'%('生产线',len(scx),'物料',len(code),'物料信息',len(codemap.keys()),'没有信息的物料',len(code)-len(codemap.keys()))

#    print row_data[0]

#    row_list.append(row_data)
def getXCL():
    fname = "zzb.xls"
    bk = xlrd.open_workbook(fname)
    sh=bk.sheet_by_name(bk.sheet_names()[-1])
    return sh
def importSCX():
    sh=getXCL()



def importCode():
    datestr='20120706'
    db=MySQLdb.connect(host="192.168.1.105",user="root",passwd="123456",db="zt1",charset='utf8')
    c=db.cursor()
#    c.executemany(
#      """INSERT INTO breakfast (name, spam, eggs, sausage, price)
#      VALUES (%s, %s, %s, %s, %s)""",
#      [
#      ("Spam and Sausage Lover's Plate", 5, 1, 8, 7.95 ),
#      ("Not So Much Spam Plate", 3, 2, 0, 3.95 ),
#      ("Don't Wany ANY SPAM! Plate", 0, 4, 3, 5.95 )
#      ] )
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

    for i in range(4,nrows):
        row_data = sh.row_values(i,0)
        if row_data[0].strip() not in scx:
            scx.append(row_data[0].strip())
            scxvalue.append((scxid,row_data[0].strip()))
            scxmap[row_data[0].strip()]=scxid
            scxid+=1

        if row_data[2].strip().upper() and not codemap.has_key(row_data[2].strip().upper()):
            if row_data[3].strip():
                if row_data[4] is not unicode:
                    row_data[4]=unicode(row_data[4])
                codemap[row_data[2].strip().upper()]=(row_data[0].strip(),row_data[3].strip(),row_data[4].strip())
                code.append(row_data[2].strip().upper())
                codevalue.append((codeid,scxmap[row_data[0].strip()],row_data[2].strip().upper(),row_data[3].strip().upper(),row_data[4].strip().upper(),0))
                codeidmap[row_data[2].strip().upper()]=codeid
                codeid+=1
            else:
                continue


        if row_data[1].strip() and row_data[1].strip().upper() not in order:
            order.add(row_data[1].strip().upper())
            ordervalue.append((orderid,row_data[1].strip().upper(),''))
            orderidmap[row_data[1].strip().upper()]=orderid
            orderid+=1
        is_last=sh.cell_value(i,7)
        is_open=1
        if is_last==1:
            is_open=0
        if orderlist.has_key(row_data[1].strip().upper()):
            if row_data[1].strip().upper()+'l'+row_data[2].strip().upper() not in orderlistset:
                orderlist[row_data[1].strip().upper()].append((row_data[2].strip().upper(),row_data[5] or 0))
                if is_open:
                    orderlistvalue.append((orderlistid,orderidmap[row_data[1].strip().upper()],codeidmap[row_data[2].strip().upper()],row_data[5] or 0,0,0,'2012-07-05','',is_open))
                else:
                    orderlistvalue.append((orderlistid,orderidmap[row_data[1].strip().upper()],codeidmap[row_data[2].strip().upper()],row_data[5] or 0,0,0,'2012-07-05','2012-07-05',is_open))
                orderlistidmap[row_data[1].strip().upper()+'c'+row_data[2].strip().upper()]=orderlistid
                orderlistid+=1
                orderlistset.add(row_data[1].strip().upper()+'l'+row_data[2].strip().upper())
            else:
                continue
        else:
            orderlist[row_data[1].strip()]=[(row_data[2].strip().upper(),row_data[5] or 0)]
            if is_open:
                orderlistvalue.append((orderlistid,orderidmap[row_data[1].strip().upper()],codeidmap[row_data[2].strip().upper()],row_data[5] or 0,0,0,'2012-07-05','',is_open))
            else:
                orderlistvalue.append((orderlistid,orderidmap[row_data[1].strip().upper()],codeidmap[row_data[2].strip().upper()],row_data[5] or 0,0,0,'2012-07-05','2012-07-05',is_open))
            orderlistidmap[row_data[1].strip().upper()+'c'+row_data[2].strip().upper()]=orderlistid
            orderlistid+=1
            orderlistset.add(row_data[1].strip().upper()+'l'+row_data[2].strip().upper())
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
                    ordergenzong[row_data[1].strip().upper()+'g'+row_data[2].strip().upper()+'s'+site[1]]=(jr,zc,bf,ys)
                    ordergenzongvalue.append((ordergenzongid,datestr,orderlistidmap[row_data[1].strip().upper()+'c'+row_data[2].strip().upper()],site[3],jr,zc,bf,ys,is_last))
                    ordergenzongid+=1
                else:
                    ordergenzong[row_data[1].strip().upper()+'g'+row_data[2].strip().upper()+'s'+site[1]]=(jr,0,0,0)
                    ordergenzongvalue.append((ordergenzongid,datestr,orderlistidmap[row_data[1].strip().upper()+'c'+row_data[2].strip().upper()],site[3],jr,0,0,0,is_last))
                    ordergenzongid+=1
#    for i in range(1,ordergenzongid):
#        if i not in orderlistidmap.values():
#            print i


    c.execute('delete from ztmanage_productsite')
    c.executemany(
        """insert into ztmanage_productsite (id,name,type) values (%s,%s,%s)
        """,value
    )
    c.execute('delete from ztmanage_scx')
    c.executemany(
        """insert into ztmanage_scx (id,name) values (%s,%s)
        """,scxvalue
    )
    c.execute('delete from ztmanage_code')
    c.executemany(
        """insert into ztmanage_code (id,scx_id,code,name,gg,dj) values (%s,%s,%s,%s,%s,%s)
        """,codevalue
    )
    c.execute('delete from ztmanage_orderno')
    c.executemany(
        """insert into ztmanage_orderno (id,ddbh,bzname) values (%s,%s,%s)
        """,ordervalue
    )
    c.execute('delete from ztmanage_orderlist')
    c.executemany(
        """insert into ztmanage_orderlist (id,ddbh_id,code_id,num,dj,cz,createDate,closeDate,is_open) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,orderlistvalue
    )
#    c.executemany(
#        """insert into ztmanage_orderlist (id,ddbh_id,code_id,num,dj,cz,createDate,is_open) values (%s,%s,%s,%s,%s,%s,%s,%s)
#        """,orderlistvalue[10:100]
#    )
#    c.executemany(
#        """insert into ztmanage_orderlist (id,ddbh_id,code_id,num,dj,cz,createDate,is_open) values (%s,%s,%s,%s,%s,%s,%s,%s)
#        """,orderlistvalue[100:1000]
#    )
#    c.executemany(
#        """insert into ztmanage_orderlist (id,ddbh_id,code_id,num,dj,cz,createDate,is_open) values (%s,%s,%s,%s,%s,%s,%s,%s)
#        """,orderlistvalue[1000:2000]
#    )
#    c.executemany(
#        """insert into ztmanage_orderlist (id,ddbh_id,code_id,num,dj,cz,createDate,is_open) values (%s,%s,%s,%s,%s,%s,%s,%s)
#        """,orderlistvalue[3000:4000]
#    )
#    c.executemany(
#        """insert into ztmanage_orderlist (id,ddbh_id,code_id,num,dj,cz,createDate,is_open) values (%s,%s,%s,%s,%s,%s,%s,%s)
#        """,orderlistvalue[5000:]
#    )
    c.execute('delete from ztmanage_ordergenzong')
    c.executemany(
        """insert into ztmanage_ordergenzong (id,date,order_id,wz_id,ywznum,zcnum,bfnum,ysnum,is_last) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,ordergenzongvalue
    )
    db.commit()




#    for i,s in enumerate(code):
#
#        if codemap.has_key(s):
#            print '%s:%s---%s---%s'%(s,codemap[s][1],codemap[s][2],codemap[s][0])
#    for k in orderlist.keys():
#        print k
#        print orderlist[k]
#    print len(order),len(orderlist.keys())
#    for k in ordergenzong.keys():
#        print k
#        print ordergenzong[k]
#        if i>100:
#            break

#    for i in range(10,22):

        
if __name__=="__main__":
#    importSCX()
    importCode()
#
#
#
#def importData():
#    db=_mysql.connect(host="localhost",user="root",passwd="123456",db="zt1")
#    c=db.cursor()
#    c.executemany(
#      """INSERT INTO breakfast (name, spam, eggs, sausage, price)
#      VALUES (%s, %s, %s, %s, %s)""",
#      [
#      ("Spam and Sausage Lover's Plate", 5, 1, 8, 7.95 ),
#      ("Not So Much Spam Plate", 3, 2, 0, 3.95 ),
#      ("Don't Wany ANY SPAM! Plate", 0, 4, 3, 5.95 )
#      ] )
    
