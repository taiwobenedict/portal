# Generated by Django 3.2.13 on 2022-09-08 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smsangosend', '0003_auto_20220626_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smsangosendsms',
            name='time_to_send',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
