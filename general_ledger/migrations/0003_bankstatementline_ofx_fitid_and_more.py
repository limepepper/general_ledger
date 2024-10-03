# Generated by Django 5.1.1 on 2024-10-01 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("general_ledger", "0002_alter_historicalinvoice_invoice_number_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="bankstatementline",
            name="ofx_fitid",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="bankstatementline",
            name="ofx_memo",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
