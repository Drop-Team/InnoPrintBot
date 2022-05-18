import {selectElementById, setValueByElementID} from './interface.js';

Telegram.WebApp.ready();
Telegram.WebApp.MainButton.setText("SAVE").show().onClick(function () {
    sendData();
    Telegram.WebApp.close();
});

let JobID = null;

function getData() {
    const data = {};

    const chooseElements = document.getElementsByClassName("active");

    for (let chooseElement of chooseElements) {

        if (chooseElement.id.startsWith("layout-")) {
            data["layout"] = chooseElement.id;
        } else if (chooseElement.id.startsWith("print-on-")) {
            data["print-on"] = chooseElement.id;
        } else if (chooseElement.id.startsWith("position-")) {
            data["position"] = chooseElement.id;
        }
    }

    const inputElements = document.getElementsByTagName("input");

    for (let inputElement of inputElements) {

        if (inputElement.id.startsWith("copies-")) {
            data["copies"] = inputElement.value;
        } else if (inputElement.id.startsWith("pages-")) {
            data["pages"] = inputElement.value;
        }
    }

    return data;
}

function autoFillFromURL() {
    const params = new URLSearchParams(window.location.search);

    const layoutChooseID = params.get("layout");
    const printOnChooseID = params.get("print-on");
    const positionChooseID = params.get("position");
    const copiesText = params.get("copies");
    const pagesText = params.get("pages");
    JobID = params.get("job-id");

    selectElementById(layoutChooseID);
    selectElementById(printOnChooseID);
    selectElementById(positionChooseID);

    setValueByElementID("copies-input", copiesText);
    setValueByElementID("pages-input", pagesText);
}

function sendData() {
    let data = getData();
    data["type"] = "print"
    data["job-id"] = JobID;

    let xhr = new XMLHttpRequest();
    xhr.open("POST", window.location.origin + "/add_event", false);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.send(JSON.stringify(data));
}

autoFillFromURL();