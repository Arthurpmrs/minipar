const editor = CodeMirror(document.querySelector("#code"), {
  lineNumbers: true,
  tabSize: 4,
  mode: "javascript",
  theme: "juejin",
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

  const res = await response.json();
  document.getElementById("output").innerHTML = res.output;
});

editor.setSize("100%", "100%");