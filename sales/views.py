import io
import logging
from decimal import Decimal

from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from dynamic_preferences.registries import global_preferences_registry

from .models import Invoice


def index(_):
    return HttpResponse("Hallo Welt. Hier werden Autos verkauft.")

def brutto_to_netto(brutto_val: Decimal, tax: int):
    return round(brutto_val / Decimal((100 + tax) / 100), 2)

def drawField(p: canvas.Canvas, description: str, value: str, x: int, y: int, length: int):
    p.setFont("Helvetica", 11)
    p.drawString(x, y, value)
    p.line(x, y + 2, x + length, y + 2)
    p.setFont("Helvetica", 7)
    p.drawString(x, y + 9, description)

# It is said that reportlab is not thread-safe. We shall ignore that here since parallel usage is not to be expected.
def pdf(_, id: int):
    logging.getLogger(__name__).info("######## Autohandel: Generating PDF ########")
    prefs = global_preferences_registry.manager()

    invoice = Invoice.objects.get(pk=id)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
    width, height = A4
    margin = 60

    seller_name = prefs["Verkäufer"]
    p.setFont("Helvetica-Bold", 16)
    p.drawString(margin, margin + 10, seller_name)

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

    y += 55
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
    p.drawString(margin + right_column_offset, y, Invoice.short_date(invoice.year))
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
    p.drawString(margin, y, f"Goslar, den {Invoice.short_date(invoice.date)}")
    y += 12
    payment = "Betrag wird auf das untenstehende Geschäftskonto überwiesen." if invoice.payment == Invoice.PAYMENT_TRANSFER else "Betrag in bar erhalten."
    p.drawString(margin, y, payment)
    if invoice.terms in [Invoice.TERMS_4_EU, Invoice.TERMS_4_NON_EU]:
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

    p.setFont("Helvetica-Bold", 16) 
    y = margin
    p.drawCentredString(width // 2, y, "Verbindlicher Kaufvertrag für gebrauchte Kraftfahrzeuge und Anhänger")

    y += 30
    rect_start_y = y
    rect_width = (width // 2) - margin - 5
    p.rect(margin - 3, y - 16, rect_width, 130)
    right_rect_start_x = width - margin + 3 - rect_width
    p.rect(right_rect_start_x, y - 16, rect_width, 130)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin, y, "Käufer")
    buyer_field_len = 210
    drawField(p, "Telefon", invoice.telephone, margin + 70, y, 140)
    y += 25
    drawField(p, "Name, Vorname/Firma", f"{invoice.title} {invoice.client_name}", margin, y, buyer_field_len)
    y += 25
    drawField(p, "Straße", f"{invoice.street}", margin, y, buyer_field_len)
    y += 25
    drawField(p, "PLZ, Ort", f"{invoice.area_code} {invoice.city}", margin, y, buyer_field_len)
    y += 25
    drawField(p, "Ausweis- u./od. Steuernr.", f"{invoice.id_tax_id}", margin, y, buyer_field_len)
    y_after_rects = y + 10

    y = rect_start_y
    x = right_rect_start_x + 2
    p.setFont("Helvetica-Bold", 14)
    p.drawString(x, y, "Verkäufer")
    y += 20
    p.drawCentredString(x + (rect_width // 2), y, seller_name)
    y += 5
    p.setFont("Helvetica", 11)
    for i, line in enumerate(address):
        y += 11
        p.drawCentredString(x + (rect_width // 2), y, line)

    y = y_after_rects + 20
    text = p.beginText()
    text.setFont("Helvetica", 10)
    text.setTextOrigin(margin, y)
    text.textLines("Der Verkäufer verkauft hiermit an den Käufer das unten beschriebene gebrauchte Kraftfahrzeug / Anhänger\n aufgrund der umseitigen Bedingungen, die sorgfältig durchgelesen und vollinhaltlich angenommen werden.")
    p.drawText(text)

    y += 25

    p.rect(margin, y, width - (2 * margin), 150)
    x = margin + 5
    y += 20
    drawField(p, "Hersteller, Nr.", invoice.make, x, y, 100)
    drawField(p, "Typ, Nr.", invoice.model, x + 120, y, 120)
    drawField(p, "Fahrgestellnummer", invoice.serial_number, x + 260, y, 200)
    y += 25
    drawField(p, "Kfz.-Brief Nr.", invoice.letter_no, x, y, 120)
    drawField(p, "Erstzulassung", Invoice.short_date(invoice.year), x + 140, y, 80)
    drawField(p, "TÜV / AU", invoice.tuev_au, x + 240, y, 80)
    drawField(p, "Kfz.-Kennzeichen", invoice.plate, x + 340, y, 120)
    y += 25
    drawField(p, "Hubraum", invoice.capacity, x, y, 100)
    drawField(p, "PS/kW", invoice.power_output, x + 120, y, 100)
    drawField(p, "km-Stand", str(invoice.odo), x + 240, y, 100)
    drawField(p, "Anzahl ausgeh. Schlüssel", "", x + 360, y, 100)
    y += 25
    p.setFont("Helvetica", 10)
    p.drawString(x, y, "Unfallschaden bekannt:  ja  O  nein  O   falls ja, folgende:    O  Rahmenschaden     Blechschaden  O")
    y += 25
    p.line(x, y, width - x, y)

    y += 50
    drawField(p, "Liefertermin/Zulassung", "", margin, y, 200)
    drawField(p, "MwSt.satz", f"{invoice.tax}    %", int(width - margin - 55), y, 55)
    y += 25
    drawField(p, "Zubehör", "", margin, y, 350)
    drawField(p, "Preis", "", margin + 360, y, 55)
    drawField(p, "MwSt.", "", margin + 420, y, 55)
    y += 25
    drawField(p, "Nebenleistungen (z.B. Zulassungskosten, o.ä)", "", margin, y, 350)
    drawField(p, "Preis", "", margin + 360, y, 55)
    drawField(p, "MwSt.", "", margin + 420, y, 55)
    y += 25
    p.setFont("Helvetica", 10)
    p.drawString(margin, y, "O  für Vorsteuerabzugsberechtigte kein Vorsteuerabzug möglich § 25 a UStG")
    y += 15
    p.drawString(margin, y, "O  zzgl. USt. _______ % (Option zur Regelbesteuerung)")
    p.line(width - margin, y, width - margin - 130, y)
    y += 25
    drawField(p, "Gesamtbetrag", "", int(width - margin - 130), y, 130)
    y += 15
    drawField(p, "Gesamtbetrag in Worten", "", margin, y, 250)
    y += 30
    drawField(p, "Zahlungsvereinbarung", "", margin, y, int(width - (2 * margin)))
    y += 30
    drawField(p, "Anzahlung", "", margin, y, int(width - (2 * margin)))
    y += 30
    drawField(p, "O  Besondere Vereinbarungen, falls der Käufer als Unternehmer handelt", "", margin, y, int(width - (2 * margin)))
    y += 30
    drawField(p, "O  Zusätzliche Vereinbarungen und Zusicherungen, wie z.B. Austauschmotor usw.", "", margin, y, int(width - (2 * margin)))
    y += 20
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(width // 2, y, "!!! Alle Zusatzvereinbarungen bedürfen der Schriftform !!!")
    y += 20
    p.setFont("Helvetica", 10)
    p.drawString(margin, y, "Bestandteil dieses Vertrages sind folgende Analgen:")
    y += 20
    p.drawCentredString(width // 2, y, "O  Garantieunterlagen Nr. _______    O  Zustandsbericht/Übergabeprotokoll    O  Prüfsiegel/-urkunde")
    y += 40
    drawField(p, "Ort, Datum", "", margin, y, 130)
    drawField(p, "Unterschrift Käufer", "", margin + 150, y, 150)
    drawField(p, "Unterschrift Verkäufer", "", margin + 320, y, 150)

    p.showPage()

    y = margin - 20
    p.drawCentredString(width // 2, y, "Gebrauchtwagen-Verkaufsbedingungen (Kraftfahrzeuge und Anhänger)")
    y += 10
    p.setFont("Helvetica", 8)
    p.drawCentredString(width // 2, y, "Unverbindliche Empfehlung des Zentralverbandes Deutsches Kraftfahrzeuggewerbe e. V. (ZDK) (Stand 01/22)")

    y += 15
    text = p.beginText()
    text.setFont("Helvetica", 6)
    text.setTextOrigin(margin, y)
    agb_text = """
    I. Vertragsabschluss/Übertragung von Rechten und Pflichten des Käufers
    1. Der Käufer ist an die Bestellung höchstens bis 10 Tage, bei Nutzfahrzeugen bis 2 Wochen gebunden. Der Kaufvertrag ist abgeschlossen, wenn der Verkäufer die Annahme 
    der Bestellung des näher bezeichneten Kaufgegenstandes innerhalb der jeweils genannten Fristen in Textform bestätigt oder die Lieferung ausführt. Der Verkäufer ist jedoch
    verpflichtet, den Besteller unverzüglich zu unterrichten, wenn er die Bestellung nicht annimmt.
    2. Übertragungen von Rechten und Pflichten des Käufers aus dem Kaufvertrag bedürfen der Zustimmung des Verkäufers in Textform. Dies gilt nicht für einen auf Geld gerichteten
    Anspruch des Käufers gegen den Verkäufer. Für andere Ansprüche des Käufers gegen den Verkäufer bedarf es der vorherigen Zustimmung des Verkäufers dann nicht, wenn beim
    Verkäufer kein schützenswertes Interesse an einem Abtretungsausschluss besteht oder berechtigte Belange des Käufers an einer Abtretbarkeit des Rechtes das schützenswerte
    Interesse des Verkäufers an einem Abtretungsausschluss überwiegen.

    II. Zahlung
    1. Der Kaufpreis und Preise für Nebenleistungen sind bei Übergabe des Kaufgegenstandes und Aushändigung oder Übersendung der Rechnung zur Zahlung fällig.
    2. Gegen Ansprüche des Verkäufers kann der Käufer nur dann aufrechnen, wenn die Gegenforderung des Käufers unbestritten ist oder ein rechtskräftiger Titel vorliegt.
    Hiervon ausgenommen sind Gegenforderungen des Käufers aus demselben Kaufvertrag. Ein Zurückbehaltungsrecht kann er nur geltend machen, soweit es auf Ansprüchen aus
    demselben Vertragsverhältnis beruht.

    III. Lieferung und Lieferverzug
    1. Liefertermine und Lieferfristen, die verbindlich oder unverbindlich vereinbart werden können, sind in Textformanzugeben. Lieferfristen beginnen mit Vertragsabschluss.
    2. Der Käufer kann zehn Tage, bei Nutzfahrzeugen zwei Wochen, nach Überschreiten eines unverbindlichen Liefertermins oder einer unverbindlichen Lieferfrist den Verkäufer
    auffordern, zu liefern. Mit dem Zugang der Aufforderung kommt der Verkäufer in Verzug. Hat der Käufer Anspruch auf Ersatz eines Verzugsschadens, beschränkt sich dieser bei
    leichter Fahrlässigkeit des Verkäufers auf höchstens 5% des vereinbarten Kaufpreises.
    3. Will der Käufer darüber hinaus vom Vertrag zurücktreten und/oder Schadensersatz statt der Leistung verlangen, muss er dem Verkäufer nach Ablauf der betreffenden Frist
    gemäß Ziffer 2, Satz 1 dieses Abschnitts eine angemessene Frist zur Lieferung setzen. Hat der Käufer Anspruch auf Schadensersatz statt der Leistung, beschränkt sich der
    Anspruch bei leichter Fahrlässigkeit auf höchstens 10% des vereinbarten Kaufpreises. Ist der Käufer eine juristische Person des öffentlichen Rechts, ein
    öffentlich-rechtliches Sondervermögen oder ein Unternehmer, der bei Abschluss des Vertrages in Ausübung seiner gewerblichen oder selbständigen beruflichen Tätigkeit handelt,
    sind Schadenersatzansprüche bei leichter Fahrlässigkeit ausgeschlossen. Wird dem Verkäufer, während er in Verzug ist, die Lieferung durch Zufall unmöglich, so haftet er mit
    den vorstehend vereinbarten Haftungsbegrenzungen. Der Verkäufer haftet nicht, wenn der Schaden auch bei rechtzeitiger Lieferung eingetreten wäre.
    4. Wird ein verbindlicher Liefertermin oder eine verbindliche Lieferfrist überschritten, kommt der Verkäufer bereits mit Überschreiten des Liefertermins oder der Lieferfrist
    in Verzug. Die Rechte des Käufers bestimmen sich dann nach Ziffer 2, Satz 3 und Ziffer 3 dieses Abschnitts.
    5. Die Haftungsbegrenzungen und Haftungsausschlüsse dieses Abschnitts gelten nicht für Schäden, die auf einer grob fahrlässigen oder vorsätzlichen Verletzung von Pflichten
    des Verkäufers, seines gesetzlichen Vertreters oder seines Erfüllungsgehilfen beruhen sowie bei Verletzung von Leben, Körper oder Gesundheit.
    6. Höhere Gewalt oder beim Verkäufer oder dessen Lieferanten eintretende Betriebsstörungen, die den Verkäufer ohne eigenes Verschulden vorübergehend daran hindern,
    den Kaufgegenstand zum vereinbarten Termin oder innerhalb der vereinbarten Frist zu liefern, verändern die in Ziffern 1 bis 4 dieses Abschnitts genannten Termine und Fristen
    um die Dauer der durch diese Umstände bedingten Leistungsstörungen. Führen entsprechende Störungen zu einem Leistungsaufschub von mehr als vier Monaten, kann der Käufer vom
    Vertrag zurücktreten. Andere Rücktrittsrechte bleiben davon unberührt.

    IV. Abnahme
    1. Der Käufer ist verpflichtet, den Kaufgegenstand innerhalb von acht Tagen ab Zugang der Bereitstellungsanzeige abzunehmen. Im Falle der Nichtabnahme kann der Verkäufer von
    seinen gesetzlichen Rechten Gebrauch machen.
    2. Verlangt der Verkäufer Schadensersatz, so beträgt dieser 10% des Kaufpreises. Der Schadenersatz ist höher oder niedriger anzusetzen, wenn der Verkäufer einen höheren Schaden
    nachweist oder der Käufer nachweist, dass ein geringerer oder überhaupt kein Schaden entstanden ist.

    V. Eigentumsvorbehalt
    1. Der Kaufgegenstand bleibt bis zum Ausgleich der dem Verkäufer aufgrund des Kaufvertrages zustehenden Forderungen Eigentum des Verkäufers. Ist der Käufer eine juristische
    Person des öffentlichen Rechts, ein öffentlich-rechtliches Sondervermögen oder ein Unternehmer, der bei Abschluss des Vertrages in Ausübung seiner gewerblichen oder selbständigen
    beruflichen Tätigkeit handelt, bleibt der Eigentumsvorbehalt auch bestehen für Forderungen des Verkäufers gegen den Käufer aus der laufenden Geschäftsbeziehung bis zum Ausgleich
    von im Zusammenhang mit dem Kauf zustehenden Forderungen. Auf Verlangen des Käufers ist der Verkäufer zum Verzicht auf den Eigentumsvorbehalt verpflichtet, wenn der Käufer
    sämtliche mit dem Kaufgegenstand im Zusammenhang stehende Forderungen unanfechtbar erfüllt hat und für die übrigen Forderungen aus den laufenden Geschäftsbeziehungen eine
    angemessene Sicherung besteht. Während der Dauer des Eigentumsvorbehalts steht das Recht zum Besitz der Zulassungsbescheinigung Teil II dem Verkäufer zu.
    2. Zahlt der Käufer den fälligen Kaufpreis und Preise für Nebenleistungen nicht oder nicht vertragsgemäß, kann der Verkäufer vom Vertrag zurücktreten und/oder bei schuldhafter
    Pflichtverletzung des Käufers Schadensersatz statt der Leistung verlangen, wenn er dem Käufer erfolglos eine angemessene Frist zur Leistung bestimmt hat, es sei denn, die
    Fristsetzung ist entsprechend den gesetzlichen Bestimmungen entbehrlich.
    3. Solange der Eigentumsvorbehalt besteht, darf der Käufer über den Kaufgegenstand weder verfügen noch Dritten vertraglich eine Nutzung einräumen.

    VI. Haftung für Sachmängel und Rechtsmängel
    1. Sofern der Käufer ein Verbraucher im Sinne von § 13 BGB ist, kann eine Verkürzung der zweijährigen Verjährungsfrist für Sachmängel und Rechtsmängel auf nicht weniger als ein
    Jahr ab Ablieferung des Kaufgegenstandes an den Käufer nur wirksam vereinbart werden, wenn der Käufer vor Abgabe seiner Vertragserklärung von der Verkürzung der Verjährungsfrist
    eigens in Kenntnis gesetzt und die Verkürzung im Vertrag ausdrücklich und gesondert vereinbart wird. Für Sach- und Rechtsmängel an Waren mit digitalen Elementen gelten für die
    digitalen Elemente nicht die Bestimmungen dieses Abschnittes, sondern die gesetzlichen Regelungen
    2. Ist der Käufer eine juristische Person des öffentlichen Rechts, ein öffentlich-rechtliches Sondervermögen oder ein Unternehmer, der bei Abschluss des Vertrages in Ausübung
    seiner gewerblichen oder selbständigen beruflichen Tätigkeit handelt, erfolgt der Verkauf unter Ausschluss jeglicher Sach- und Rechtsmängelansprüche.
    Dieser Ausschluss gilt nicht für Schäden, die auf einer grob fahrlässigen oder vorsätzlichen Verletzung von Pflichten des Verkäufers, seines gesetzlichen Vertreters oder seines
    Erfüllungsgehilfen beruhen sowie bei Verletzung von Leben, Körper oder Gesundheit.
    3. Hat der Verkäufer aufgrund der gesetzlichen Bestimmungen für einen Schaden aufzukommen, der leicht fahrlässig verursacht wurde, so haftet der Verkäufer beschränkt: Die Haftung
    besteht nur bei Verletzung vertragswesentlicher Pflichten, etwa solcher, die der Kaufvertrag dem Verkäufer nach seinem Inhalt und Zweck gerade auferlegen will oder deren Erfüllung
    die ordnungsgemäße Durchführung des Kaufvertrages überhaupt erst ermöglicht und auf deren Einhaltung der Käufer regelmäßig vertraut und vertrauen darf. Diese Haftung ist auf den
    bei Vertragsabschluss vorhersehbaren typischen Schaden begrenzt. Ausgeschlossen ist die persönliche Haftung der gesetzlichen Vertreter, Erfüllungsgehilfen und Betriebsangehörigen
    des Verkäufers für von ihnen durch leichte Fahrlässigkeit verursachte Schäden. Dies gilt nicht für Schäden, die auf einer grob fahrlässigen oder vorsätzlichen Verletzung von
    Pflichten des Verkäufers, seines gesetzlichen Vertreters oder seines Erfüllungsgehilfen beruhen sowie bei Verletzung von Leben, Körper oder Gesundheit.
    4. Unabhängig von einem Verschulden des Verkäufers bleibt eine etwaige Haftung des Verkäufers bei arglistigem Verschweigen eines Mangels, aus der Übernahme einer Garantie oder eines
    Beschaffungsrisikos und nach dem Produkthaftungsgesetz unberührt.
    5. Soll eine Mängelbeseitigung durchgeführt werden, gilt folgendes:
    a) Ansprüche wegen Sachmängeln hat der Käufer beim Verkäufer geltend zu machen. Bei mündlichen Anzeigen von Ansprüchen ist dem Käufer eine schriftliche Bestätigung über den Eingang
    der Anzeige auszuhändigen.
    b) Wird der Kaufgegenstand wegen eines Sachmangels betriebsunfähig, kann sich der Käufer mit vorheriger Zustimmung des Verkäufers an einen anderen Kfz-Meisterbetrieb wenden.
    c) Für die im Rahmen einer Mängelbeseitigung eingebauten Teile kann der Käufer bis zum Ablauf der Verjährungsfrist des Kaufgegenstandes Sachmängelansprüche auf Grund des
    Kaufvertrages geltend machen. Ersetzte Teile werden Eigentum des Verkäufers.

    VII. Haftung für sonstige Ansprüche
    1. Für sonstige Ansprüche des Käufers, die nicht in Abschnitt VI. „Haftung für Sachmängel und Rechtsmängel“ geregelt sind, gelten die gesetzlichen Verjährungsfristen.
    2. Die Haftung wegen Lieferverzuges ist in Abschnitt III „Lieferung und Lieferverzug“ abschließend geregelt. Für sonstige Schadensersatzansprüche gegen den Verkäufer gelten die
    Regelungen in Abschnitt VI. „Haftung für Sachmängel und Rechtsmängel“, Ziffer 3 und 4 entsprechend.
    3. Wenn der Käufer ein Verbraucher im Sinne von § 13 BGB ist und Vertragsgegenstand auch die Bereitstellung digitaler Inhalte oder digitaler Dienstleistungen ist, wobei das Fahrzeug
    seine Funktion auch ohne diese digitalen Produkte erfüllen kann, gelten für diese digitalen Inhalte oder digitalen Dienstleistungen die gesetzlichen Vorschriften der §§ 327 ff BGB.

    VIII. Gerichtsstand
    1. Für sämtliche gegenwärtigen und zukünftigen Ansprüche aus der Geschäftsverbindung mit Kaufleuten einschließlich Wechsel- und Scheckforderungen ist ausschließlicher Gerichtsstand
    der Sitz des Verkäufers.
    2. Der gleiche Gerichtsstand gilt, wenn der Käufer keinen allgemeinen Gerichtsstand im Inland hat, nach Vertragsabschluss seinen Wohnsitz oder gewöhnlichen Aufenthaltsort aus dem
    Inland verlegt oder sein Wohnsitz oder gewöhnlicher Aufenthaltsort zum Zeitpunkt der Klageerhebung nicht bekannt ist. Im Übrigen gilt bei Ansprüchen des Verkäufers gegenüber dem
    Käufer dessen Wohnsitz als Gerichtsstand.

    IX. Außergerichtliche Streitbeilegung 1. Kfz-Schiedsstellen
    a) Führt der Kfz-Betrieb das Meisterschild „Meisterbetrieb der Kfz-Innung“ oder das Basisschild „Mitgliedsbetrieb der Kfz-Innung“, können die Parteien bei Streitigkeiten aus dem
    Kaufvertrag über gebrauchte Fahrzeuge mit einem zulässigen Gesamtgewicht von nicht mehr als 3,5 t - mit Ausnahme über den Kaufpreis - die für den Sitz des Verkäufers zuständige Kfz-
    Schiedsstelle anrufen. Die Anrufung muss unverzüglich nach Kenntnis des Streitpunktes, spätestens einen Monat nach Ablauf der Verjährungsfrist für Sach- und Rechtsmängel gem.
    Abschnitt VI. durch Einreichung eines Schriftsatzes (Anrufungsschrift) bei der Kfz-Schiedsstelle erfolgen.
    b) Durch die Entscheidung der Kfz- Schiedsstelle wird der Rechtsweg nicht ausgeschlossen.
    c) Durch die Anrufung der Kfz-Schiedsstelle ist die Verjährung für die Dauer des Verfahrens gehemmt.
    d) Das Verfahren vor der Kfz-Schiedsstelle richtet sich nach deren Geschäfts- und Verfahrensordnung, die den Parteien auf Verlangen von der Kfz-Schiedsstelle ausgehändigt wird.
    e) Die Anrufung der Kfz-Schiedsstelle ist ausge- schlossen, wenn bereits der Rechtsweg be- schritten ist. Wird der Rechtsweg während eines Schiedsstellenverfahrens beschritten,
    stellt die Kfz-Schiedsstelle ihre Tätigkeit ein.
    f) Für die Inanspruchnahme der Kfz-Schiedsstelle werden Kosten nicht erhoben.
    2. Hinweis gemäß § 36 Verbraucherstreitbeilegungsgesetz (VSBG)
    Der Verkäufer wird nicht Streitbeilegungsverfahren Verbraucherschlichtungsstelle im Sinne des VSBG teilnehmen und ist hierzu auch nicht verpflichtet.
    """

    text.textLines(agb_text)
    p.drawText(text)

    p.showPage()
    p.save()

    buffer.seek(0)
    download_file = True
    return FileResponse(buffer, as_attachment=download_file, filename=f"rechnung-{invoice.number}.pdf")