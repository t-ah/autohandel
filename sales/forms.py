from django import forms
from sales.models import Invoice, Client, Car

class InvoiceForm(forms.ModelForm):
    load_client = forms.ModelChoiceField(Client.objects.all(), label="Kundendaten einfügen", required=False)
    load_car = forms.ModelChoiceField(Car.objects.filter(sold=False), label="Fahrzeugdaten einfügen", required=False)

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
        if car_id: # mark car sold and set (shared car data) fields of invoice
            car = Car.objects.get(pk=car_id)
            car.sold = True
            car.save()
            cdata["make"] = car.make
            cdata["model"] = car.model
            cdata["serial_number"] = car.serial_number
            cdata["year"] = car.year
            cdata["colour"] = car.colour
            cdata["letter_no"] = car.letter_no
            cdata["odo"] = car.odo

        return cdata