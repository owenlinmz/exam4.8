# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0003_hostdisk_hostload5_hostmem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hostmem',
            name='mem',
        ),
        migrations.AddField(
            model_name='hostmem',
            name='free_mem',
            field=models.IntegerField(default=0, verbose_name='\u7a7a\u95f2\u5185\u5b58'),
        ),
        migrations.AddField(
            model_name='hostmem',
            name='used_mem',
            field=models.IntegerField(default=0, verbose_name='\u5df2\u7528\u5185\u5b58'),
        ),
    ]
