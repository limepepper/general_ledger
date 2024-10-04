# Generated by Django 5.1.1 on 2024-10-04 02:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("general_ledger", "0001_squashed_0007_bankbalance_balance_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="BookPreferenceModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "section",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default=None,
                        max_length=150,
                        null=True,
                        verbose_name="Section Name",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True, max_length=150, verbose_name="Name"
                    ),
                ),
                (
                    "raw_value",
                    models.TextField(blank=True, null=True, verbose_name="Raw Value"),
                ),
                (
                    "instance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="general_ledger.book",
                    ),
                ),
            ],
        ),
    ]
