# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.views',
    (r'^$', 'home'),
    (r'^dev-guide/$', 'dev_guide'),
    (r'^contactus/$', 'contactus'),
    (r'^api/test/$', 'test'),
    (r'^modal/$', 'modal'),

    (r'^get_set/$', 'get_set'),
    (r'^get_biz/$', 'get_biz'),
    (r'^search_host/$', 'get_host'),
    (r'^list_host/$', 'list_host'),
    (r'^add_host/$', 'add_host'),
    (r'^delete_host/$', 'delete_host'),
    (r'^edit_desc/$', 'edit_desc'),
    (r'^get_load5/$', 'get_load5'),
    (r'^display_performance/$', 'display_performance'),

)
