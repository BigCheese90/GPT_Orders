/*
 * Copyright (c) Microsoft Corporation. All rights reserved. Licensed under the MIT license.
 * See LICENSE in the project root for license information.
 */
import * as Helper from "./helpers";

/* global document, Office */






Office.onReady(async (info) => {
  if (info.host === Office.HostType.Outlook) {
    console.log("ready")
    let importData: any[] = [];
    let exportData = {
      type: "",
      df: [],
    }
    document.getElementById("sideload-msg").style.display = "none";
    document.getElementById("app-body").style.display = "flex";
    document.getElementById("run").onclick = run;
    document.getElementById("send-offer-to-api").onclick = async () => {exportData = await Helper.sendOffer(importData)};
    document.getElementById("send-order-to-api").onclick = async () => {exportData = await Helper.sendOrder(importData)};
    document.getElementById("confirm-no").onclick = Helper.cancelSend;
    document.getElementById("confirm-yes").onclick = () => {Helper.sendToWawi(exportData)};

    const item = Office.context.mailbox.item;
    const attachmentContainer = document.getElementById("attachment-list")
    const attachments = await Helper.getAttachments(item)
    attachments.forEach((att) => {
      if (att.contentType == "application/pdf" || att.contentType == "application/x-pdf" ) {
        attachmentContainer.innerHTML += `
          <div class="selection-item">
              <input type="checkbox" id=${att.id} class="attachment-checkbox" checked>
              <label for = ${att.id}>${att.name}</label>
          </div>
        `
      }
    });
  }
});


export async function run() {
  /**
   * Insert your Outlook code here
   *
   *
   */
  Helper.showLoader("Daten werden geladen...");

  const item = Office.context.mailbox.item;
  const headerRow = document.getElementById("header-row");
  const tableBody = document.getElementById("table-body");
  headerRow.innerHTML = "";
  tableBody.innerHTML = "";





  const body = await Helper.getBody(item);
  const attachments = await Helper.getAttachments(item);
  const attachmentSelection = document.querySelectorAll('.attachment-checkbox:checked');
  const subjectChecked = document.getElementById('include-subject') as HTMLInputElement
  const bodyChecked = document.getElementById('include-body') as HTMLInputElement

  const payload = {
    subject: subjectChecked.checked ? item.subject : null,
    body: bodyChecked.checked ? body: null,
    attachments: []
  }
  attachmentSelection.forEach(checked => {
    const target = attachments.find(item => item.id === checked.id);
    payload.attachments.push(target);
  })


  try {
    const response = await fetch("https://192.168.31.180:8432/analyse_email", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!result.df || result.df.length===0) {
      Helper.showError("Keine Artikel gefunden in Bestellung gefunden");
      return;
    }
    Helper.createTable(result.df)
    Helper.fillInfo(result.df)

    Helper.showContent();

    importData = result.df;

    const buttons = document.getElementById("options")
    buttons.style.display = "flex";


    console.log("Success", result.df);
  } catch (error) {
    Helper.showError("Fehler beim Laden der Daten.")
    console.log("Error:", error);
  }
}
