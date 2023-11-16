// Progress bar from https://codepen.io/theprogrammingexpert/pen/jOqGBLL

const noRefresh = false
const refreshPeriod = 15;
let elapsedTime = 0;

const startUp = () => {
    getRecords().then(r => window.location.assign("/"));
}


async function getRecords() {
    let response = await fetch("/harvest");
    let respJson = await response.json();
    if (respJson["records"] === "failure") {
        displayError("Record harvest failed.")
    }
}

function displayError(message) {
    let errorDiv = document.getElementById("errormessage")
    errorDiv.innerText = "<p>Something went wrong: " + message + "</p>"
}


const tickSecond = () => {
    elapsedTime += 1;
    let progressPercentage = Math.round((elapsedTime / refreshPeriod) * 100);
    if (progressPercentage > 100) {
        progressPercentage = 100;
    }
    changeProgress(progressPercentage);
    if (elapsedTime === refreshPeriod) {
        sleep(1000).then(() => { location.reload(); })
    }
}

const changeProgress = (progress) => {
    let progressbar = document.getElementById("progressbar");
    progressbar.style.width = `${progress}%`;
};

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


window.addEventListener("load", () => {
    if (noRefresh === false) {
        setInterval(tickSecond, 1000);
    }
});