# Generated by Django 4.2.3 on 2023-10-14 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0015_alter_invoice_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='apply_tax',
            field=models.BooleanField(default=False, verbose_name='MWSt. anwenden'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='tax',
            field=models.IntegerField(default=19, verbose_name='MWSt.-satz'),
        ),
    ]
