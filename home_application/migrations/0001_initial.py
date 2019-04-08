# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HostInfo',
            fields=[
                ('bk_host_innerip', models.CharField(max_length=50, serialize=False, verbose_name='IP\u5730\u5740', primary_key=True)),
                ('bk_host_name', models.CharField(max_length=50, verbose_name='\u4e3b\u673a\u540d')),
                ('bk_os_name', models.CharField(max_length=50, verbose_name='\u7cfb\u7edf\u540d')),
                ('bk_inst_name', models.CharField(max_length=50, verbose_name='\u4e91\u533a\u57df\u540d\u79f0')),
                ('bk_biz_id', models.IntegerField(verbose_name='\u4e1a\u52a1ID')),
                ('bk_biz_name', models.CharField(max_length=50, verbose_name='\u4e1a\u52a1\u540d\u79f0')),
                ('bk_cloud_id', models.IntegerField(verbose_name='\u4e91\u533a\u57dfID')),
                ('last_user', models.CharField(default=b'admin', max_length=50, verbose_name='\u7528\u6237\u540d')),
                ('is_delete', models.BooleanField(default=False, verbose_name='\u662f\u5426\u5220\u9664')),
            ],
        ),
    ]
