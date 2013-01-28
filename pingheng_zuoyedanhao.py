#coding=utf-8
#author:u'王健'
#Date: 13-1-20
#Time: 下午1:18
__author__ = u'王健'


import MySQLdb

db1=MySQLdb.connect(host="69.16.97.123",user="root",passwd="123456",db="zt24-1",charset='utf8')
db2=MySQLdb.connect(host="69.16.97.123",user="root",passwd="123456",db="zt24-2",charset='utf8')
db20130120=MySQLdb.connect(host="69.16.97.123",user="root",passwd="123456",db="zt20130120",charset='utf8')

c1=db1.cursor()
c2=db2.cursor()
c3=db20130120.cursor()


sql='select id,date,order_id,wz_id,ywznum,zcnum,bfnum,ysnum,is_last from ztmanage_ordergenzong order by id asc'
c1.execute(sql)
rows1=c1.fetchall()
c1.close()

c2.execute(sql)
rows2=c2.fetchall()
c2.close()
lsh_id=58570
c3.execute('insert into ztmanage_orderbbno (id,lsh,user_id) values (%s,%s,%s)',(lsh_id,'20120824-001-0000',1))
print 'zt24-1 :%s(rows); zt24-2 :%s(rows)\n'%(len(rows1),len(rows2))
rowdict={}
valueslist=[]

changeRow=[]
for row in rows1:
    rowdict[str(row[0])]=row
if len(rows2)>=len(rows1):
    num=0
    for i,row2 in enumerate(rows2):
        row1=rowdict.get(str(row2[0]))
        if row1:
            if row1[7]!=row2[7]:
                #print 'insert into ztmanage_orderbb (lsh_id,yorder_id,yzydh,ywz_id,ywznum,zrorder_id,zrwznum,bfnum,ysnum,ywzsynum,bztext) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'%(lsh_id,row2[2],'20120824号平衡数据（程序录入）',row2[3],0,row2[3],row2[7]-row1[7],0,0,0,'程序录入，不可删除')
                #print 'id%s: zt24-1(%s)_zt24-2(%s):%s\n'%(row2[0],row1[7],row2[7],row2[7]-row1[7])

                c3.execute('select id from ztmanage_orderlist where id=%s'%(row2[2]))
                result=c3.fetchone()
                if not result:
                    print row2[2]
                else:
                    valueslist.append((lsh_id,row2[2],'20120824号平衡数据（程序录入）',row2[2],row2[3],row2[7]-row1[7],0,0,0,'程序录入，不可删除'))
                    num+=1
                    changeRow.append((row2[2],row2[3]))

                #print '1:  id:%s ;date:%s ;order_id:%s ;wz_id:%s ;ywznum:% s;zcnum:%s ;bfnum:%s ;ysnum:%s ;is_last:%s ;\n'%(row1[0],row1[1],row1[2],row1[3],row1[4],row1[5],row1[6],row1[7],row1[8])
                #print '2:  id:%s ;date:%s ;order_id:%s ;wz_id:%s ;ywznum:% s;zcnum:%s ;bfnum:%s ;ysnum:%s ;is_last:%s ;\n'%(row2[0],row2[1],row2[2],row2[3],row2[4],row2[5],row2[6],row2[7],row2[8])
                #print '----------'
        else:
            print 'id:%s ;date:%s ;order_id:%s ;wz_id:%s ;ywznum:% s;zcnum:%s ;bfnum:%s ;ysnum:%s ;is_last:%s ;\n'%(row2[0],row2[1],row2[2],row2[3],row2[4],row2[5],row2[6],row2[7],row2[8])
    print num
#    c3.executemany(
#            """insert into ztmanage_orderbb (lsh_id,yorder_id,yzydh,zrorder_id,zrwz_id,zrwznum,bfnum,ysnum,ywzsynum,bztext) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#            """,valueslist
#        )
#    db20130120.commit()
    print 'success'
else:
    print 'error'
print ''
print ''
print ''
print len(changeRow)
changeRow=set(changeRow)
print len(changeRow)
for orderlistid,wzid in changeRow:
    print '(%s,%s),'%(orderlistid,wzid),
print ''



