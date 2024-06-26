# Generated by Django 2.0.6 on 2019-12-21 11:31

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
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=30)),
                ('content', models.TextField(blank=True, default='', max_length=1000, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReadNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('readAt', models.DateTimeField(auto_now_add=True)),
                ('read', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='readonly', to='notificationapp.Notification')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='readnotification', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
