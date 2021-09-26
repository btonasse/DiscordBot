# Generated by Django 3.2.7 on 2021-09-26 08:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jupiter', '0012_character_uploaded_timestamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='character',
            name='uploaded_timestamp',
        ),
        migrations.AddField(
            model_name='character',
            name='last_modified',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 26, 10, 25, 51, 199129)),
        ),
        migrations.AddField(
            model_name='character',
            name='mortem_timestamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 9, 26, 10, 25, 51, 199129)),
        ),
        migrations.AddConstraint(
            model_name='character',
            constraint=models.UniqueConstraint(fields=('name', 'mortem_timestamp'), name='unique_mortem'),
        ),
    ]
