# Generated by Django 5.1 on 2024-10-26 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_transaction_status_alter_orderplaced_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="status_id",
            field=models.CharField(default=21, max_length=255),
            preserve_default=False,
        ),
    ]