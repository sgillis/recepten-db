from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rdb.views.home', name='home'),
    # url(r'^rdb/', include('rdb.foo.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'rdb_app.views.home', name='home'),
    url(r'^signup/$', 'rdb_app.views.signup', name='signup'),
    url(r'^loginview$', 'rdb_app.views.loginview', name='loginview'),
    url(r'^logoutview/$', 'rdb_app.views.logoutview', name='logoutview'),
    url(r'^toevoegen/$', 'rdb_app.views.toevoegen', name='toevoegen'),
    url(r'^recept/(?P<recept_id>\d+)/$', 'rdb_app.views.recept', name='recept'),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
