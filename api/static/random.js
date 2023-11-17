// Progress bar from https://codepen.io/theprogrammingexpert/pen/jOqGBLL

const noRefresh = false
const refreshPeriod = 15;
let elapsedTime = 0;

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