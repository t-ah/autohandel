# Generated by Django 4.2.3 on 2023-10-14 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0016_invoice_apply_tax_alter_invoice_tax'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='number',
            field=models.IntegerField(default=0, verbose_name='Rechnungsnummer (wird bei erstem PDF-Laden vergeben, wenn 0)'),
        ),
    ]