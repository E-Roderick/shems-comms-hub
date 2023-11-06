
function currentTime() {
    return Math.floor(Date.now() / 1000);
}

function datetimeStringToTimestamp(s) {
    return Math.floor(Date.parse(s) / 1000);
}

function timeStampToDate(t) {
    return new Date(t * 1000);
}

export {
    currentTime,
    datetimeStringToTimestamp,
    timeStampToDate,
}