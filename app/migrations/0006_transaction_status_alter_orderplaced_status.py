# Generated by Django 5.1 on 2024-10-26 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_alter_transaction_order_delete_receipt"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="status",
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="orderplaced",
            name="status",
            field=models.CharField(
                choices=[
                    ("Accepted", "Accepted"),
                    ("Packed", "Packed"),
                    ("On The Way", "On The Way"),
                    ("Delivered", "Delivered"),
                    ("Cancel", "Cancel"),
                    ("Failed", "Failed"),
                ],
                default="Pending",
                max_length=50,
            ),
        ),
    ]
