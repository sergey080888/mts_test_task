# Generated by Django 4.2.5 on 2023-09-16 12:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mts", "0002_rename_ptice_tarifs_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tarifs",
            name="price",
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name="tarifs",
            name="price_old",
            field=models.FloatField(null=True),
        ),
    ]
