# -*- coding: utf-8 -*-
"""
celery 任务示例

本地启动celery命令: python  manage.py  celery  worker  --settings=settings
周期性任务还需要启动celery调度命令：python  manage.py  celerybeat --settings=settings
"""
import base64
import datetime
import json
import time

import requests
from celery import task
from celery.schedules import crontab
from celery.task import periodic_task
from django.http import JsonResponse

from blueking.component.shortcuts import get_client_by_user
from common.log import logger
from home_application.common_esb import fast_execute_script_esb, get_job_instance_log_esb, execute_job_esb
from home_application.models import HostInfo, HostLoad5, HostMem, HostDisk


@task()
def async_task(x, y):
    """
    定义一个 celery 异步任务
    """
    # logger.error(u"celery 定时任务执行成功，执行结果：{:0>2}:{:0>2}".format(x, y))
    # return x + y


def execute_task():
    """
    执行 celery 异步任务

    调用celery任务方法:
        task.delay(arg1, arg2, kwarg1='x', kwarg2='y')
        task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': 'x', 'kwarg2': 'y'})
        delay(): 简便方法，类似调用普通函数
        apply_async(): 设置celery的额外执行选项时必须使用该方法，如定时（eta）等
                      详见 ：http://celery.readthedocs.org/en/latest/userguide/calling.html
    """
    # now = datetime.datetime.now()
    # logger.error(u"celery 定时任务启动，将在60s后执行，当前时间：{}".format(now))
    # # 调用定时任务
    # async_task.apply_async(args=[now.hour, now.minute], eta=now + datetime.timedelta(seconds=60))


@periodic_task(run_every=crontab(minute='*/5', hour='*', day_of_week="*"))
def get_time():
    """
    celery 周期任务示例

    run_every=crontab(minute='*/5', hour='*', day_of_week="*")：每 5 分钟执行一次任务
    periodic_task：程序运行时自动触发周期任务
    """
    # execute_task()
    # now = datetime.datetime.now()
    # logger.error(u"celery 周期任务调用成功，当前时间：{}".format(now))


# @periodic_task(run_every=crontab(minute='*/1', hour='*', day_of_week='*'))
# def get_job_instance_status():
#     logger.info(u"已启动作业状态查询")
#     all_history = JobHistory.objects.all()
#     for obj in all_history:
#         if obj.job_status not in [3, 4]:
#             url_status = BK_PAAS_HOST + '/api/c/compapi/v2/job/get_job_instance_status/'
#             url_log = BK_PAAS_HOST + '/api/c/compapi/v2/job/get_job_instance_log/'
#             params = {
#                 "bk_app_code": APP_ID,
#                 "bk_app_secret": APP_TOKEN,
#                 "bk_username": "admin",
#                 "bk_biz_id": obj.bk_biz_id,
#                 "job_instance_id": obj.job_instance_id
#             }
#             response_status = requests.post(url_status, json.dumps(params), verify=False)
#             response_log = requests.post(url_log, json.dumps(params), verify=False)
#             data_status = json.loads(response_status.content)
#             data_log = json.loads(response_log.content)
#             if data_status['result']:
#                 history_obj = JobHistory.objects.get(bk_biz_id=obj.bk_biz_id, job_instance_id=obj.job_instance_id)
#                 history_obj.job_status = data_status['data']['job_instance']['status']
#                 if data_log['result']:
#                     history_obj.job_log = json.dumps(data_log['data'])
#                     history_obj.save()


@periodic_task(run_every=crontab(minute='*/1', hour='*', day_of_week='*'))
def get_load5():
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
                "name": "查看CPU负载",
                "script_content": "#!/bin/bash\n\ncat /proc/loadavg",
                "block_name": "查看CPU负载",
                "create_time": "2019-04-08 10:06:52 +0800",
                "last_modify_time": "2019-04-08 10:06:55 +0800",
                "ip_list": ip_list,
                "step_id": 1,
                "script_id": 2,
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
                    load5 = result['log_content'].split(' ')[1]
                    ip = result['ip']
                    check_time = result['start_time'].split(' +')[0]
                    host_info = HostInfo.objects.get(bk_host_innerip=ip)
                    HostLoad5.objects.create(load5=load5,
                                             check_time=datetime.datetime.strptime(check_time, "%Y-%m-%d %H:%M:%S"),
                                             bk_host_innerip=host_info)
            except KeyError:
                logger.error(u"找不到负载数据")


@periodic_task(run_every=crontab(minute='*/1', hour='*', day_of_week='*'))
def get_mem():
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
                "name": "查看内存状态",
                "script_content": "#!/bin/bash\n\n# 查看内存状态\n\nfree -m",
                "block_name": "查看内存状态",
                "create_time": "2019-04-08 10:08:41 +0800",
                "last_modify_time": "2019-04-08 10:08:43 +0800",
                "ip_list": ip_list,
                "step_id": 1,
                "script_id": 4,
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
                    mem = result['log_content'].split('\n')[1].split(' ')
                    real_mem = []
                    for item in mem:
                        if item:
                            real_mem.append(item)

                    ip = result['ip']
                    check_time = result['start_time'].split(' +')[0]
                    host_info = HostInfo.objects.get(bk_host_innerip=ip)
                    HostMem.objects.create(used_mem=real_mem[2],
                                           free_mem=real_mem[3],
                                           check_time=datetime.datetime.strptime(check_time, "%Y-%m-%d %H:%M:%S"),
                                           bk_host_innerip=host_info)
            except KeyError:
                logger.error(u"找不到内存数据")


@periodic_task(run_every=crontab(minute='*/1', hour='*', day_of_week='*'))
def get_disk():
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
            except KeyError:
                logger.error(u"找不到磁盘数据")
