# Generated by Django 3.2.13 on 2022-06-24 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='mode',
            field=models.CharField(default='DIRECT', max_length=200),
        ),
    ]
