from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
import zt.settings as settings
from zt.ztmanage.views import index,checkZZB
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^zt/', include('zt.foo.urls')),
    (r'^$',index),
    (r'^check.html$',checkZZB),
    (r'^zt_flex.html$',index),
    (r'^accounts/login/$',login,{'template_name':'zt/login.html'}),
    (r'^accounts/logout/$', logout,{'template_name':'zt/logout.html'}),
    (r'^accounts/profile/$',index),

    (r'^zt/', include('zt.ztmanage.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',{'document_root':settings.MEDIA_ROOT}),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
