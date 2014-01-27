#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from django.contrib.auth.models import User
from zt.ztmanage.flexview import getUser, userhaschange, saveUser, changeUserPassword, getAllUser, getUserById,  getOrderGenZongCache
from zt.ztmanage.flexview import getAllScx, getScxById, saveScx, getAllCode, saveCode, getCodeByCode, getCodeById, getAllProductSite, saveSite, delSite, openSite, getProductSiteById, getAllOrderNo, getOrderNoById, getOrderNoByBH, getOrderByBH, getAllOrderList, setOrderListClose, getOrderIsOpen, saveOrder, delOrder, getOrderByBHAndCode, getOrderAllBBNo, getOrderBBNoByUser, getOrderBBNoByDate, getOrderBBNoByDateQJ, getNewOrderBBNoByUser, delOrderBB, saveOrderBB, isOrderBBNoUnlock, getOrderBBByLsh, getOrderGenZongByDate, getOrderGenZongToday, getWriteExcel, getWriteExcel2, getOrderBBExcel, getCodeExcel, getOrderExcel, getZYOrderGenZongByOrderAndSite, getZYOrderGenZongByOrderAndSite2, getAllOpenProductSite
from zt.ztmanage.flexview2 import updatePlan, checkPlan, uncheckPlan,  queryPlan, changerecordPlan, queryPlanByUser, getPlanDetailByIdOrLsh, updatePlanUNDelete, updatePlanZYDH, getZYDHByOrderList, getZYDHByCode, queryPlanDetail, getAllPlanNo, queryPlanDaily, closePlanDetail, onlinePlanDetail, checkPlanDetail
from zt.ztmanage.flexview2 import changerecordPlanDelete, updatePlanDelete, getOrderRuningList, getOrderEndDate
from zt.ztmanage.models import OrderBBNo
from zt.ztmanage.flexview_view import queryPlanDetail2

__author__ = u'王健'
from pyamf.remoting.gateway.django import DjangoGateway
import pyamf

try:
    pyamf.register_class(User, 'django.contrib.auth.models.User')
    pyamf.register_class(OrderBBNo, 'zt.ztmanage.models.OrderBBNo')
except ValueError:
    print "Class already registered"

orderGateway = DjangoGateway({
    'service.getUser': getUser,
    'service.userhaschange': userhaschange,
    'service.saveUser': saveUser,
    'service.changeUserPassword': changeUserPassword,
    'service.getAllUser': getAllUser,
    'service.getUserById': getUserById,
    'service.getAllScx': getAllScx,
    'service.getScxById': getScxById,
    'service.saveScx': saveScx,
    #  'service.delScx': delScx,
    'service.getAllCode': getAllCode,
    #  'service.delCode': delCode,
    'service.saveCode': saveCode,
    'service.getCodeByCode': getCodeByCode,
    'service.getCodeById': getCodeById,
    'service.getAllProductSite': getAllProductSite,
    'service.getAllOpenProductSite': getAllOpenProductSite,
    'service.saveSite': saveSite,
    'service.delSite': delSite,
    'service.openSite': openSite,
    'service.getProductSiteById': getProductSiteById,
    'service.getAllOrderNo': getAllOrderNo,
    'service.getOrderNoById': getOrderNoById,
    'service.getOrderNoByBH': getOrderNoByBH,
    'service.getOrderByBH': getOrderByBH,
    'service.getAllOrderList': getAllOrderList,
    'service.setOrderListClose': setOrderListClose,
    'service.getOrderIsOpen': getOrderIsOpen,
    'service.saveOrder': saveOrder,
    'service.delOrder': delOrder,
    'service.getOrderByBHAndCode': getOrderByBHAndCode,
    'service.getOrderAllBBNo': getOrderAllBBNo,
    'service.getOrderBBNoByUser': getOrderBBNoByUser,
    'service.getOrderBBNoByDate': getOrderBBNoByDate,
    'service.getOrderBBNoByDateQJ': getOrderBBNoByDateQJ,
    'service.getNewOrderBBNoByUser': getNewOrderBBNoByUser,
    'service.delOrderBB': delOrderBB,
    'service.saveOrderBB': saveOrderBB,
    'service.isOrderBBNoUnlock': isOrderBBNoUnlock,
    'service.getOrderBBByLsh': getOrderBBByLsh,
    'service.getOrderGenZongByDate': getOrderGenZongByDate,
    'service.getOrderGenZongToday': getOrderGenZongToday,
    'service.getOrderGenZongCache': getOrderGenZongCache,
    'service.getWriteExcel': getWriteExcel,
    'service.getWriteExcel2': getWriteExcel2,
    'service.getOrderBBExcel': getOrderBBExcel,
    'service.getCodeExcel': getCodeExcel,
    'service.getOrderExcel': getOrderExcel,
    'service.getZYOrderGenZongByOrderAndSite': getZYOrderGenZongByOrderAndSite,
    'service.getZYOrderGenZongByOrderAndSite2': getZYOrderGenZongByOrderAndSite2,
    #  'service.computeOrderMonitor': computeOrderMonitor,
    'service.updatePlan': updatePlan,
    'service.updatePlanDelete': updatePlanDelete,
    'service.updatePlanUNDelete': updatePlanUNDelete,
    'service.updatePlanZYDH': updatePlanZYDH,
    'service.checkOrderbbPlanDetail': checkPlanDetail,
    'service.checkPlan': checkPlan,
    'service.uncheckPlan': uncheckPlan,
    'service.getAllPlanNo': getAllPlanNo,
    'service.queryPlanDetail': queryPlanDetail2,
    'service.closePlanDetail': closePlanDetail,
    'service.onlinePlanDetail': onlinePlanDetail,
    'service.queryPlanDaily': queryPlanDaily,
    'service.queryPlanByUser': queryPlanByUser,
    'service.getPlanDetailByIdOrLsh': getPlanDetailByIdOrLsh,
    'service.queryPlan': queryPlan,
    'service.changerecordPlan': changerecordPlan,
    'service.changerecordPlanDelete': changerecordPlanDelete,

    'service.getZYDHByOrderList': getZYDHByOrderList,
    'service.getZYDHByCode': getZYDHByCode,


    'service.getOrderRuningList': getOrderRuningList,
    'service.getOrderEndDate': getOrderEndDate,
})