# Generated by Django 2.0.6 on 2021-02-13 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorResponses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_of_api', models.CharField(default='', max_length=200)),
                ('error_name', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('error_code', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('error_description', models.TextField(blank=True, default='', null=True)),
            ],
        ),
    ]
