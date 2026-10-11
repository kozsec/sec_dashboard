
const character = document.getElementById("character-image");
const buttons = document.querySelectorAll("[data-expression]");

const expressions = {
    normal: "images/character/normal.png"
};

const blinkImages = {
    normal: "images/character/blink-normal.png"
};

let currentExpression = "normal";
let blinking = false;

function changeExpression(expression) {
    if (!expressions[expression]) return;

    currentExpression = expression;

    if (!blinking) {
        character.src = expressions[currentExpression];
    }
}

buttons.forEach(button => {
    button.addEventListener("click", () => {
        changeExpression(button.dataset.expression);
    });
});

function blink() {
    if (blinking) return;

    blinking = true;
    character.src = blinkImages[currentExpression];

    setTimeout(() => {
        character.src = expressions[currentExpression];
        blinking = false;
    }, 150);
}

function scheduleBlink() {
    const interval = 2500 + Math.random() * 3000;

    setTimeout(() => {
        blink();
        scheduleBlink();
    }, interval);
}

scheduleBlink();
