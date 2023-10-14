from decimal import Decimal
from django.db import models
import datetime

# changes to fields need to be reflected in forms.py!
class SharedClientData(models.Model):
    title       = models.CharField("Anrede", max_length=64, default="", blank=True)
    client_name = models.CharField("Name", max_length=200, default="", blank=True)
    street      = models.CharField("Straße", max_length=200, default="", blank=True)
    area_code   = models.PositiveIntegerField("PLZ", default=0)
    city        = models.CharField("Stadt", max_length=200, default="", blank=True)
    telephone   = models.CharField("Telefon", max_length=50, default="", blank=True)
    id_tax_id   = models.CharField("Ausweis- und/oder Steuernr.", max_length=100, default="", blank=True)
    # changes to fields need to be reflected in forms.py!
    
    class Meta:
        abstract = True

# changes to fields need to be reflected in forms.py!
class SharedCarData(models.Model):
    make            = models.CharField("Marke", max_length=200, default="", blank=True)
    model           = models.CharField("Modell", max_length=200, default="", blank=True)
    colour          = models.CharField("Farbe", max_length=200, default="", blank=True)
    letter_no       = models.CharField("KFZ-Brief-Nr.", max_length=100, default="", blank=True)
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
        return f"{self.make} {self.model} EZL: {Invoice.short_date(self.year)} S/N: {self.serial_number}"
    
    class Meta:
        verbose_name = "Fahrzeug"
        verbose_name_plural = "🚗 Fahrzeuge"


class Client(SharedClientData):
    def __str__(self):
        return self.client_name
    
    class Meta:
        verbose_name = "Kunde"
        verbose_name_plural = "👤 Kunden"


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
    # number    = models.IntegerField("Rechnungsnummer", unique=True, default=get_new_invoice_number)
    number    = models.IntegerField("Rechnungsnummer (wird bei erstem PDF-Laden vergeben, wenn 0)", unique=False, default=0)
    date      = models.DateField("Rechnungsdatum", default=datetime.date.today)
    value     = models.DecimalField("Betrag (brutto)", max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax       = models.IntegerField("MWSt.-satz", default=19)
    apply_tax = models.BooleanField("MWSt. anwenden", default=False)
    payment   = models.CharField("Zahlungsmethode", max_length=2, choices=PAYMENT_CHOICES, default=PAYMENT_CASH)
    terms     = models.CharField("Bedingungen", max_length=5, choices=TERMS_CHOICES, default=TERMS_25a_DIFF)
    complete  = models.BooleanField("Abgeschlossen", default=False)

    @classmethod
    def convert_date(cls, date):
        return "{:%d. %B %Y}".format(date)

    @classmethod
    def short_date(cls, date):
        return "{:%d.%m.%Y}".format(date)
    
    @classmethod
    def get_new_invoice_number(cls):
        number_max = Invoice.objects.all().aggregate(models.Max('number'))['number__max']
        if number_max:
            return number_max + 1
        return 1
    
    def __str__(self) -> str:
        return f"#{self.number} vom {Invoice.short_date(self.date)} : {self.make} {self.model}"

    class Meta:
        verbose_name = "Verkauf"
        verbose_name_plural = "💰 Verkäufe"


def get_new_invoice_number():
    pass # just keep an older migration happy for now