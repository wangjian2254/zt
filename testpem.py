#coding=utf-8
#author:u'王健'
#Date: 12-7-4
#Time: 下午10:40
__author__ = u'王健'


def permission_required(function,code):
    print function
    print code

@permission_required('123','abc')
def login(request,ddbh):
    print  request
    print ddbh

login('1','2')



  