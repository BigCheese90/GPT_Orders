from rapidfuzz import fuzz, process
import pandas as pd
from addressFinder import find_address_number

if __name__ == "__main__":
    order = {
        'name': 'CANCOM a+d IT Solutions GmbH',
        "street": "Heinrich-Bablik-Straße 17",
        "zip": "2345"
    }
    print(find_address_number(order, is_customer=True))

