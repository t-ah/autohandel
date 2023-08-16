import io
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas

from .models import Invoice


def index(request):
    return HttpResponse("Hallo Welt. Hier werden Autos verkauft.")


# It is said that reportlab is not thread-safe. We shall ignore that here since parallel usage is not to be expected.
def pdf(request, id: int):
    invoice = Invoice.objects.get(pk=id)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(100, 100, str(invoice.number))

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="hello.pdf")