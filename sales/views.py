import io
from decimal import Decimal

from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from dynamic_preferences.registries import global_preferences_registry

from .models import Invoice


def index(request):
    return HttpResponse("Hallo Welt. Hier werden Autos verkauft.")

def convert_date(date):
    return "{:%d. %B %Y}".format(date)

def brutto_to_netto(brutto_val, tax):
    return round(brutto_val / Decimal((100 + tax) / 100), 2)

# It is said that reportlab is not thread-safe. We shall ignore that here since parallel usage is not to be expected.
def pdf(request, id: int):
    prefs = global_preferences_registry.manager()

    invoice = Invoice.objects.get(pk=id)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
    width, height = A4
    margin = 50

    p.setFont("Helvetica-Bold", 16)
    p.drawString(margin, margin + 10, "Kanaan-Automobile") # TODO var

    text = p.beginText()
    text.setFont("Helvetica", 10)
    text.setTextOrigin(margin, margin + 25)
    text.textLines(prefs["Firma"])
    p.drawText(text)
    

    address = prefs["Adresse"].splitlines()
    p.setFont("Helvetica", 11)
    for i, line in enumerate(address):
        p.drawRightString(width - margin, margin + 10 + (i * 10), line)

    # text = p.beginText()
    # text.setFont("Helvetica", 10)
    # text.setTextOrigin(width - 200, margin + 10)
    # text.textLines(prefs["Adresse"])
    # p.drawText(text)
    # print(len(prefs["Adresse"].split("\n")))

    p.setFontSize(10)
    p.drawRightString(width - margin - 75, 150, f"Rechnungsnummer:")
    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(width - margin, 150, str(invoice.number))

    y = 170
    vspace = 12
    p.setFont("Helvetica-Bold", 11)
    p.drawString(margin, y, invoice.title)
    p.setFont("Helvetica", 11)
    y += vspace
    p.drawString(margin, y, invoice.client_name)
    y += vspace
    p.drawString(margin, y, invoice.street)
    y += vspace
    p.drawString(margin, y, f"{invoice.area_code} {invoice.city}")

    y += 40
    p.setFont("Helvetica-Bold", 16)
    p.drawString(margin, y, "Fahrzeugrechnung" if invoice.terms in [Invoice.TERMS_25a_DIFF, Invoice.TERMS_6a_IGL] else "Fahrzeugrechnung/Kaufvertrag")

    y += 30
    p.setFont("Helvetica-BoldOblique", 16)
    p.drawString(margin, y, f"{invoice.make} {invoice.model}")
    p.line(margin, y + 2, width // 2, y + 2)
    y += 20
    p.setFont("Helvetica", 11)
    right_column_offset = 150
    p.drawString(margin, y, "Fahrgestellnummer:")
    p.drawString(margin + right_column_offset, y, invoice.serial_number)
    y += 12
    p.drawString(margin, y, "Erstzulassung:")
    p.drawString(margin + right_column_offset, y, convert_date(invoice.year))
    y += 12
    p.drawString(margin, y, "Farbe:")
    p.drawString(margin + right_column_offset, y, invoice.colour)
    y += 12
    p.drawString(margin, y, "KFZ-Brief-Nr.")
    p.drawString(margin + right_column_offset, y, invoice.letter_no)
    y += 12
    p.drawString(margin, y, "Kilometerstand")
    p.drawString(margin + right_column_offset, y, str(invoice.odo))
    if invoice.capacity != "":
        y += 12
        p.drawString(margin, y, "Hubraum")
        p.drawString(margin + right_column_offset, y, invoice.capacity)
    if invoice.capacity != "":
        y += 12
        p.drawString(margin, y, "kW/PS")
        p.drawString(margin + right_column_offset, y, invoice.power_output)

    y += 40

    if invoice.terms in [Invoice.TERMS_25a_DIFF, Invoice.TERMS_6a_IGL]:
        p.setFont("Helvetica-Bold", 16)
        p.drawString(margin, y, "Gesamtpreis")
        p.line(margin, y + 2, width - margin, y + 2)

        y += 40
        p.setFont("Helvetica", 11)
        p.drawString(margin, y, "Fahrzeugpreis")
        p.drawRightString(width - margin, y, f"{invoice.value}   EURO")
        y += 30
        p.drawString(margin, y, f"MwSt. {invoice.tax}%")
        p.drawRightString(width - margin, y, f"0,00   EURO")
        y += 30
        for line_y_offset in [2, 4, -10]:
            p.line(width - margin , y + line_y_offset, margin, y + line_y_offset)
        p.setFont("Helvetica-Bold", 11)
        p.drawString(margin, y, "Summe")
        p.drawRightString(width - margin, y, f"{invoice.value}   EURO")
    else: # netto-verkauf EU/nicht-EU
        p.setFont("Helvetica-Bold", 12)
        p.drawString(margin, y, "Fahrzeugpreis/Summe")
        p.setFont("Helvetica-Bold", 12)
        p.drawRightString(width - margin, y, f"{invoice.value}   EURO")


    y += 50
    p.setFont("Helvetica-Bold", 11)
    p.drawString(margin, y, "Dieser Rechnungsbetrag ist sofort fällig.")
    y += 12
    p.setFont("Helvetica", 11)
    p.drawString(margin, y, "Lieferdatum entspricht Rechnungsdatum.")
    y += 12
    p.drawString(margin, y, f"Goslar, den {convert_date(invoice.date)}")
    y += 12
    payment = "Betrag wird auf das untenstehende Geschäftskonto überwiesen." if invoice.payment == Invoice.PAYMENT_TRANSFER else "Betrag in bar erhalten."
    p.drawString(margin, y, payment)
    if invoice.terms in [Invoice.TERMS_4_EU]:
        y += 12
        p.drawString(margin, y, "Händlergeschäft, ohne Sachmangelhaftung.")

    y += 25
    if invoice.terms == Invoice.TERMS_25a_DIFF:
        p.drawString(margin, y, "Gebrauchtgegenstände/Sonderregelung Kein Umsatzsteuerausweis")
        y += 12
        p.drawString(margin, y, "gemäß § 25 a UStG möglich.")
    elif invoice.terms == Invoice.TERMS_6a_IGL:
        p.drawString(margin, y, "Innergemeinschaftliche Lieferung, steuerfrei gemäß § 6a Abs. 1 UStG i.V.m. § 4 Nr. 1b UStG.")
    elif invoice.terms == Invoice.TERMS_4_NON_EU:
        p.drawString(margin, y, "Steuerfreie Auslieferung nach § 4 Nr. 1a i.V.m. § 6 UStG. Mit Erhalt der Ausfuhrbescheinigung")
        y += 12
        p.drawString(margin, y, f"wird die angefallene Steuer erstattet und der Kaufpreis auf {brutto_to_netto(invoice.value, invoice.tax)}€  gemindert.")
    elif invoice.terms == Invoice.TERMS_4_EU:
        p.drawString(margin, y, "Innergemeinschaftliche Lieferung nach § 4 Nr. 1b i.V.m. § 6a UStG.")
    
    y += 60
    if invoice.terms in [Invoice.TERMS_4_EU, Invoice.TERMS_4_NON_EU]:
        sign_line_length = 150
        p.drawCentredString(margin + (sign_line_length // 2), y, "Käufer")
        p.line(margin, y - 10, margin + sign_line_length, y - 10)
        p.drawCentredString(width - margin - (sign_line_length // 2), y, "Verkäufer")
        p.line(width - margin, y - 10, width - margin - sign_line_length, y - 10)
    else:
        p.drawCentredString(width // 2, y, "Wir wünschen Ihnen jederzeit eine gute Fahrt!")

    text = p.beginText()
    text.setFont("Helvetica-Bold", 8)
    text.setTextOrigin(margin, height - 90)
    text.textLines(prefs["Bankverbindung"])
    p.drawText(text)

    p.setFont("Helvetica-Bold", 8)
    p.drawCentredString(width // 2, height - 90, "Inhaber:")
    p.drawCentredString(width // 2, height - 80, prefs["Inhaber"])

    p.drawRightString(width - margin, height - 90, f"Steuernummer: {prefs['Steuernummer']}")
    p.drawRightString(width - margin, height - 80, f"USt-ID-Nr.: {prefs['UStIDNr']}")

    p.showPage()
    p.save()

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, filename=f"rechnung-{invoice.number}.pdf")  # TODO as_attachment=True für öffnen und runterladen