from dynamic_preferences.types import StringPreference, LongStringPreference
from dynamic_preferences.registries import global_preferences_registry


@global_preferences_registry.register
class BankDetailsPreference(LongStringPreference):
    name = "Bankverbindung"
    verbose_name = "Kontodaten"
    default = ""
    required = True


@global_preferences_registry.register
class FirmaPreference(LongStringPreference):
    name = "Firma"
    default = ""
    required = True


@global_preferences_registry.register
class AddressPreference(LongStringPreference):
    name = "Adresse"
    default = ""
    required = True


@global_preferences_registry.register
class OwnerPreference(StringPreference):
    name = "Inhaber"
    default = ""
    required = True


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
