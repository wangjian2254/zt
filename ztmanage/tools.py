#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
from ztmanage.models import OrderBBNo, PlanNo

__author__ = u'王健'

def getResult(result,success=True,message=None):
    return {'result':result,'success':success,'message':message}

def newLSHNoByUser(user):
    '''
    根据用户，生成流水号
    '''
    date=datetime.datetime.now().strftime("%Y%m%d")

#    lastNo=OrderBBNo.objects.filter(lsh__startswith=date,user=user).delete()
#    lastNo=[]
    lastNo=OrderBBNo.objects.filter(lsh__startswith=date,user=user).order_by('-lsh')[:1]
    if len(lastNo)>0:
        lsh=lastNo[0].lsh.split('-')[2]
        lsh=int(lsh)
        lsh+=1
        lsh=lastNo[0].lsh.split('-')[0]+'-'+lastNo[0].lsh.split('-')[1]+'-'+('0000'+str(lsh))[-4:]
        return lsh
    else:
        return date+'-'+('000'+str(user.pk))[-3:]+'-'+'0000'[-4:]


def newPlanLSHNoByUser(user):
    '''
    根据用户，生成流水号
    '''
    date=datetime.datetime.now().strftime("%Y%m%d")

    lastNo=PlanNo.objects.filter(lsh__startswith=date+'-'+('000'+str(user.pk))[-3:]+'-').order_by('-lsh')[:1]
    if len(lastNo)>0:
        lsh=lastNo[0].lsh.split('-')[2]
        lsh=int(lsh)
        lsh+=1
        lsh=lastNo[0].lsh.split('-')[0]+'-'+lastNo[0].lsh.split('-')[1]+'-'+('0000'+str(lsh))[-4:]
        return lsh
    else:
        return date+'-'+('000'+str(user.pk))[-3:]+'-'+'0000'[-4:]