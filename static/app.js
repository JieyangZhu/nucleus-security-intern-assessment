const expressionElement = document.querySelector("#expression");
const resultElement = document.querySelector("#result");
const statusElement = document.querySelector("#status");
const keypad = document.querySelector(".keys");
const keys = [...document.querySelectorAll(".key")];

const state = {
  current: "0",
  left: null,
  operator: null,
  replaceCurrent: false,
  busy: false,
};

function operatorLabel(operator) {
  return { "+": "+", "-": "−", "*": "×", "/": "÷" }[operator];
}

function render() {
  resultElement.value = state.current;
  resultElement.textContent = state.current;
  expressionElement.textContent = state.operator
    ? `${state.left} ${operatorLabel(state.operator)}`
    : "\u00a0";
  for (const key of keys) {
    key.disabled = state.busy;
    key.classList.toggle(
      "is-active",
      Boolean(state.operator && key.dataset.operator === state.operator),
    );
  }
}

function enterDigit(value) {
  if (state.replaceCurrent) {
    state.current = value === "." ? "0." : value;
    state.replaceCurrent = false;
    return;
  }

  if (value === ".") {
    if (!state.current.includes(".")) {
      state.current += ".";
    }
    return;
  }

  state.current = state.current === "0" ? value : state.current + value;
}

function chooseOperator(operator) {
  state.left = state.current;
  state.operator = operator;
  state.replaceCurrent = true;
}

function clearAll() {
  state.current = "0";
  state.left = null;
  state.operator = null;
  state.replaceCurrent = false;
}

function deleteLast() {
  if (state.replaceCurrent) {
    return;
  }
  state.current = state.current.length > 1 ? state.current.slice(0, -1) : "0";
  if (state.current === "-") {
    state.current = "0";
  }
}

async function evaluate() {
  if (!state.operator || state.left === null || state.busy) {
    return;
  }

  const calculation = {
    left: state.left,
    operator: state.operator,
    right: state.current,
  };

  statusElement.textContent = "";
  state.busy = true;
  render();
  expressionElement.textContent = `${calculation.left} ${operatorLabel(calculation.operator)} ${calculation.right}`;

  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(calculation),
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "Calculation failed");
    }

    state.current = payload.result;
    state.left = null;
    state.operator = null;
    state.replaceCurrent = true;
  } catch (error) {
    statusElement.textContent = error instanceof Error ? error.message : "Calculation failed";
  } finally {
    state.busy = false;
    render();
  }
}

function handleAction(target) {
  statusElement.textContent = "";
  if (target.dataset.value !== undefined) {
    enterDigit(target.dataset.value);
  } else if (target.dataset.operator) {
    chooseOperator(target.dataset.operator);
  } else if (target.dataset.action === "clear") {
    clearAll();
  } else if (target.dataset.action === "delete") {
    deleteLast();
  } else if (target.dataset.action === "equals") {
    evaluate();
    return;
  }
  render();
}

keypad.addEventListener("click", (event) => {
  const target = event.target.closest("button");
  if (target) {
    handleAction(target);
  }
});

document.addEventListener("keydown", (event) => {
  const key = event.key;
  statusElement.textContent = "";
  if (/^\d$/.test(key) || key === ".") {
    enterDigit(key);
  } else if (["+", "-", "*", "/"].includes(key)) {
    chooseOperator(key);
  } else if (key === "Enter" || key === "=") {
    event.preventDefault();
    evaluate();
    return;
  } else if (key === "Backspace") {
    deleteLast();
  } else if (key === "Escape") {
    clearAll();
  } else {
    return;
  }
  render();
});

render();
