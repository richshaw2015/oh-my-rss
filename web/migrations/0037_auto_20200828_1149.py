# Generated by Django 3.1 on 2020-08-28 03:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0036_auto_20200826_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='name',
            field=models.CharField(max_length=100, verbose_name='name'),
        ),
    ]
