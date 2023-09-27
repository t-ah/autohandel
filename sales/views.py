import io
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from dynamic_preferences.registries import global_preferences_registry
from .models import Invoice


def index(request):
    return HttpResponse("Hallo Welt. Hier werden Autos verkauft.")


# It is said that reportlab is not thread-safe. We shall ignore that here since parallel usage is not to be expected.
def pdf(request, id: int):
    prefs = global_preferences_registry.manager()

    invoice = Invoice.objects.get(pk=id)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
    width, height = A4
    margin = 20

    # p.setFontSize(12)
    p.drawString(margin, margin + 10, "Kanaan-Automobile") # TODO
    p.drawString(margin, margin + 20, "Kanaan-Automobile") # TODO
    p.drawString(margin, margin + 30, "Kanaan-Automobiles") # TODO
    p.line(5,5,width - 5,height - 5)

    p.drawString(100, 50, str(invoice.number))

    text = p.beginText(100, 100)
    for l in prefs["Bankverbindung"].split("$"):
        text.textLine(l)
    p.drawText(text)

    text = p.beginText(200, 200)
    text.textLines(prefs["Bankverbindung"])
    p.drawText(text)

    # p.drawString(100, 100, prefs["Bankverbindung"])

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename="hello.pdf")  # TODO as_attachment=True für öffnen und runterladen