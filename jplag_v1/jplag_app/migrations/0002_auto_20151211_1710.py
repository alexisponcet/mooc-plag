# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jplag_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submissionfile',
            name='submission',
            field=models.ForeignKey(verbose_name='Submission ', null=True, to='jplag_app.Submission', blank=True),
        ),
    ]
