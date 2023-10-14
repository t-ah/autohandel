from dynamic_preferences.types import StringPreference, LongStringPreference
from dynamic_preferences.registries import global_preferences_registry


@global_preferences_registry.register
class BankDetailsPreference(LongStringPreference):
    name = "Bankverbindung"
    verbose_name = "Kontodaten"
    default = ""
    required = True
    help_text = "Erscheint unten auf Rechnung"


@global_preferences_registry.register
class FirmaPreference(LongStringPreference):
    name = "Firma"
    default = ""
    required = True
    help_text = "Erscheint oben links auf Rechnung"


@global_preferences_registry.register
class AddressPreference(LongStringPreference):
    name = "Adresse"
    default = ""
    required = True
    help_text = "Erscheint auf Rechnung und Kaufvertrag"


@global_preferences_registry.register
class OwnerPreference(StringPreference):
    name = "Inhaber"
    default = ""
    required = True
    help_text = "Erscheint auf Rechnung"


@global_preferences_registry.register
class TaxNumberPreference(StringPreference):
    name = "Steuernummer"
    default = ""
    required = True


@global_preferences_registry.register
class SalesTaxNumberPreference(StringPreference):
    name = "UStIDNr"
    default = ""
    required = True


@global_preferences_registry.register
class SellerNamePreference(StringPreference):
    name = "Verkäufer"
    default = ""
    required = True
    help_text = "Erscheint auf Rechnung und Kaufvertrag"


@global_preferences_registry.register
class CustomContractConditionOne(LongStringPreference):
    name = "BedingungA"
    default = "(A) Eigene Vertragsbedingung kann in den globalen Einstellungen verfasst werden."
    required = True
    help_text = "Kann als Vertragsbedingung ausgewählt werden"


@global_preferences_registry.register
class CustomContractConditionTwo(LongStringPreference):
    name = "BedingungB"
    default = "(B) Eigene Vertragsbedingung kann in den globalen Einstellungen verfasst werden."
    required = True
    help_text = "Kann als Vertragsbedingung ausgewählt werden"


@global_preferences_registry.register
class CustomContractConditionThree(LongStringPreference):
    name = "BedingungC"
    default = "(C) Eigene Vertragsbedingung kann in den globalen Einstellungen verfasst werden."
    required = True
    help_text = "Kann als Vertragsbedingung ausgewählt werden"


@global_preferences_registry.register
class CustomContractConditionFour(LongStringPreference):
    name = "BedingungD"
    default = "(D) Eigene Vertragsbedingung kann in den globalen Einstellungen verfasst werden."
    required = True
    help_text = "Kann als Vertragsbedingung ausgewählt werden"