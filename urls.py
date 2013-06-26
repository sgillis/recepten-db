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
    url(r'^((ingredients=(?P<ingredienten_ids>([0-9]+,?)*/?))|(types=(?P<types_ids>([0-9]+,?)*)/?)|(seizoenen=(?P<seizoenen>([a-zA-Z]+,?)*)/?)|((?P<vegetarisch>vegetarisch)/?)|(tijd=(?P<tijd>[0-9]+)/?))*$', 'rdb_app.views.home', name='home'),
    url(r'^signup/$', 'rdb_app.views.signup', name='signup'),
    url(r'^loginview$', 'rdb_app.views.loginview', name='loginview'),
    url(r'^logoutview/$', 'rdb_app.views.logoutview', name='logoutview'),
    url(r'^toevoegen/$', 'rdb_app.views.toevoegen', name='toevoegen'),
    url(r'^recept/(?P<recept_id>\d+)/(personen=(?P<personen>[0-9]+)/?)?$', 'rdb_app.views.recept', name='recept'),
    url(r'^ingredient/(?P<ingredient_id>\d+)/$', 'rdb_app.views.ingredient', name='ingredient'),
    url(r'^ingredienten/$', 'rdb_app.views.ingredienten', name='ingredienten'),
    url(r'^submit_recipe/$', 'rdb_app.views.submit_recipe', name='submit_recipe'),
    url(r'^profile/$', 'rdb_app.views.profile', name='profile'),
    url(r'^edit_recipe/(?P<recept_id>\d+)/$', 'rdb_app.views.edit_recipe', name='edit_recipe'),
    url(r'^delete_recipe/(?P<recept_id>\d+)/$', 'rdb_app.views.delete_recipe', name='delete_recipe'),
    # Ajax urls
    url(r'^ingredient_toevoegen/$', 'rdb_app.views.ingredient_toevoegen', name='ingredient_toevoegen'),
    url(r'^type_toevoegen/$', 'rdb_app.views.type_toevoegen', name='type_toevoegen'),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
