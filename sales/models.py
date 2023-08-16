from decimal import Decimal
from django.db import models
import datetime

class SharedClientData(models.Model):
    client_name = models.CharField("Name", max_length=200, default="")
    street      = models.CharField("Straße", max_length=200, default="")
    area_code   = models.PositiveIntegerField("PLZ", default=0)
    city        = models.CharField("Stadt", max_length=200, default="")
    
    class Meta:
        abstract = True


class SharedCarData(models.Model):
    make            = models.CharField("Marke", max_length=200, default="Mazda")
    model           = models.CharField("Modell", max_length=200, default="MX-5")
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

class Invoice(SharedClientData):
    number   = models.IntegerField("Rechnungsnummer", unique=True, default=get_new_invoice_number)
    date     = models.DateField("Rechnungsdatum", default=datetime.date.today)
    complete = models.BooleanField("Abgeschlossen", default=False)

    def __str__(self) -> str:
        return f"#{self.number} vom {self.date}"

    class Meta:
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"


def get_new_position_index():
        index_max = Item.objects.all().aggregate(models.Max('index'))['index__max']
        if index_max:
            return index_max + 1
        return 1

class Item(models.Model):
    index   = models.PositiveIntegerField("Pos.", default=0, blank=False, null=False, db_index=True)
    name    = models.CharField("Bezeichnung", max_length=200)
    value   = models.DecimalField("Betrag", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    tax     = models.IntegerField("MWSt", default=19)

    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positionen"
        ordering = ["index"]
