# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostinfo',
            name='desc',
            field=models.TextField(default=b'', verbose_name='\u5907\u6ce8'),
        ),
    ]
