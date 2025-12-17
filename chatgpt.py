from openai import OpenAI
import pdfplumber
from chatGptHelper import Order
from config import BASE_DIR
import logging
from dotenv import load_dotenv
import os
from transformOrder import transform_order, validate_response_and_extract_data



logging.basicConfig(filename=BASE_DIR / "Queries.log",
                    encoding="utf-8",
                    filemode="a",
                    format="{asctime} - {levelname} - {message}",
                    style = "{",
                    datefmt = "%Y-%m-%d %H:%M",
                    level=logging.INFO)

def query_gpt(client, email_subject: str, email_body: str, pdf_text: str ):
    instructions = """
    Beginne mit einer kurzen Checkliste (3-7 Punkte), um den Ablauf zur strukturierten Extraktion sicherzustellen. Extrahiere aus dem bereitgestellten Text die für die Bestellung benötigten Daten. Analysiere den Text und identifiziere alle Positionen, für die eine Bestellung erfolgen soll.
    Fokussiere dich auf die Extraktion von Positionsdaten und zusätzlich auf die korrekte Extraktion des Bestelldatums. Achte darauf, bei der Extraktion des Datums nur realistische Datumsangaben zu erfassen (z. B. zwischen 2024 und dem aktuellen Jahr) und keine fehlerhaften oder offensichtlich falschen Daten wie z. B. ein "Bestelldatum im Jahr 1059" auszugeben.
    Für jede gefundene Position sollen folgende Felder ausgegeben werden:
    - menge: Die Stückzahl der gewünschten Position.
    - artikelnummer: Die Artikelnummer, entweder die Hersteller-Artikelnummer (manufacturer_product_number) oder unsere Allnet-Artikelnummer (sku). Falls beide vorhanden sind, gib beide Felder aus. Ist nur eine vorhanden, gib nur diese aus.
    Allnet-Artikelnummern (sku) sind besonders relevant. Sie bestehen aus 5-6 Ziffern. Suche auch explizit in Produktbeschreibungen nach möglichen skus. 
    Extrahiere NUR Daten die in der Bestellung stehen
    Wenn bei einer Position keine Artikelnummer (weder sku noch manufacturer_product_number) gefunden wird, ignoriere diese Position und gib keinen Output dazu aus.
    Trage alles dass möglicherweise eine Artikelnummer sein könnte und bei einem Produkt aufgeführt wird in das Feld mögliche Artikelnummern ein
    Sollte eine Kommission oder Referenz aufgeführt sein, schreibe diese in das Feld Referenz.
    Referenz meistens am Anfang des Dokuments, es handelt sich um einen Namen/Projektnummer, unterscheidet sich aber von der Bestellnummer.
    Extrahiere die Referenz nur wenn es sich von Bestellnummer und Artikelnummern unterscheidet
    Die Referenz steht nicht bei den Artikelpositionen, es sollte sich um maximal 1-2 Zeilen handeln.
    Die folgenden Firmendaten meiner Firma sollen nicht extrahiert werden:
    Allnet Österreich GmbH
    Dr. Erwin Schrödinger Strasse 14
    9500 Villach
    Ebenso ignoriere explizit sämtliche Angaben zu Bankverbindungen, Fußzeilen, AGB, Zahlungsbedingungen und ähnliche administrative Informationen.
    Nach jedem Durchlauf des Extraction-Workflows validiere das Teilergebnis in 1-2 Sätzen. Wenn ein Fehler festgestellt wird (z. B. ungültige oder nicht gefundene Artikelnummer oder ein offensichtlich fehlerhaftes Bestelldatum), führe eine minimale Korrektur durch und wiederhole die Validierung.
    """
    content = f"""
    Subject: {email_subject}
    Body: {email_body}

    <<<
    {pdf_text}
    >>>
    """

    text_input = [{
        "role": "user",
        "content": content
    }]

    response = client.responses.parse(
        model="gpt-5.1",
        instructions=instructions,
        input=text_input,
        text_format=Order,
        # tools=[{
        #     "type": "file_search",
        #     "vector_store_ids": [VECTOR_STORE_ID]
        # }],
        max_output_tokens=2000,
    )

    return response



def create_csv_from_email(email_subject:str, email_body, pdf_text:str = ""):
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    client = OpenAI(api_key=API_KEY)

    response = query_gpt(client, email_subject, email_body, pdf_text)
    print(response.usage)
    data = validate_response_and_extract_data(response)
    df = transform_order(data)
    if df.shape[0] != len(data["items"]):
        logging.info("Mismatch, Querying again")
        response = query_gpt(client, email_subject, email_body, pdf_text)
        data = validate_response_and_extract_data(response)
        df = transform_order(data)

    df.to_csv("\\\\192.168.31.10\\Office\\Anleitungen\\Stuff\\EmailBestellImport.csv", sep=";", index=False)
    return df


if __name__ == "__main__":
    pdf_path = "Bestellung_2025-12-05_B200060073_400360.pdf"
    with (pdfplumber.open(str(pdf_path)) as pdf):
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text()

    subject = "Bestellung B200060073"
    body = """
    Sehr geehrte Damen und Herren,
    
    Anbei die Bestellung B200060073.
    
    Bei Fragen oder Unklarheiten stehen wir Ihnen jederzeit gerne zur Verfügung.
    
     
    Mit freundlichen Grüßen / Best Regards
    
    Sonepar Einkauf
    Email: einkauf@sonepar.at
    Telefon: +43 5 1706 12000
    Sonepar Österreich GmbH, Gaudenzdorfer Gürtel 67, 1120 Wien, Österreich
    Geschäftsführung: Dipl.-Ing.(FH) Uwe Klingsbigl, Thomas Schaffer
    Firmenbuch: FN 176431h, UID-Nummer: ATU47103209, Gerichtsstand: Wien

    """

    df_test = create_csv_from_email(subject, body, pdf_text)
