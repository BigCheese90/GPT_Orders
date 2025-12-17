from rapidfuzz import fuzz, process
import pandas as pd
from addressFinder import find_address_number

if __name__ == "__main__":
    order = {
        'name': 'NEUMANN Messgeräte GmbH',
        "street": "Stammersdorfer Straße 60",
        "zip": "1210"
    }
    print(find_address_number(order, is_customer=True))

