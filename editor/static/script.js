const editor = CodeMirror(document.querySelector("#code"), {
  lineNumbers: true,
  tabSize: 4,
  mode: "javascript",
  theme: "juejin",
  lineWrapping: true,
  autofocus: true
});
const input = CodeMirror(document.querySelector("#input"), {
  lineNumbers: true,
  tabSize: 4,
  mode: "javascript",
  theme: "juejin",
  lineWrapping: true
});

const output = CodeMirror(document.querySelector("#output"), {
  lineNumbers: true,
  tabSize: 4,
  mode: "javascript",
  theme: "juejin",
  lineWrapping: true,
  lineNumbers: false,
  readOnly: true,
  cursorHeight: 0
});

editor.setSize("100%", "100%");
input.setSize("100%", "100%");
output.setSize("100%", "100%");

function toggleDisable(disable) {
  if (disable === true) {
    output.setValue("Executando...")
  }
  editor.setOption("readOnly", disable);
  input.setOption("readOnly", disable);
  document.querySelector("#run-btn").disabled = disable
  document.querySelector("#clear-btn").disabled = disable
}

document.querySelector("#run-btn").addEventListener("click", async function () {
  let code = editor.getValue();
  let keyboard_input = input.getValue();

  toggleDisable(true);
  const response = await fetch("/run", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      source: code,
      keyboard_input: keyboard_input
    }),
  });

  const res = await response.json();
  output.setValue(res.output);
  const doc = output.getDoc();
  const lastLine = doc.lineCount() - 1;
  const lastChar = doc.getLine(lastLine).length;
  doc.setCursor({ line: lastLine, ch: lastChar });
  output.scrollTo(null, output.getScrollInfo().height);
  toggleDisable(false);
});

document.querySelector("#clear-btn").addEventListener("click", function () {
  editor.setValue("");
  input.setValue("");
  output.setValue("");
})