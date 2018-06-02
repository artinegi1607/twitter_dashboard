# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('tweet_id', models.CharField(max_length=30)),
                ('username', models.CharField(max_length=100)),
                ('text', models.CharField(max_length=800)),
                ('image', models.CharField(max_length=200)),
                ('tweet_on', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime(2018, 4, 23, 6, 48, 37, 794976, tzinfo=utc))),
            ],
        ),
    ]
