# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0002_hostinfo_desc'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostDisk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('disk', models.TextField(verbose_name='\u786c\u76d8\u60c5\u51b5')),
                ('check_time', models.DateTimeField(auto_now=True, verbose_name='\u68c0\u6d4b\u65f6\u95f4')),
                ('bk_host_innerip', models.ForeignKey(to='home_application.HostInfo', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='HostLoad5',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('load5', models.CharField(max_length=10, verbose_name='5\u5206\u949f\u8d1f\u8f7d')),
                ('check_time', models.DateTimeField(auto_now=True, verbose_name='\u68c0\u6d4b\u65f6\u95f4')),
                ('bk_host_innerip', models.ForeignKey(to='home_application.HostInfo', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='HostMem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mem', models.TextField(verbose_name='\u5185\u5b58\u60c5\u51b5')),
                ('check_time', models.DateTimeField(auto_now=True, verbose_name='\u68c0\u6d4b\u65f6\u95f4')),
                ('bk_host_innerip', models.ForeignKey(to='home_application.HostInfo', max_length=20)),
            ],
        ),
    ]
