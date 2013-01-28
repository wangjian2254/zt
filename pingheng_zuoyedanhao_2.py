#coding=utf-8
import MySQLdb

__author__ = '王健'
orderidstr='5989,6794,6795,6792,6790,6791,6798,279,279,12014,4843,4721,4722,5842,5202,9752,9751,697,3533,3537,3537,154,156,2722,812,8738,6430,2531,2531,2537,2537,5384,5387,791,791,4974,2886,2889,5800,2705,4881,4887,3471,3471,6415,5010,5011,4417,911,911,910,910,1444,1444,2005,2005,2005,5824,5827,854,855,5223,5225,1306,1300,1309,1309,4432,10126,5594,5200,5200,1320,1321,1325,11853,11853,11855,1667,2822,2822,5417,3382,339,2010,2010,4865,5008,450,4467,4461,2461,2463,1420,4868,5551,5880,4801,2073,4395,4395,4397,1363,1999,1999,5530,6570,6571,6577,3837,6653,2052,13190,2422,2422,2427,2427,1909,1909,6517,6169,4510,4511,4516,5209,4474,431,431,4981,4983,4982,2150,4984,4987,4986,4989,4988,3241,5498,5491,4375,8664,6645,2397,4963,5129,5915,5913,4940,4943,2117,666,4122,4127,4125,4124,5689,5689,5689,888,888,2589,2589,4336,4331,3131,5186,2354,2354,3739,3739,3739,4693,2131,4805,649,4480,2489,703,703,5312,5317,4714,4710,2339,2339,4718,4679,4676,4903,4905,4671,4671,2481,2481,124,6825,6825,8745,8743,8742,8740,4241,2673,2673,3176,3176,4684,4685,4737,2318,2318,1757,1757,1757,685,681,2699,4759,4754,4757,4757,168,6195,5606,5181,4772,5816,4889,147,2710,4405,4402,13,6407,6407,2522,2522,5394,5398,2893,1452,1452,4690,4920,4794,4794,4695,5835,2130,2130,4696,5839,4699,4899,4890,4890,4897,4896,4895,9721,9729,845,845,3464,3464,3462,5003,5002,5001,5000,5007,5006,5005,5004,5009,1453,1453,903,903,4420,1696,2287,4820,186,187,187,2024,1315,2564,2564,5022,3092,3092,3092,3092,1676,4498,306,4416,6614,4412,5402,5408,5544,5544,5899,4915,328,6139,6137,4875,4874,4877,4871,4873,4878,2065,2065,3184,2477,4485,12153,9647,1982,1982,1983,2816,2816,1186,5426,5422,5526,5527,42,6541,6541,6540,6154,4520,2046,4810,4385,4384,1374,2452,2452,4985,5191,2879,3358,5503,541,366,901,901,5291,1394,1394,1394,1391,4715,2334,2334,4711,4713,2438,2438,2435,4719,4996,4997,4994,4995,4992,4993,4990,4991,4998,4999,3251,3332,3338,3338,528,6501,4673,4673,4907,5920,5923,1002,1002,1001,1001,4348,4348,4494,4492,1822,1822,2419,2419,4975,4977,2149,2149,4973,4220,5486,5482,630,6524,5904,2385,2385,2386,1276,2594,2594,1043,1043,4707,4706,6675,4709,4708,2367,2367,2362,2362,4933,4682,4683,4680,4688,4689,2497,2497,6028,712,712,5303,1358,3709,3709,1881,1881,4916,4917,4917,4661,4910,4911,5174,5178,6581,6009,2930,2930,4703,4701,4700,2494,119,1742,1568'
idlist=[]
for id in orderidstr.split(','):
    idlist.append(int(id))
db20130120=MySQLdb.connect(host="69.16.97.123",user="root",passwd="123456",db="zt20130120",charset='utf8')
c=db20130120.cursor()
c.execute('select * from ztmanage_orderbb order by id asc')
rows=c.fetchall()
perrow=None
num=0
rnum=0
for row in rows:
    if perrow:
        b=True
        for i,v in enumerate(row):
            if i==0:
                continue
            if v!=perrow[i]:
                b=False
        if b:
            if row[2] in idlist or row[6] in idlist:
                rnum+=1
                print '------'
            else:
                print ''
            print 'id:%s lsh_id:%s yorder_id:%s yzydh:%s ywz_id:%s ywznum:%s zrorder_id:%s  zrwz_id:%s zrwznum:%s bfnum:%s ysnum:%s bztext:%s'%(perrow[0],perrow[1],perrow[2],perrow[3],perrow[4],perrow[5],perrow[6],perrow[7],perrow[8],perrow[9],perrow[10],perrow[12])
            print 'id:%s lsh_id:%s yorder_id:%s yzydh:%s ywz_id:%s ywznum:%s zrorder_id:%s  zrwz_id:%s zrwznum:%s bfnum:%s ysnum:%s bztext:%s'%(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[12])
            print '\n'
            num+=1
        perrow=row
    else:
        perrow=row
print num
print rnum

#13078 24号前的最后一个 日报表