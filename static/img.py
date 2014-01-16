#coding=utf-8
from PIL import Image
import time,datetime
import os
p=os.path.join(os.path.dirname(__file__), 'excel').replace('\\','/')
l=[]

for n in os.listdir(p):
    info = os.stat(p+'\\'+n)
    ctime = time.localtime(info.st_ctime)
    date = datetime.datetime(*ctime[:3])
    datestr = date.strftime('%Y%m%d')
    #print datestr
    if datestr < datetime.datetime.now().strftime('%Y%m%d'):
        os.remove(p+'\\'+n)
     #   print n
        continue
    if n.find('.xls')>=0:
        continue
    if n.find('.png')>0 or n.find('.bmp')>0:
        na=n[:n.find('.')]
        if na in l:
            l.remove(na)
        else:
            l.append(na)

for n in l:
    #print n
    if os.path.isfile(p+'\\'+n+'.png'):
        Image.open(p+'\\'+n+'.png').convert("RGB").save(p+'\\'+n+'.bmp')
        

        
    
        
    
    
