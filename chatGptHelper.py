
import pdfplumber
from pydantic import BaseModel, field_serializer, field_validator, constr
from datetime import date, datetime


# schema = {
#     "type": "object",
#     "properties": {
#         "order_id": {"type": "string"},
#         "customer_name": {"type": "string"},
#         "order_date": {"type": "string"},
#         "currency": {"type": "string"},
#         "items": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "properties": {
#                     "position": {"type": "integer"},
#                     "article": {"type": "string"},
#                     "description": {"type": "string"},
#                     "quantity": {"type": "number"},
#                     "unit": {"type": "string"},
#                     "unit_price": {"type": "number"},
#                 },
#                 "required": ["position", "description", "quantity"]
#             }
#         }
#     },
#     "required": ["order_id", "items"]
# }

class OrderItem(BaseModel):
    Bestellnummer: str
    Artikelnummer: int
    sku: str
    manufacturer_product_number: str
    description: str
    quantity: float
    unit_price: float
    möglicheArtikelnummern: list[str]

    model_config = {
        "json_schema_extra": {
            "additionalProperties": False
        }
    }

class Address(BaseModel):
    name: str
    street: str
    zip: str
    city: str



class Order(BaseModel):
    order_id: str
    customer_name: str
    order_date: date
    referenz: str
    items: list[OrderItem]
    invoice_address: Address
    delivery_address: Address
    model_config = {
        "json_schema_extra": {
            "additionalProperties": False
        }
    }

    @field_validator("order_date")
    def validate_order_date(cls, v):
        current_year = date.today().year
        if not (date(current_year-3, 1, 1) <= v <= date(current_year, 12, 31)):
            raise ValueError("order_date must be between 2020 and 2035.")
        return v


def parse_pdf_to_text(pdf_path: str) -> str:
    with (pdfplumber.open(str(pdf_path)) as pdf):
        pdf_text = ""
        for page in pdf.pages:
            pdf_text += page.extract_text()
    return pdf_text


if __name__ == "__main__":
    item = OrderItem(
        sku="1",
        manufacturer_product_number="1",
        description="Bestell #1",
        quantity=1.0,
        unit_price=1.0, )
    address = Address(
        name="Bestell #1",
        street="Bestell #1",
        zip="9101",
        city="Bestell #1",
    )
    o = Order(
        order_id="123",
        customer_name="John",
        order_date=date(2021, 3, 1),
        items=[item],
        invoice_address=address,
        delivery_address=address,

    )
