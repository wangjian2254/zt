from zt.ztmanage.models import   Ztperm,Scx,Code,ProductSite,OrderList,OrderBB, OrderNo, OrderBBNo, OrderBBLock, OrderGenZong

__author__ = 'WangJian'

from django.contrib import admin

#admin.site.register(List)
#admin.site.register(Item)


admin.site.register(Ztperm)
admin.site.register(Scx)
admin.site.register(Code)
admin.site.register(ProductSite)
admin.site.register(OrderNo)
admin.site.register(OrderList)
admin.site.register(OrderBBNo)
admin.site.register(OrderBBLock)
admin.site.register(OrderBB)
admin.site.register(OrderGenZong)
#admin.site.register(AutoComplete)
