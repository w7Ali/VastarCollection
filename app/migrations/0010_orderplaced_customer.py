# Generated by Django 3.1.4 on 2021-01-18 08:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0009_auto_20210118_1245"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderplaced",
            name="customer",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="app.customer",
            ),
            preserve_default=False,
        ),
    ]
