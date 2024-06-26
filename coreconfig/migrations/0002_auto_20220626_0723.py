# Generated by Django 3.2.13 on 2022-06-26 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreconfig', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboardconfig',
            name='dashboard_extra_info',
            field=models.TextField(blank=True, default='', max_length=1000000, null=True),
        ),
        migrations.AddField(
            model_name='dashboardconfig',
            name='redirect_user_on_insufficient_funds',
            field=models.BooleanField(default=True),
        ),
    ]
