from decimal import Decimal
from django.db import models
import datetime

# changes to fields need to be reflected in forms.py!
class SharedClientData(models.Model):
    title       = models.CharField("Anrede", max_length=64, default="")
    client_name = models.CharField("Name", max_length=200, default="")
    street      = models.CharField("Straße", max_length=200, default="")
    area_code   = models.PositiveIntegerField("PLZ", default=0)
    city        = models.CharField("Stadt", max_length=200, default="")
    telephone   = models.CharField("Telefon", max_length=50, default="", blank=True)
    id_tax_id   = models.CharField("Ausweis- und/oder Steuernr.", max_length=100, default="", blank=True)
    # changes to fields need to be reflected in forms.py!
    
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
    capacity        = models.CharField("Hubraum", max_length=20, default="", blank=True)
    power_output    = models.CharField("PS/kW", max_length=20, default="", blank=True)
    tuev_au         = models.CharField("TÜV/AU", max_length=20, default="", blank=True)
    plate           = models.CharField("Kennzeichen", max_length=20, default="", blank=True)
    # changes to fields need to be reflected in forms.py!
    
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
    PAYMENT_CASH = "c"
    PAYMENT_TRANSFER = "t"
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Bar"),
        (PAYMENT_TRANSFER, "Überweisung"),
    ]
    TERMS_25a_DIFF = "25a"
    TERMS_6a_IGL = "6a"
    TERMS_4_NON_EU = "4"
    TERMS_4_EU = "4eu"
    TERMS_CHOICES = [
        (TERMS_25a_DIFF, "§ 25a Differenzbesteuerung"),
        (TERMS_6a_IGL, "§ 6a Innergemeinschaftliche Lieferung"),
        (TERMS_4_NON_EU, "§ 4 Netto-Verkauf (Nicht-EU)"),
        (TERMS_4_EU, "§ 4 Netto-Verkauf (EU)"),
    ]
    number   = models.IntegerField("Rechnungsnummer", unique=True, default=get_new_invoice_number)
    date     = models.DateField("Rechnungsdatum", default=datetime.date.today)
    value    = models.DecimalField("Betrag (brutto)", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax      = models.IntegerField("MWSt", default=19)
    payment  = models.CharField("Zahlungsmethode", max_length=2, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    terms    = models.CharField("Bedingungen", max_length=5, choices=TERMS_CHOICES, default=TERMS_25a_DIFF)
    complete = models.BooleanField("Abgeschlossen", default=False)

    def __str__(self) -> str:
        return f"#{self.number} vom {self.date}"

    class Meta:
        verbose_name = "Rechnung"
        verbose_name_plural = "Rechnungen"