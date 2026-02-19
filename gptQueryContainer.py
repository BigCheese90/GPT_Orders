
from openai.types.responses.parsed_response import ParsedResponse
from pydantic import BaseModel, model_validator, ConfigDict
from datetime import datetime, date
from typing_extensions import Self
import logging
import pandas as pd
from chatGptHelper import Order, Address
from transformOrder import transform_order, validate_response_and_extract_data
from addressFinder import add_address_number, find_customer_address, find_delivery_address
from articleNumbers import validate_article_number, find_allnet_article_number


class GPTQueryContainer(BaseModel):

    gpt_response: ParsedResponse[Order]
    validated_order: Order | None = None
    transformed_order: Self | None = None

    customer_address: Address | None = None
    customer_number: str | None = None
    customer_score: float | None = None
    delivery_address: Address | None = None
    delivery_address_number: str | None = None
    delivery_address_score: float | None = None
    df: list[dict] | None = None



    @model_validator(mode="after")
    def validate_order(self) -> Self:
        self.validated_order = validate_response_and_extract_data(self.gpt_response)
        return self

    @model_validator(mode="after")
    def transform_order(self) -> Self:
        order_validated = self.validated_order

        customer_result = find_customer_address(order_validated.invoice_address)
        self.customer_number = customer_result.address_number
        self.customer_address = customer_result.address
        self.customer_score = customer_result.address_score

        delivery_address_result = find_delivery_address(order_validated.delivery_address, customer_result)
        self.delivery_address_number = delivery_address_result.address_number
        self.delivery_address = delivery_address_result.address
        self.delivery_address_score = delivery_address_result.address_score

        #self.date = order_validated.order_date
        order_date = order_validated.order_date
        order_date_str: str = order_date.strftime("%d.%m.%Y")
        order_items= []

        for i, item in enumerate(order_validated.items):
            article_number = find_allnet_article_number(item)
            if article_number == "Not Found":
                continue
            position = {
                "Kundennummer": self.customer_number,
                "Pos": i + 1,
                "Artikelnummer": article_number,
                "Menge": item.quantity,
                "Preis": "",
                "Belegtext": f"e-mail Best. #{order_validated.order_id} vom {order_date_str}" if i == 0 else "",
                "Referenz": clean_strings_for_export(order_validated.referenz) if i == 0 else "",
                "Datum": order_date_str,
                "Liefer-ID": self.delivery_address_number,
                "Land": "A",
                "PLZ": order_validated.delivery_address.zip,
                "Ort": order_validated.delivery_address.city,
                "Strasse": order_validated.delivery_address.street,
                "Name1": order_validated.delivery_address.name,
                "Name2": ""
            }
            order_items.append(position)


        logging.info(order_validated)
        self.df = order_items
        return self


def clean_strings_for_export(string):
    string = string.replace(";",",")
    string = string.replace('"',"'")
    return string