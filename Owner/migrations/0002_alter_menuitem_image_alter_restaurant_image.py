# Generated by Django 5.0 on 2024-06-18 11:24

import cloud_storages.backends.appwrite
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Owner', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(blank=True, default='666c9126003710f4443a', null=True, storage=cloud_storages.backends.appwrite.AppWriteStorage(), upload_to=''),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='image',
            field=models.ImageField(blank=True, default='666c927c0021620424da', null=True, storage=cloud_storages.backends.appwrite.AppWriteStorage(), upload_to=''),
        ),
    ]
