# Generated by Django 5.1.1 on 2024-10-04 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("general_ledger", "0009_fileupload_book"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="bank",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="bank",
            constraint=models.UniqueConstraint(
                fields=("book", "slug"), name="bank_account_uniq_bank_slug"
            ),
        ),
    ]
