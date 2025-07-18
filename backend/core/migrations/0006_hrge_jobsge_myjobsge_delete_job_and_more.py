# Generated by Django 5.2.3 on 2025-06-29 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_job_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='HrGe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('position_url', models.URLField(max_length=255)),
                ('company_url', models.URLField(max_length=255)),
                ('published_date', models.CharField(blank=True, null=True)),
                ('end_date', models.CharField(blank=True, null=True)),
            ],
            options={
                'db_table': 'hr_ge',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='JobsGe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('position_url', models.URLField(max_length=255)),
                ('company_url', models.URLField(max_length=255)),
                ('published_date', models.CharField(blank=True, null=True)),
                ('end_date', models.CharField(blank=True, null=True)),
            ],
            options={
                'db_table': 'jobs_ge',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MyJobsGe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('position_url', models.URLField(max_length=255)),
                ('company_url', models.URLField(max_length=255)),
                ('published_date', models.CharField(blank=True, null=True)),
                ('end_date', models.CharField(blank=True, null=True)),
            ],
            options={
                'db_table': 'myjobs_ge',
                'managed': False,
            },
        ),
        migrations.DeleteModel(
            name='Job',
        ),
        migrations.AddField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
