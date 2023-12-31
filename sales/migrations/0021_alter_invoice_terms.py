# Generated by Django 4.2.3 on 2023-10-14 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0020_alter_invoice_terms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='terms',
            field=models.CharField(choices=[('25a', '§ 25a Differenzbesteuerung'), ('6a', '§ 6a Innergemeinschaftliche Lieferung'), ('4', '§ 4 Netto-Verkauf (Nicht-EU)'), ('4eu', '§ 4 Netto-Verkauf (EU)'), ('BedingungA', 'Eigene Bedingungen A'), ('BedingungB', 'Eigene Bedingungen B'), ('BedingungC', 'Eigene Bedingungen C'), ('BedingungC', 'Eigene Bedingungen D')], default='25a', max_length=15, verbose_name='Bedingungen'),
        ),
    ]
