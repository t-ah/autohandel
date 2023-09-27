# Generated by Django 4.2.3 on 2023-09-18 20:21

import datetime
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_alter_item_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='make',
            field=models.CharField(default='Mazda', max_length=200, verbose_name='Marke'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='model',
            field=models.CharField(default='MX-5', max_length=200, verbose_name='Modell'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='serial_number',
            field=models.CharField(default='0', max_length=200, verbose_name='Fahrgestellnummer'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='tax',
            field=models.IntegerField(default=19, verbose_name='MWSt'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='value',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name='Betrag'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='year',
            field=models.DateField(default=datetime.date.today, verbose_name='Erstzulassung'),
        ),
        migrations.DeleteModel(
            name='Item',
        ),
    ]