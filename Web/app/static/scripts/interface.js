export { selectElementById, setValueByElementID };

function selectElementById(id) {

    const element = document.getElementById(id);
    console.log(element);
    if (element == null) return;
    changeElementSelect(element);
}

function setValueByElementID(id, newValue) {

    const element = document.getElementById(id);

    if (element == null || newValue == null) return;
    element.value = newValue;
}

function changeElementSelect(element) {

    if (element.className !== "select-button") return;

    let siblings = element.parentElement.children;
    for (let element of siblings) element.classList.remove("active");

    element.classList.add("active");
}

function changeNumberSpinnerValue(element, change) {

    let numberSpinnerValue = parseInt(element.parentElement.children[1].value);

    if (numberSpinnerValue > 1 || (numberSpinnerValue === 1 && change > 0)) {
        element.parentElement.children[1].value = numberSpinnerValue + change;
    }
}

function onNumberSpinnerClick(event) {

    switch(event.target.className) {
        case "number-spinner-plus":
            changeNumberSpinnerValue(event.target, 1);
            break;
        case "number-spinner-minus":
            changeNumberSpinnerValue(event.target, -1);
            break;
    }
}

function onOptionElementsClick(event) {

    let clickedElement = event.target;
    changeElementSelect(clickedElement)
}

let numberSpinners = document.getElementsByClassName("number-spinner");

for (let numberSpinner of numberSpinners) {
    numberSpinner.addEventListener("click", onNumberSpinnerClick);
}

let optionElements = document.getElementsByClassName("switcher");

for (let optionElement of optionElements) {
    optionElement.addEventListener("click", onOptionElementsClick);
}

// let inputTexts = document.getElementsByTagName("input");
//
// for (let inputText of inputTexts) {
//     inputText.addEventListener("input", regexValidation);
// }

