# Generated by Django 5.0.6 on 2024-07-07 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0018_rename_locality_customer_first_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customer",
            name="user_image",
            field=models.ImageField(blank=True, null=True, upload_to="userimg"),
        ),
    ]
