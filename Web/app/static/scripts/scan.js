import {selectElementById, setValueByElementID} from './interface.js';

Telegram.WebApp.ready();
Telegram.WebApp.MainButton.setText("SAVE").show().onClick(function () {
    sendData();
    Telegram.WebApp.close();
});

let jobID = null;

function getData() {
    const data = {};

    const chooseElements = document.getElementsByClassName("active");

    for (let chooseElement of chooseElements) {

        if (chooseElement.id.startsWith("scan-from-")) {
            data["scan-from"] = chooseElement.id;
        } else if (chooseElement.id.startsWith("quality-")) {
            data["quality"] = chooseElement.id;
        }
    }

    return data;
}

function autoFillFromURL() {
    const params = new URLSearchParams(window.location.search);

    const scanOnChooseID = params.get("scan-from");
    const qualityChooseID = params.get("quality");
    jobID = params.get("job-id");

    selectElementById(scanOnChooseID);
    selectElementById(qualityChooseID);
}

function sendData() {
    let data = getData();
    data["type"] = "scan"
    data["job-id"] = jobID;

    let xhr = new XMLHttpRequest();
    xhr.open("POST", window.location.origin + "/add_event", false);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.send(JSON.stringify(data));
}

autoFillFromURL();
// console.log(getData());
// sendData();