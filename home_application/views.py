# -*- coding: utf-8 -*-
import base64
import datetime
import json
import time

import requests
from django.forms import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from account.decorators import login_exempt
from blueking.component.shortcuts import get_client_by_user, get_client_by_request
from common.log import logger
from common.mymako import render_mako_context
from common.mymako import render_json
from conf.default import APP_ID, APP_TOKEN, BK_PAAS_HOST

from home_application.common_esb import get_job_instance_log_esb, fast_execute_script_esb, search_host_esb, \
    search_set_esb, search_business_esb, fast_push_file_esb
from home_application.models import HostInfo


def home(request):
    """
    首页
    """
    return render_mako_context(request, '/home_application/home.html')


def dev_guide(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/dev_guide.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')


def modal(request):
    """
    测试
    """
    return render_mako_context(request, '/home_application/modal.html')


def test(request):
    return render_json({"result": 'ok', "username": request.user.username})


@csrf_exempt
def get_biz(request):
    client = get_client_by_request(request)
    res = search_business_esb(client, request.user.username)
    return render_json(res)


@csrf_exempt
def get_set(request):
    bk_biz_id = request.GET.get('bk_biz_id')
    client = get_client_by_request(request)
    res = search_set_esb(client, request.user.username, bk_biz_id)
    return render_json(res)


@csrf_exempt
def get_host(request):
    params = json.loads(request.body)
    bk_host_innerip__in = params.get('bk_host_innerip__in')
    client = get_client_by_request(request)
    res = search_host_esb(client, request.user.username)
    result = []
    for item in res['data']:
        params = {
            'bk_host_innerip': item['host']['bk_host_innerip'],
            'bk_host_name': item['host']['bk_host_name'],
            'bk_os_name': item['host']['bk_os_name'],
            'bk_inst_name': item['host']['bk_cloud_id'][0]['bk_inst_name'],
            'bk_cloud_id': item['host']['bk_cloud_id'][0]['id'],
            'bk_biz_id': item['biz'][0]['bk_biz_id'],
            'bk_biz_name': item['biz'][0]['bk_biz_name'],
            'last_user': request.user.username
        }
        host_info, is_exist = HostInfo.objects.update_or_create(**params)
        if is_exist:
            host_info.last_user = request.user.username
            host_info.save()

    if bk_host_innerip__in:
        bk_host_innerip__in = bk_host_innerip__in.split(',')
        host_info = HostInfo.objects.filter(bk_host_innerip__in=bk_host_innerip__in, is_delete=False)
    else:
        host_info = HostInfo.objects.filter(is_delete=False)
    for host in host_info:
        result.append(model_to_dict(host))

    return render_json({'data': result})


@csrf_exempt
def list_host(request):
    bk_biz_id = request.GET.get('bk_biz_id')
    client = get_client_by_request(request)
    res = search_host_esb(client, request.user.username, bk_biz_id)
    result = []
    for item in res['data']:
        params = {
            'bk_host_innerip': item['host']['bk_host_innerip']
        }
        result.append(params)
    return render_json({'data': result})


@csrf_exempt
def add_host(request):
    params = json.loads(request.body)
    ip = params['ip']
    host_info = HostInfo.objects.filter(bk_host_innerip=ip, is_delete=False)
    if host_info:
        result = u'主机已存在'
    else:
        HostInfo.objects.filter(bk_host_innerip=ip).update(is_delete=False)
        result = u'添加成功'
    return render_json({'data': result})


@csrf_exempt
def delete_host(request):
    params = json.loads(request.body)
    ip = params['ip']
    HostInfo.objects.filter(bk_host_innerip=ip).update(is_delete=True)
    return render_json({'data': u'删除成功'})


# @csrf_exempt
# def display_performance(request):
#     def generate_data(pfm_list):
#         if not pfm_list:
#             return None
#         xAxis = []
#         series = []
#         load5 = []
#
#         for host_pfm in pfm_list:
#             xAxis.append(host_pfm.check_time.strftime("%Y-%m-%d %H:%M:%S"))
#             load5.append(host_pfm.load5)
#         series.append({
#             'name': 'load5',
#             'type': 'line',
#             'data': load5
#         })
#         return {
#             "xAxis": xAxis,
#             "series": series,
#             "title": pfm_list[0].bk_host_innerip.bk_host_innerip
#         }
#
#     ip = request.GET.get('ip')
#     now = datetime.datetime.now()
#     load5 = HostLoad5.objects.filter(bk_host_innerip=ip)
#     load5_result = generate_data(load5)
#     return render_json({'load5': load5_result})


# @csrf_exempt
# def get_load5(request):
#     host_info_list = HostInfo.objects.filter(is_delete=False)
#
#     ip_list = []
#     if not host_info_list:
#         return
#     else:
#         username = host_info_list[0].last_user
#         bk_biz_id = host_info_list[0].bk_biz_id
#
#     for host_info in host_info_list:
#         ip_list.append({
#             'ip': host_info.bk_host_innerip,
#             'bk_cloud_id': host_info.bk_cloud_id
#         })
#
#     client = get_client_by_user(username)
#     load5_script = '''#!/bin/bash
# cat /proc/loadavg'''
#
#     mem_script = '''#!/bin/bash
# free –m'''
#
#     disk_script = '''#!/bin/bash
# df –h'''
#
#     data = {
#         'ip_list': ip_list,
#         'bk_biz_id': bk_biz_id
#     }
#     res = fast_execute_script_esb(client, 'admin', data, base64.b64encode(load5_script))
#     time.sleep(5)
#     if res['data']:
#         params = {}
#         params.update({'bk_biz_id': data['bk_biz_id'], 'job_instance_id': res['data']['job_instance_id']})
#         res = get_job_instance_log_esb(client, 'admin', params)
#
#         for i in range(5):
#             if res['data'][0]['status'] != 3:
#                 time.sleep(2)
#                 res = get_job_instance_log_esb(client, 'admin', params)
#             else:
#                 break
#
#         if res['data'][0]['status'] == 3:
#             # 处理性能数据
#             try:
#                 pfm_data = res['data'][0]['step_results'][0]['ip_logs']
#             except KeyError:
#                 pfm_data = []
#             for item in pfm_data:
#                 result = item['log_content'].split(' ')
#                 load5 = result[1]
#                 mem = result[1]
#                 disk = result[2]
#                 cpu = result[3]
#                 ip = item['ip']
#                 host_info = HostInfo.objects.get(bk_host_innerip=ip)
#                 host_pfm = HostLoad5.objects.create(
#                     bk_host_innerip=host_info,
#                     check_time=datetime.datetime.now(),
#                     load5=load5
#                 )
#             now = datetime.datetime.now()
#             logger.info(u"主机{}完成一条性能查询：{}".format(host_pfm.bk_host_innerip, now))


class CommonUtil(object):

    @classmethod
    def pop_useless_params(self, params):
        # 请求参数处理
        pop_keys = []
        for key, value in params.items():
            if value == '':
                pop_keys.append(key)
            if key.endswith('__in'):
                params[key] = str(value).split(',')
        for pop in pop_keys:
            params.pop(pop)
        return params


def fast_push_file(request):
    client = get_client_by_request(request)
    biz_id = request.GET.get('biz_id')
    file_target_path = "/tmp/"
    target_ip_list = [{
        "bk_cloud_id": 0,
        "ip": "192.168.240.52"
    },
        {
            "bk_cloud_id": 0,
            "ip": "192.168.240.55"
        }
    ]
    file_source_ip_list = [{
        "bk_cloud_id": 0,
        "ip": "192.168.240.43"
    }
    ]
    file_source = ["/tmp/test12.txt"]
    data = fast_push_file_esb(client, biz_id, file_target_path, file_source, target_ip_list, file_source_ip_list,
                              request.user.username)
    return JsonResponse(data)
