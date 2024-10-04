# Generated by Django 5.1.1 on 2024-10-04 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("general_ledger", "0017_alter_bankstatementline_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="bankstatementline",
            name="ofx_dtposted",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="bankstatementline",
            name="ofx_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="bankstatementline",
            name="ofx_trntype",
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
