const editor = CodeMirror(document.querySelector("#code"), {
  lineNumbers: true,
  tabSize: 4,
  mode: "xml",
});

document.querySelector("#run-btn").addEventListener("click", async function () {
  let code = editor.getValue();
  const response = await fetch("/run", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      source: code,
    }),
  });
});
