# Generated by Django 4.2.3 on 2023-09-18 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_invoice_make_invoice_model_invoice_serial_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='colour',
            field=models.CharField(default='', max_length=200, verbose_name='Farbe'),
        ),
        migrations.AddField(
            model_name='car',
            name='letter_no',
            field=models.CharField(default='', max_length=100, verbose_name='KFZ-Brief-Nr.'),
        ),
        migrations.AddField(
            model_name='car',
            name='odo',
            field=models.PositiveIntegerField(default=0, verbose_name='KM-Stand'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='colour',
            field=models.CharField(default='', max_length=200, verbose_name='Farbe'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='letter_no',
            field=models.CharField(default='', max_length=100, verbose_name='KFZ-Brief-Nr.'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='odo',
            field=models.PositiveIntegerField(default=0, verbose_name='KM-Stand'),
        ),
        migrations.AlterField(
            model_name='car',
            name='make',
            field=models.CharField(default='', max_length=200, verbose_name='Marke'),
        ),
        migrations.AlterField(
            model_name='car',
            name='model',
            field=models.CharField(default='', max_length=200, verbose_name='Modell'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='make',
            field=models.CharField(default='', max_length=200, verbose_name='Marke'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='model',
            field=models.CharField(default='', max_length=200, verbose_name='Modell'),
        ),
    ]
