import pandas as pd
from config import ARTICLE_CSV
from chatGptHelper import OrderItem


def validate_article_number(article_number: str) -> str:
    article_number = article_number.lower()
    data = pd.read_csv(ARTICLE_CSV,
                                  sep=";",
                                  dtype={"AllnetArtikelNummer": str,
                                         "HerstellerArtikelNummer": str}, on_bad_lines='skip')
    data['AllnetArtikelNummer'] = data['AllnetArtikelNummer'].apply(lambda x:x.lower() if type(x) == str else x)
    data['HerstellerArtikelNummer'] = data['HerstellerArtikelNummer'].apply(lambda x: x.lower() if type(x) == str else x)
    if article_number in data.AllnetArtikelNummer.values:
        return article_number
    match_manufacturer = data[data.HerstellerArtikelNummer == article_number]
    if match_manufacturer.shape[0] == 1:
        return match_manufacturer.AllnetArtikelNummer.values[0]
    else:
        return "Not Found"
def validate_single_article_number(article_number: str, article_list: pd.DataFrame) -> str:
    print("validating ", article_number)
    if len(article_number) < 3:
        print("too short")
        return "Not Found"

    article_number = article_number.lower()
    if article_number in article_list.AllnetArtikelNummer.values:
        print("found ", article_number)
        return article_number
    match_manufacturer = article_list[article_list.HerstellerArtikelNummer == article_number]
    if match_manufacturer.shape[0] == 1:
        article_number = match_manufacturer.AllnetArtikelNummer.values[0]
        print("found ", article_number)
        return article_number
    else:
        return "Not Found"

def find_allnet_article_number(item: OrderItem) -> tuple[str, str]:
    data = pd.read_csv(ARTICLE_CSV,
                       sep=";",
                       dtype={"AllnetArtikelNummer": str,
                              "HerstellerArtikelNummer": str}, on_bad_lines='skip')
    data['AllnetArtikelNummer'] = data['AllnetArtikelNummer'].apply(lambda x: x.lower() if type(x) == str else x)
    data['HerstellerArtikelNummer'] = data['HerstellerArtikelNummer'].apply(
        lambda x: x.lower() if type(x) == str else x)

    possible_numbers = [item.manufacturer_product_number, item.Artikelnummer, item.sku, item.Bestellnummer]
    possible_numbers.extend(item.möglicheArtikelnummern)
    print(possible_numbers)
    for possible in possible_numbers:
        article_number = validate_single_article_number(str(possible), data)
        if article_number != "Not Found":
            article_description = data[data.AllnetArtikelNummer == article_number].at[0, "Artikelbeschreibung"]
            return article_number, article_description

    return "Not Found", ""




if __name__ == "__main__":
    data = pd.read_csv(ARTICLE_CSV,
                       sep=";",
                       dtype={"AllnetArtikelNummer": str,
                              "HerstellerArtikelNummer": str}, on_bad_lines='skip')
    data['AllnetArtikelNummer'] = data['AllnetArtikelNummer'].apply(lambda x: x.lower() if type(x) == str else x)
    data['HerstellerArtikelNummer'] = data['HerstellerArtikelNummer'].apply(
        lambda x: x.lower() if type(x) == str else x)
    print(validate_single_article_number("SW/SBC/10S/10-250", data))