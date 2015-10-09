from django.conf.urls import patterns, include, url
from django.contrib import admin
from aglaia import settings

urlpatterns = patterns('',
					   # Examples:
					   url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
						   {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
					   # url(r'^blog/', include('blog.urls')),

					   url(r'^$', 'account.views.account_home'),
					   url(r'^account/', include('account.urls')),
					   url(r'^admin/', include(admin.site.urls)),
					   url(r'^goods/', include('goods.urls')),
					   url(r'^computing/', include('computing.urls')),
					   url(r'^log/', include('log.urls'))
					   )
