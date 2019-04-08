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
    search_set_esb, search_business_esb, fast_push_file_esb, execute_job_esb
from home_application.models import HostInfo, HostLoad5, HostMem, HostDisk


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


@csrf_exempt
def edit_desc(request):
    params = json.loads(request.body)
    ip = params['ip']
    desc = params['desc']
    HostInfo.objects.filter(bk_host_innerip=ip).update(desc=desc)
    return render_json({'data': u'修改成功'})


@csrf_exempt
def display_performance(request):
    def generate_load5(pfm_list):
        if not pfm_list:
            return None
        xAxis = []
        series = []
        load5 = []

        for host_pfm in pfm_list:
            xAxis.append(host_pfm.check_time.strftime("%Y-%m-%d %H:%M:%S"))
            load5.append(host_pfm.load5)
        series.append({
            'name': 'load5',
            'type': 'line',
            'data': load5
        })
        return {
            "xAxis": xAxis,
            "series": series,
            "title": pfm_list[0].bk_host_innerip.bk_host_innerip
        }

    ip = request.GET.get('ip')
    load5 = HostLoad5.objects.filter(bk_host_innerip=ip)[:60]
    load5_result = generate_load5(load5)

    mem = HostMem.objects.filter(bk_host_innerip=ip).last()
    mem_data = {
        'title': '',
        'series': [
            {'name': u'已用内存', 'value': mem.used_mem},
            {'name': u'空余内存', 'value': mem.free_mem},
        ]
    }

    disk = HostDisk.objects.filter(bk_host_innerip=ip).last()
    disk_data = json.loads(disk.disk)

    real_disk_data = []
    disk_data.pop(0)
    disk_data.pop()
    for item in disk_data:
        new_list = item.split(' ')
        real_list = []
        for data in new_list:
            if data:
                real_list.append(data)
        real_disk_data.append(real_list)

    return_disk_data = []
    for item in real_disk_data:
        return_disk_data.append({
            'filesystem': item[0],
            'size': item[1],
            'used': item[2],
            'avail': item[3],
            'use': item[4],
            'mounted on': item[5]
        })

    return render_json({'load5': load5_result, 'mem': mem_data, 'disk': return_disk_data})


@csrf_exempt
def get_load5(request):
    host_info_list = HostInfo.objects.filter(is_delete=False)
    ip_list = []
    if not host_info_list:
        return
    else:
        username = host_info_list[0].last_user
        bk_biz_id = host_info_list[0].bk_biz_id

    for host_info in host_info_list:
        ip_list.append({
            'ip': host_info.bk_host_innerip,
            'bk_cloud_id': host_info.bk_cloud_id
        })

    client = get_client_by_user(username)
    data = {
        'bk_biz_id': bk_biz_id,
        "bk_job_id": 1,
        "steps": [
            {
                "account": "root",
                "pause": 0,
                "is_param_sensitive": 0,
                "creator": "admin",
                "script_timeout": 1000,
                "last_modify_user": "admin",
                "block_order": 1,
                "name": "查看磁盘使用情况",
                "script_content": "#!/bin/bash\n\n# 查看磁盘使用情况\n\ndf -h",
                "block_name": "查看磁盘使用情况",
                "create_time": "2019-04-08 10:10:13 +0800",
                "last_modify_time": "2019-04-08 10:10:58 +0800",
                "ip_list": ip_list,
                "step_id": 1,
                "script_id": 7,
                "script_param": "",
                "type": 1,
                "order": 1,
                "script_type": 1
            }
        ]
    }
    res = execute_job_esb(client, username, data)
    time.sleep(5)
    if res['data']:
        params = {'bk_biz_id': data['bk_biz_id'], 'job_instance_id': res['data']['job_instance_id']}
        res = get_job_instance_log_esb(client, 'admin', params)

        for i in range(5):
            if res['data'][0]['status'] != 3:
                time.sleep(2)
                res = get_job_instance_log_esb(client, 'admin', params)
            else:
                break

        if res['data'][0]['status'] == 3:
            # 处理性能数据
            try:
                for result in res['data'][0]['step_results'][0]['ip_logs']:
                    disk = result['log_content'].split('\n')

                    ip = result['ip']
                    check_time = result['start_time'].split(' +')[0]
                    host_info = HostInfo.objects.get(bk_host_innerip=ip)
                    HostDisk.objects.create(disk=json.dumps(disk),
                                            check_time=datetime.datetime.strptime(check_time, "%Y-%m-%d %H:%M:%S"),
                                            bk_host_innerip=host_info)
                    logger.info(u'写入一条磁盘数据')
            except KeyError:
                logger.error(u"找不到负载数据")


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
