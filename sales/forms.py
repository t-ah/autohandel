from django import forms

from sales.models import Invoice, Client, Car, Item

class InvoiceForm(forms.ModelForm):
    load_client = forms.ModelChoiceField(Client.objects.all(), label="Kundendaten übernehmen", required=False)
    load_car = forms.ModelChoiceField(Car.objects.filter(sold=False), label="Fahrzeug hinzufügen", required=False)

    class Meta:
        model = Invoice
        fields = "__all__"

    def clean(self):
        cdata = super(InvoiceForm, self).clean()

        client_id = self.data["load_client"]
        if client_id:
            client = Client.objects.get(pk=client_id)
            cdata["client_name"] = client.client_name
            cdata["street"] = client.street
            cdata["city"] = client.city
            cdata["area_code"] = client.area_code

        car_id = self.data["load_car"]
        if car_id: # mark car sold and add as item to invoice
            car = Car.objects.get(pk=car_id)
            car.sold = True
            car.save()
            
            new_item = Item.objects.create(index=0, invoice_id=self.instance.id)
            # new_item.index = 0
            # new_item.invoice = Invoice.objects.get(cdata["pk"])
            print(f"INVOICE {new_item.invoice}")
            new_item.name = car.__str__()
            new_item.tax = 19 # TODO use default tax configured somewhere
            new_item.save()

        return cdata