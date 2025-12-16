from rapidfuzz import fuzz
import pandas as pd
from config import BASE_DIR
def normalize(s: str) -> str:
    if not s:
        return ""
    try:
        s = s.lower().strip()
    except Exception as e:
        print(s)
        print(e)
    replacements = {
        "straße": "strasse",
        "str.": "strasse",
        ".": "",
        "-": ""
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    return " ".join(s.split())

def score_address(order, customer):
    # order / customer sind dicts mit name, street, house_no, zip, city

    name_o = normalize(order["name"])
    street_o = normalize(order["street"])
    name_c = normalize(customer["Firmenname_1"])
    street_c = normalize(customer["Strasse"])

    name_score = fuzz.token_sort_ratio(name_o, name_c)
    street_score = fuzz.token_sort_ratio(street_o, street_c)


    zip_exact = 100 if order["zip"] == customer["Plz"] else 0

    total = (
        0.5 * name_score +
        0.5 * street_score

    )
    if total > 80:
         print(name_score, street_score, zip_exact, total)
    return total

def find_best_match(order, customers):
    best = None
    best_score = -1

    # Blocking: nur gleiche PLZ
    candidates = [c for c in customers if c["Plz"] == order["zip"]]

    for c in candidates:
        s = score_address(order, c)
        if s > best_score:
            best_score = s
            best = c

    return best, best_score

def special_customers(address: pd.DataFrame):
    row = address[address.Nummer == "237889"].copy()
    row["Firmenname_1"] = "Technikladen.at"
    address = pd.concat([address, row], ignore_index=True)
    row  = address[address.Nummer == "236318"].copy()
    row["Firmenname_1"] = "PKE Energy Automation GmbH"
    address = pd.concat([address, row], ignore_index=True)
    return address

def find_address_number(order, is_customer=False):
    address = pd.read_csv(BASE_DIR / "Addressenstamm.csv", sep=";", na_filter=False)
    if is_customer:
        address = address[address.iloc[:, 7] == 1 ]
    address = special_customers(address)
    customers = address.to_dict(orient="records")

    test = find_best_match(order, customers)
    if test[1] > 85:
        return test[0]["Nummer"]
    else:
        return 0

def add_address_number(customer, delivery_address):
    address_data = pd.read_csv(BASE_DIR / "Addressenstamm.csv", sep=";")
    delivery_number_base = str(customer) +"-L"
    i = 0
    while True:
        new_delivery_number = delivery_number_base + str(i)
        if new_delivery_number not in address_data["Nummer"].values:
            break
        i += 1
    new_row = {"Nummer": new_delivery_number,
               "Firmenname_1": delivery_address["name"],
               "Strasse": delivery_address["street"],
               "Plz": delivery_address["zip"],
               "Ort": delivery_address["city"],
               "Ist_Kunde": 0}
    new_row = pd.DataFrame(pd.Series(new_row)).T
    address_data = pd.concat([address_data, new_row], ignore_index=True)
    address_data['Ist_Kunde'] = address_data['Ist_Kunde'].astype('Int64')
    address_data.to_csv(BASE_DIR / "Addressenstamm.csv", index=False, sep=";")
    return new_delivery_number

