# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweet', '0002_auto_20180427_0952'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='retweeted_user',
            field=models.CharField(max_length=30, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tweet',
            name='retweeted_user_image',
            field=models.CharField(max_length=200, blank=True, null=True),
        ),
    ]
