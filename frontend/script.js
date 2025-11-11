// const askBtn = document.getElementById("ask-btn");
// const questionInput = document.getElementById("question");
// const answerDiv = document.getElementById("answer");
// const sourcesDiv = document.getElementById("sources");
// const latencyDiv = document.getElementById("latency");

// const API_BASE = "http://127.0.0.1:8000";

// askBtn.onclick = async () => {
//   const q = questionInput.value.trim();
//   if (!q) return alert("Enter a question!");

//   answerDiv.textContent = "";
//   sourcesDiv.textContent = "";
//   latencyDiv.textContent = "⏳ Thinking...";

//   const res = await fetch(`${API_BASE}/query/stream`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify({ question: q, top_k: 5 }),
//   });

//   const reader = res.body.getReader();
//   const decoder = new TextDecoder("utf-8");
//   let full = "";
//   while (true) {
//     const { done, value } = await reader.read();
//     if (done) break;
//     const chunk = decoder.decode(value);
//     full += chunk;
//     answerDiv.textContent += chunk;
//   }

//   // parse footer
//   const latencyMatch = full.match(/\[END_STREAM latency_ms=(.*?)\]/);
//   latencyDiv.textContent =
//     latencyMatch ? `⚡ ${latencyMatch[1]} ms` : "✅ Done";

//   // parse sources header
//   const sourcesLine = full.split("\n")[0];
//   if (sourcesLine.startsWith("[sources]")) {
//     sourcesDiv.textContent = sourcesLine.replace("[sources]", "📂 Sources:");
//   }
// };

const askBtn = document.getElementById("ask-btn");
const questionInput = document.getElementById("question");
const answerDiv = document.getElementById("answer");
const sourcesDiv = document.getElementById("sources");
const latencyDiv = document.getElementById("latency");

const API_BASE = "http://127.0.0.1:8000";

askBtn.onclick = async () => {
  const q = questionInput.value.trim();
  if (!q) return alert("Enter a question!");

  answerDiv.textContent = "";
  sourcesDiv.textContent = "";
  latencyDiv.textContent = "⏳ Thinking...";

  try {
    const response = await fetch(`${API_BASE}/query/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q, top_k: 5 }),
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let partial = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      partial += chunk;
      answerDiv.textContent += chunk;

      // force DOM repaint (Chrome streaming fix)
      await new Promise(r => setTimeout(r, 0));
    }

    // parse latency footer
    const latencyMatch = partial.match(/\[END_STREAM latency_ms=(.*?)\]/);
    latencyDiv.textContent = latencyMatch
      ? `⚡ ${latencyMatch[1]} ms`
      : "Done";

    // parse sources header
    const firstLine = partial.split("\n")[0];
    if (firstLine.startsWith("[sources]")) {
      sourcesDiv.textContent = firstLine.replace("[sources]", "Sources:");
    }
  } catch (err) {
    latencyDiv.textContent = `Error: ${err.message}`;
    console.error(err);
  }
};

