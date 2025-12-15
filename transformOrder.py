import pandas as pd
from datetime import datetime
from addressFinder import find_address_number
from articleNumbers import validate_article_number
import logging
import json

def transform_order(data):

    customer_number = find_address_number(data["invoice_address"], is_customer=True)
    delivery_address_number = find_address_number(data["delivery_address"])
    if "" in data["delivery_address"]:
        data["delivery_address"] = data["invoice_address"]
    delivery_address_number = find_address_number(data["delivery_address"])
    date = data["order_date"]
    date = datetime.strptime(date, "%Y-%m-%d").date()
    date = date.strftime("%d.%m.%Y")
    order = []
    for i, item in enumerate(data["items"]):
        article_number = validate_article_number(item["manufacturer_product_number"])
        if article_number == "Not Found":
            article_number = validate_article_number(str(item["Artikelnummer"]))
        if article_number == "Not Found":
            article_number = validate_article_number(item["sku"])
        if article_number == "Not Found":
            article_number = validate_article_number(item["Bestellnummer"])
        if article_number == "Not Found":
            for possibles in item["möglicheArtikelnummern"]:
                article_number = validate_article_number(possibles)
                if article_number != "Not Found":
                    break
        if article_number == "Not Found":
            continue
        position = {
            "Kundennummer": customer_number,
            "Pos": i + 1,
            "Artikelnummer": article_number,
            "Menge": item["quantity"],
            "Preis": "",
            "Belegtext": f"e-mail Best. #{data['order_id']} vom {date}" if i == 0 else "",
            "Referenz": data["referenz"],
            "Datum": date,
            "Liefer-ID": delivery_address_number,
            "Land": "A",
            "PLZ": data["delivery_address"]["zip"],
            "Ort": data["delivery_address"]["city"],
            "Strasse": data["delivery_address"]["street"],
            "Name1": data["delivery_address"]["name"],
            "Name2": ""
        }
        order.append(position)

    df = pd.DataFrame.from_dict(order)
    logging.info(df)
    return df

def validate_response_and_extract_data(response):
    try:
        data = json.loads(response.output[-1].content[0].text)
        logging.info(data)
        return data
    except Exception as e:
        logging.critical(e)
        logging.critical(response)
        return  None