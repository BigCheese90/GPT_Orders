from rapidfuzz import fuzz, process
import pandas as pd
from addressFinder import find_address_number

if __name__ == "__main__":
    order = {
        'name': 'TechnikLaden.at',
        "street": "Eltzgasse 3",
        "zip": "2620"
    }
    print(find_address_number(order, is_customer=True))

