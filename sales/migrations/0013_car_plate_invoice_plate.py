# Generated by Django 4.2.3 on 2023-10-01 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0012_car_tuev_au_invoice_tuev_au'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='plate',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Kennzeichen'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='plate',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Kennzeichen'),
        ),
    ]
