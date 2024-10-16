# Generated by Django 5.1.1 on 2024-10-04 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("general_ledger", "0014_bank_closing_balance_bank_opening_balance"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="bankbalance",
            constraint=models.UniqueConstraint(
                fields=("bank", "date", "balance_type"),
                name="bankbalance_uniq_bank_date_balance_type",
            ),
        ),
    ]
