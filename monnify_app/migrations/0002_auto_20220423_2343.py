# Generated by Django 3.2 on 2022-04-23 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monnify_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monnifyaccount',
            name='accountName',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='monnifyaccount',
            name='accountNumber',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='monnifyaccount',
            name='bankCode',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='monnifyaccount',
            name='bankName',
            field=models.CharField(default='', max_length=500),
        ),
    ]
