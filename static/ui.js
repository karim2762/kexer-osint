let foundCount = 0;
let totalChecks = 0;

function startScan(username) {

const terminal = document.getElementById("terminal");
const bar = document.getElementById("bar");
const counter = document.getElementById("foundCount");
const reportBtn = document.getElementById("reportBtn");

reportBtn.style.display = "none";

const source = new EventSource("/scan_stream?username=" + username);

source.onmessage = function(event) {

let data = JSON.parse(event.data);

if (!data) return;

if (data.type === "log") {
terminal.innerHTML += data.message + "<br>";
terminal.scrollTop = terminal.scrollHeight;
}

if (data.type === "result") {

totalChecks++;

if (data.status === "FOUND") {
foundCount++;
counter.innerText = foundCount;
}

let percent = (totalChecks / data.total) * 100;
bar.style.width = percent + "%";

}

if (data.type === "done") {

bar.style.width = "100%";
source.close();

reportBtn.style.display = "block";
reportBtn.href = "/report/" + username;

terminal.innerHTML += "<br><b>Scan Completed.</b>";

}

};

}
