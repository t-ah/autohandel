from django.contrib import admin
from adminsortable2.admin import SortableAdminBase, SortableTabularInline

from sales.models import Car, Client, Invoice, Item
from sales.forms import InvoiceForm


class ItemInline(SortableTabularInline):
    model = Item


class InvoiceAdmin(SortableAdminBase, admin.ModelAdmin):
    inlines = [ItemInline,]
    actions = ["make_PDF"]
    change_form_template = 'sales/invoice/change_form.html'
    form = InvoiceForm
    
    @admin.action(description="Als PDF anzeigen")
    def make_PDF(self, request, queryset):
        pass # template redirects to view


admin.site.register(Car)
admin.site.register(Client)
admin.site.register(Invoice, InvoiceAdmin)