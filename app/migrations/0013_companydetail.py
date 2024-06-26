# Generated by Django 5.0.6 on 2024-06-28 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0012_auto_20240626_1911"),
    ]

    operations = [
        migrations.CreateModel(
            name="CompanyDetail",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=250, null=True)),
                (
                    "subscription_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                (
                    "contact_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                (
                    "office_address",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("state", models.CharField(blank=True, max_length=100, null=True)),
                ("city", models.CharField(blank=True, max_length=100, null=True)),
                ("pin_code", models.CharField(blank=True, max_length=20, null=True)),
                ("area", models.CharField(blank=True, max_length=100, null=True)),
                ("country", models.CharField(blank=True, max_length=100, null=True)),
                ("office_number_1", models.BigIntegerField(blank=True, null=True)),
                ("office_number_2", models.BigIntegerField(blank=True, null=True)),
                ("gst_number", models.CharField(blank=True, max_length=20, null=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
    ]
