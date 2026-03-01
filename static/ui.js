function typeLine(text) {
    const terminal = document.getElementById("terminal");
    const line = document.createElement("div");
    line.innerText = text;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

async function startScan(username) {

    const bar = document.getElementById("bar");
    const reportBtn = document.getElementById("reportBtn");

    typeLine("Initializing KEXER Intelligence Engine...");
    typeLine("Target locked: " + username);
    typeLine("Starting OSINT sweep...");

    let progress = 0;

    const interval = setInterval(() => {
        progress += Math.random() * 8;
        bar.style.width = progress + "%";
        if (progress >= 100) clearInterval(interval);
    }, 200);

    const response = await fetch("/api/scan/" + username);
    const data = await response.json();

    typeLine("Analyzing username intelligence...");
    typeLine("Length: " + data.intelligence.length);
    typeLine("Numbers: " + data.intelligence.has_numbers);
    typeLine("Risk Level: " + data.intelligence.risk_level);

    typeLine("Scanning social networks...");

    data.results.forEach(r => {
        if (r.status === "FOUND") {
            typeLine("[FOUND] " + r.site + " -> " + r.url);
        } else {
            typeLine("[MISS] " + r.site);
        }
    });

    bar.style.width = "100%";

    typeLine("KEXER Scan Complete.");
    typeLine("Generating intelligence report...");

    reportBtn.innerText = "Open KEXER Report";
    reportBtn.href = "/report/" + username;
}
