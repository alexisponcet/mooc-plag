# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jplag_app', '0002_auto_20151211_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionfile',
            name='submission',
            field=models.ForeignKey(to='jplag_app.Submission', verbose_name='Submission '),
        ),
    ]
