import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Chat() {
  const [docs, setDocs] = useState([]);
  const [selected, setSelected] = useState([]);
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.getDocuments().then(setDocs).catch(() => {});
  }, []);

  const toggle = (name) =>
    setSelected((s) =>
      s.includes(name) ? s.filter((x) => x !== name) : [...s, name]
    );

  const ask = async () => {
    if (!question.trim()) return;
    setBusy(true);
    setErr("");
    setResult(null);
    try {
      // empty selection => search all documents
      const res = await api.ask(question, selected);
      setResult(res);
    } catch (e) {
      setErr(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div className="page-head">
        <h1>AI Chat</h1>
        <p>Ask questions grounded in your documents — answers cite the source page.</p>
      </div>

      <div className="stack">
        <div className="card">
          <label className="field">Choose documents (none selected = search all)</label>
          {docs.length === 0 ? (
            <div className="empty">Upload a PDF in Documents first.</div>
          ) : (
            <div className="checklist">
              {docs.map((d) => (
                <div
                  key={d.name}
                  className={"checkitem" + (selected.includes(d.name) ? " on" : "")}
                  onClick={() => toggle(d.name)}
                >
                  {selected.includes(d.name) ? "☑" : "☐"} {d.name}
                </div>
              ))}
            </div>
          )}

          <div style={{ marginTop: 18 }}>
            <label className="field">Question</label>
            <textarea
              value={question}
              placeholder="e.g. What is normalization?"
              onChange={(e) => setQuestion(e.target.value)}
            />
          </div>
          <div style={{ marginTop: 12 }}>
            <button className="btn" onClick={ask} disabled={busy}>
              {busy ? "Thinking…" : "Ask"}
            </button>
          </div>
        </div>

        {err && <div className="alert">{err}</div>}

        {result && (
          <div className="card">
            <h3>Answer</h3>
            <div className="answer" style={{ marginTop: 12 }}>{result.answer}</div>
            {result.citations?.length > 0 && (
              <div style={{ marginTop: 14 }}>
                <div className="muted" style={{ fontSize: 13, marginBottom: 4 }}>Sources</div>
                {result.citations.map((c, i) => (
                  <span key={i} className="cite">
                    {c.source} · page {c.page}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
