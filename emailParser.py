import win32com.client
from chatGptHelper import parse_pdf_to_text
from chatgpt import create_csv_from_email
#from Wawiimport import GPTBestellImport
from config import BASE_DIR



def main():
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.Folders("ALLNET Österreich GmbH").Folders("Posteingang")
    print(inbox, inbox.Folders)
    target = inbox.Folders("Email-Bestellungen")
    inbox = inbox.Folders("BestellImport")
    save_folder = BASE_DIR / "Bestellungen"
    messages = inbox.Items
    if messages.Count == 0:
        return
    message = messages.GetFirst()

    print(message.subject)
    print(message.body)

    pdf_text = ""
    for attachment in message.attachments:
        if attachment.filename[-4:].lower() == ".pdf":
            file_name = save_folder / attachment.filename
            attachment.SaveAsFile(file_name)
            pdf_text = parse_pdf_to_text(file_name)
            break

    df = create_csv_from_email(message.subject, message.body, pdf_text)

    message.Move(target)
    #GPTBestellImport()
    return df


if __name__ == "__main__":
    df = main()



