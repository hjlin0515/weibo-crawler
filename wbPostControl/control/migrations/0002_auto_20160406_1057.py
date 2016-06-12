# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='end_time',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='liveness',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='start_time',
            field=models.DateField(null=True, blank=True),
        ),
    ]
