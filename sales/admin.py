from django.contrib import admin
from adminsortable2.admin import SortableAdminBase, SortableTabularInline

from sales.models import Car, Client, Invoice
from sales.forms import InvoiceForm


class CarAdmin(admin.ModelAdmin):
    list_filter = ("sold", "make",)
    search_fields = ("serial_number__startswith", "make__startswith")


class ClientAdmin(admin.ModelAdmin):
    search_fields = ("client_name__contains",)


class InvoiceAdmin(SortableAdminBase, admin.ModelAdmin): # sortable kann eigentlich raus?
    actions = ["make_PDF, make_PDF_Contract"]
    change_form_template = 'sales/invoice/change_form.html'
    form = InvoiceForm
    list_filter = ("complete", "make",)
    search_fields = ("number__startswith", "make__startswith")
    
    @admin.action(description="Rechnung als PDF herunterladen")
    def make_PDF(self, request, queryset):
        pass # template redirects to view

    @admin.action(description="Kaufvertrag als PDF herunterladen")
    def make_PDF_Contract(self, request, queryset):
        pass # template redirects to view


admin.site.site_header = "Autohandel"
admin.site.site_title = "Autohandel"
admin.site.index_title = "Autohandel Rechnungen etc."

admin.site.register(Car, CarAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Invoice, InvoiceAdmin)