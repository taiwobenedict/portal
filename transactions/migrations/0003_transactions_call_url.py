# Generated by Django 3.2.13 on 2022-06-26 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0002_transactions_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='call_url',
            field=models.TextField(blank=True, max_length=20000, null=True),
        ),
    ]