#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28

__author__ = u'王健'

class CompluteError(Exception):
    pass
class CompluteNumError(Exception):
    def __init__(self,order,wz):
        self.order=order
        self.wz=wz

