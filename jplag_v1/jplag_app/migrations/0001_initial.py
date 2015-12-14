# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jplag_app.models
import smart_selects.db_fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name_assignment', models.CharField(max_length=100, verbose_name='Assignment ', unique=True)),
                ('date_assignment', models.DateTimeField(verbose_name='Date ', default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Similarity',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('similarity', models.FloatField(verbose_name='Similarity ', default=0.0)),
                ('assignment', models.ForeignKey(verbose_name='Assignment ', to='jplag_app.Assignment')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('id_student_submission', models.IntegerField(verbose_name='Identifiant ')),
                ('name_student_submission', models.CharField(max_length=30, verbose_name='Name ')),
                ('date_submission', models.DateTimeField(verbose_name='Date ', default=django.utils.timezone.now)),
                ('assignment', models.ForeignKey(verbose_name='Assignment ', to='jplag_app.Assignment')),
            ],
        ),
        migrations.CreateModel(
            name='SubmissionFile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('file_submission', models.FileField(upload_to=jplag_app.models.SubmissionFile._get_upload_to)),
                ('submission', models.ForeignKey(verbose_name='Submission ', to='jplag_app.Submission')),
            ],
        ),
        migrations.AddField(
            model_name='similarity',
            name='sub1',
            field=smart_selects.db_fields.GroupedForeignKey(related_name='Student_1', to='jplag_app.Submission', verbose_name='Student 1 ', group_field='assignment'),
        ),
        migrations.AddField(
            model_name='similarity',
            name='sub2',
            field=smart_selects.db_fields.GroupedForeignKey(related_name='Student_2', to='jplag_app.Submission', verbose_name='Student 2 ', group_field='assignment'),
        ),
        migrations.AlterUniqueTogether(
            name='assignment',
            unique_together=set([('name_assignment',)]),
        ),
        migrations.AlterUniqueTogether(
            name='submissionfile',
            unique_together=set([('submission', 'file_submission')]),
        ),
        migrations.AlterUniqueTogether(
            name='submission',
            unique_together=set([('assignment', 'id_student_submission')]),
        ),
        migrations.AlterUniqueTogether(
            name='similarity',
            unique_together=set([('assignment', 'sub1', 'sub2')]),
        ),
    ]
