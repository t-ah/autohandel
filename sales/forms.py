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
            cdata["title"] = client.title
            cdata["client_name"] = client.client_name
            cdata["street"] = client.street
            cdata["area_code"] = client.area_code
            cdata["city"] = client.city
            cdata["telephone"] = client.telephone
            cdata["id_tax_id"] = client.id_tax_id

        car_id = self.data["load_car"]
        if car_id: # mark car sold and set (shared car data) fields of invoice
            car = Car.objects.get(pk=car_id)
            car.sold = True
            car.save()
            cdata["make"] = car.make
            cdata["model"] = car.model
            cdata["colour"] = car.colour
            cdata["letter_no"] = car.letter_no
            cdata["odo"] = car.odo
            cdata["serial_number"] = car.serial_number
            cdata["year"] = car.year
            cdata["capacity"] = car.capacity
            cdata["power_output"] = car.power_output
            cdata["tuev_au"] = car.tuev_au
            cdata["plate"] = car.plate

        return cdata