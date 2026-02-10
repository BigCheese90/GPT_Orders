from typing import Union, List

import time
import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
import pandas as pd
import json
from chatGptHelper import parse_pdf_to_text
from chatgpt import create_csv_from_email
from config import BASE_DIR
from datetime import datetime
import re
import wawiImport
import uvicorn
app = FastAPI()
origins = ["https://localhost:8432",
           "https://192.168.31.180:8432"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows specific domains
    allow_credentials=True,
    allow_methods=["*"],              # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],              # Allows all headers (Content-Type, etc.)
)




class Attachment(BaseModel):
    name: str
    contentType: str
    contentBytes: str


class EmailItem(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    attachments: List[Attachment]
    @field_validator("subject", "body", mode="before")
    def validate_subject(cls, value) -> str:
        if isinstance(value, str):
            return value
        else:
            return ""

class ImportItem(BaseModel):
    type: str
    df: List



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/analyse_email")
def test_item(email_item: EmailItem):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    clean_subject = re.sub(r'[^\w\s-]', '', email_item.subject)
    filename = timestamp + "_" + clean_subject

    order_path = BASE_DIR / "Api_Orders" / filename
    order_path.mkdir(parents=True, exist_ok=True)

    pdf_text = ""
    with open(order_path / "emailBody.txt", "w", encoding="utf-8") as f:
        f.write(email_item.body)
    for att in email_item.attachments:
        file_data = base64.b64decode(att.contentBytes)


        with open(order_path / f"{att.name}", "wb") as f:
            f.write(file_data)

        if att.name.lower()[-4:] == ".pdf":
            pdf_text = parse_pdf_to_text(order_path / f"{att.name}")
            print(pdf_text)

    df = create_csv_from_email(email_item.subject, email_item.body, pdf_text)
    df.to_csv(order_path / "df.csv", index=False)
    print(df)
    df = df.to_dict(orient="records")

    return {"message": "Item successfully uploaded",
            "df": df}

@app.post("/test_df")
def test_df():
    df = pd.read_csv("testdf.csv", na_values = "none")
    print(df)
    time.sleep(2)
    df = df.to_json(orient="records")
    print(df)
    return {"message": "Item successfully uploaded",
            "df": json.loads(df)}
    print(df)

@app.post("/import")
def import_order(import_data: ImportItem):
    print(import_data.type)
    df = pd.DataFrame(import_data.df)
    print(df)
    if import_data.type == "order":
        df.to_csv("\\\\192.168.31.10\\Office\\Anleitungen\\Stuff\\EmailBestellImport.csv", sep=";", index=False)
        result = wawiImport.GPTBestellImport()
        print(result)
    if import_data.type == "offer":
        df.to_csv("\\\\192.168.31.10\\Office\\Anleitungen\\Stuff\\EmailAngebotImport.csv", sep=";", index=False)
        result = wawiImport.GPTAngebotImport()
        print(result)
    return {"message": "Item successfully uploaded",}

app.mount("/frontend", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("api:app",
                host="0.0.0.0",
                port=8432,
                reload=True,
                ssl_keyfile="./localhost+2-key.pem",
                ssl_certfile="./localhost+2.pem")