// script.js
function appendValue(value) {
    const display = document.getElementById('display');
    display.value += value;
}

function clearDisplay() {
    const display = document.getElementById('display');
    display.value = '';
}

function backspace() {
    const display = document.getElementById('display');
    display.value = display.value.slice(0, -1);
}

function calculate() {
    const display = document.getElementById('display');
    try {
        // Convert power operator (^) to JavaScript's Math.pow function
        let expression = display.value;
        expression = expression.replace(/\^/g, '**');
        
        // Convert trigonometric functions from degrees to radians
        expression = expression.replace(/sin\(([^()]*)\)/g, (_, angle) => `Math.sin(toRadians(${angle}))`);
        expression = expression.replace(/cos\(([^()]*)\)/g, (_, angle) => `Math.cos(toRadians(${angle}))`);
        expression = expression.replace(/tan\(([^()]*)\)/g, (_, angle) => `Math.tan(toRadians(${angle}))`);
        
        // Evaluate the expression
        display.value = eval(expression);
    } catch (error) {
        display.value = 'Error';
    }
}

function appendTrigFunction(func) {
    const display = document.getElementById('display');
    display.value += `${func}(`;
}

function toRadians(degrees) {
    return degrees * (Math.PI / 180);
}