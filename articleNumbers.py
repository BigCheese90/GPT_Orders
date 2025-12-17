import pandas as pd
from config import ARTICLE_CSV


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


if __name__ == "__main__":
    print(validate_article_number("5060408464236"))