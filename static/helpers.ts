export async function sendToWawi(exportData) {
    document.getElementById("popup-overlay").style.display = "none";

    showLoader("Daten werden gesendet...");

    try {
        const response = await fetch("https://192.168.31.180:8432/import", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(exportData)
        });

        if (response.ok) {
            document.getElementById("loading-state").style.display= "none";
            document.getElementById("popup-overlay").style.display = "none";
            document.getElementById("display-result-container").style.display = "none";
            document.getElementById("options").style.display = "none";
            document.getElementById("transfer-successful").style.display = "flex";
        }
        else {
            showError("Fehler beim Senden der Daten,")
        }


    } catch(error) {
        console.error("Failed to send data:", error);
        showError("Fehler beim Senden der Daten,")
    }



}

export async function getBody(item: any) {
    return await new Promise<string>((resolve, reject) => {
        item.body.getAsync(Office.CoercionType.Text, (result) => {
            if (result.status === Office.AsyncResultStatus.Succeeded) {

                resolve(result.value)
            } else {
                reject(result.error)
            }
        });
    });
}

export async function getAttachments(item: any) {
    const attachmentPromises = item.attachments.map(att => {
        return new Promise((resolve) => {
            item.getAttachmentContentAsync(att.id, (result) => {
                resolve( {
                    name: att.name,
                    id: att.id,
                    contentType: att.contentType,
                    contentBytes: result.value.content
                });
            });
        });
    });
    return await Promise.all(attachmentPromises)
}

export async function sendOffer(importData) {
    console.log("Button clicked");

    const updatedData = importData.map( row => {
        if (row.Belegtext) {
            return {
                ...row,
                Belegtext: row.Belegtext.replace(/Best\..*vom/, "Angebot vom")
            }
        }
        return {...row };
    })

    const overlay = document.getElementById("popup-overlay") as HTMLDivElement;
    overlay.style.display = "flex";
    return {
        type: "offer",
        df: updatedData
    }
}

export async function sendOrder(importData) {
    console.log("Button clicked");

    const overlay = document.getElementById("popup-overlay") as HTMLDivElement;
    overlay.style.display = "flex";
    return {
        type: "order",
        df: importData.map(row => {return row;})
    }
}

export function cancelSend() {
    document.getElementById("popup-overlay").style.display = "none";
}

export function createTable(df) {
    const headerRow = document.getElementById("header-row");
    const tableBody = document.getElementById("table-body");
    const requiredCols = ["Pos", "Artikelnummer", "Menge"]

    requiredCols.forEach(col => {
        const th = document.createElement("th")
        th.textContent = col;
        headerRow.appendChild(th)
    })
    df.forEach(rowData => {
        const tr = document.createElement("tr")
        requiredCols.forEach(col => {
            const td = document.createElement("td")
            td.textContent = rowData[col]
            tr.appendChild(td)
        })
        tableBody.appendChild(tr)
    })
}

export function fillInfo(df) {
    const customerNumberContainer = document.getElementById("customer-number-container")
    customerNumberContainer.innerHTML = `<span><strong>Kdnr:</strong> ${df[0]['Kundennummer']}</span>`;
    const introductionTextContainer = document.getElementById("introduction-text-container")
    introductionTextContainer.innerHTML = `<span><strong>Text:</strong></span><br><span>${df[0]['Belegtext']}</span>`;
    const referenceContainer = document.getElementById("reference-text-container")
    if (df[0]['Referenz']) {
        referenceContainer.innerHTML = `<span><strong>Referenz: </strong></span> ${df[0]['Referenz']}`;
    }
    const deliveryContainer = document.getElementById("delivery-address-container")
    deliveryContainer.innerHTML = `<span><strong>Lieferadresse:</strong></span>
<address class="address-box">
${df[0]['Name1']}<br>
${df[0]['Strasse']}<br>
${df[0]['PLZ']} ${df[0]['Ort']}
`
}

export function showContent(): void {
    const content = document.getElementById("display-result-container")
    const loader = document.getElementById("loading-state")
    const loadingError = document.getElementById("loading-error")
    loader.style.display = "none";
    content.style.display = "block";
    loadingError.style.display = "none";
}

export function showLoader(msg: string = "loading"): void {
    const content = document.getElementById("display-result-container")
    const loader = document.getElementById("loading-state")
    const loadingError = document.getElementById("loading-error")
    const loadingText = document.getElementById("loading-text")
    const options = document.getElementById("options")

    options.style.display = "none";
    loader.style.display = "flex";
    content.style.display = "none";
    loadingError.style.display = "none";
    loadingText.innerHTML = msg
}

export function showError(msg: string) {
    const loadingError = document.getElementById("loading-error") as HTMLDivElement
    const content = document.getElementById("display-result-container")
    const loader = document.getElementById("loading-state")
    const options = document.getElementById("options")
    document.getElementById("popup-overlay").style.display = "none"

    options.style.display = "none";
    loader.style.display = "none";
    content.style.display = "none";
    loadingError.style.display = "block";
    loadingError.innerHTML = `<p>${msg}</p>`

}