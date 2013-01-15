#coding=utf-8
#author:u'王健'
#Date: 12-8-11
#Time: 上午1:34
__author__ = u'王健'




import sys, urllib
url = "http://127.0.0.1/zt/auto"
#网页地址
wp = urllib.urlopen(url)
#打开连接
content = wp.read()