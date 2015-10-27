from django.conf.urls import patterns, include, url
from django.contrib import admin
from aglaia import settings

urlpatterns = patterns('excel.views',
                       url(r'^$', 'index'),
                       url(r'^export_database/$', 'export_database'),
                       url(r'^export_excel/$', 'export_excel'),
                       url(r'^import_database/$', 'import_database'),
                       url(r'^import_excel/$', 'import_excel'),
                       )
