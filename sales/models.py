from decimal import Decimal
from django.db import models
import datetime

# changes to fields need to be reflected in forms.py!
class SharedClientData(models.Model):
    client_name = models.CharField("Name", max_length=200, default="")
    street      = models.CharField("Straße", max_length=200, default="")
    area_code   = models.PositiveIntegerField("PLZ", default=0)
    city        = models.CharField("Stadt", max_length=200, default="")
    
    class Meta:
        abstract = True

# changes to fields need to be reflected in forms.py!
class SharedCarData(models.Model):
    make            = models.CharField("Marke", max_length=200, default="")
    model           = models.CharField("Modell", max_length=200, default="")
    colour          = models.CharField("Farbe", max_length=200, default="")
    letter_no       = models.CharField("KFZ-Brief-Nr.", max_length=100, default="")
    odo             = models.PositiveIntegerField("KM-Stand", default=0)
    serial_number   = models.CharField("Fahrgestellnummer", max_length=200, default="0")
    year            = models.DateField("Erstzulassung", default=datetime.date.today)
    
    class Meta:
        abstract = True


class Car(SharedCarData):
    sold = models.BooleanField("Verkauft", default=False)

    def __str__(self):
        return f"{self.make} {self.model} EZL: {self.year} S/N: {self.serial_number}"
    
    class Meta:
        verbose_name = "Fahrzeug"
        verbose_name_plural = "Fahrzeuge"


class Client(SharedClientData):
    def __str__(self):
        return self.client_name
    
    class Meta:
        verbose_name_plural = "Kunden"


def get_new_invoice_number():
        number_max = Invoice.objects.all().aggregate(models.Max('number'))['number__max']
        if number_max:
            return number_max + 1
        return 1

class Invoice(SharedClientData, SharedCarData):
    number   = models.IntegerField("Rechnungsnummer", unique=True, default=get_new_invoice_number)
    date     = models.DateField("Rechnungsdatum", default=datetime.date.today)
    value    = models.DecimalField("Betrag", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax      = models.IntegerField("MWSt", default=19)
    complete = models.BooleanField("Abgeschlossen", default=False)

    def __str__(self) -> str:
        return f"#{self.number} vom {self.date}"

    class Meta:
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"