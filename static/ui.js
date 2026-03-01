// KEXER UI Engine

document.addEventListener("DOMContentLoaded", () => {

    animateLogo();
    animateBackground();
    terminalGlow();

});


// Logo glow animation
function animateLogo() {
    const logo = document.querySelector(".logo");
    if (!logo) return;

    let glow = 0;

    setInterval(() => {
        glow = (glow + 1) % 20;
        logo.style.textShadow =
            "0 0 " + (10 + glow) + "px #00ffcc, 0 0 " + (20 + glow) + "px #00ffcc";
    }, 120);
}


// Animated cyber background
function animateBackground() {

    const body = document.body;
    let pos = 0;

    setInterval(() => {
        pos += 0.2;
        body.style.backgroundPosition = pos + "px " + pos + "px";
    }, 40);

}


// Terminal animation
function terminalGlow() {
    const terminal = document.querySelector(".terminal");
    if (!terminal) return;

    let level = 0;

    setInterval(() => {
        level = (level + 1) % 30;
        terminal.style.boxShadow =
            "0 0 " + (10 + level) + "px rgba(0,255,200,0.15)";
    }, 100);
}


// Typing animation (optional use)
function typeEffect(element, text, speed = 40) {
    let i = 0;

    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }

    element.innerHTML = "";
    type();
}


// Smooth scroll utility
function smoothScroll(targetId) {
    const el = document.getElementById(targetId);
    if (!el) return;

    window.scrollTo({
        top: el.offsetTop,
        behavior: "smooth"
    });
}
