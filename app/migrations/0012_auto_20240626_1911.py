# Generated by Django 3.1.5 on 2024-06-26 19:11

import django_resized.forms
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0011_auto_20240626_1747"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="category",
            field=models.CharField(
                choices=[
                    ("M", "Mobile"),
                    ("L", "Laptop"),
                    ("MW", "Men_Wear"),
                    ("WW", "Women_Wear"),
                ],
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_image",
            field=django_resized.forms.ResizedImageField(
                blank=True,
                crop=None,
                force_format=None,
                keep_meta=True,
                null=True,
                quality=-1,
                scale=None,
                size=[700, 400],
                upload_to="productimg",
            ),
        ),
    ]
