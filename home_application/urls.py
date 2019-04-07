# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns(
    'home_application.views',
    (r'^$', 'home'),
    (r'^dev-guide/$', 'dev_guide'),
    (r'^contactus/$', 'contactus'),
    (r'^test/$', 'test'),
    (r'^modal/$', 'modal'),
    (r'^api/getJson/$', 'getJson'),

    (r'^search_biz/$', 'search_biz'),
    (r'^search_set/$', 'search_set'),
    (r'^search_host/$', 'search_host'),
    (r'^fast_execute_script/$', 'fast_execute_script'),
    (r'^execute_job/$', 'execute_job'),
    (r'^job_detail/$', 'job_detail'),
    (r'^get_log_content/$', 'get_log_content'),
    (r'^fast_push_file/$', 'fast_push_file'),
)
