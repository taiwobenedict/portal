# Generated by Django 3.2 on 2021-10-03 14:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratedVoucher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voucher', models.CharField(blank=True, default='', max_length=30, null=True)),
                ('voucher_amount', models.IntegerField()),
                ('status', models.CharField(default='UN-USED', max_length=7)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UsedVouchers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='', max_length=7)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_used_voucher', to=settings.AUTH_USER_MODEL)),
                ('voucher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='voucher.generatedvoucher')),
            ],
        ),
    ]
