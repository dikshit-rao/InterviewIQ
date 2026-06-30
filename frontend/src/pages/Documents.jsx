import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Documents() {
  const [docs, setDocs] = useState([]);
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const load = () => api.getDocuments().then(setDocs).catch(() => {});
  useEffect(() => { load(); }, []);

  const upload = async () => {
    if (!file) return;
    setBusy(true);
    setMsg("");
    try {
      const res = await api.uploadPdf(file);
      setMsg(
        res.already_exists
          ? `"${res.document_name}" is already uploaded.`
          : `Uploaded "${res.document_name}" — ${res.total_chunks} chunks indexed.`
      );
      setFile(null);
      load();
    } catch (e) {
      setMsg("Upload failed: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div className="page-head">
        <h1>Documents</h1>
        <p>Upload your notes as PDFs. They become searchable in AI Chat.</p>
      </div>

      <div className="stack">
        <div className="card">
          <label className="field">Upload a PDF</label>
          <div className="row">
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <button className="btn" onClick={upload} disabled={!file || busy}>
              {busy ? "Uploading…" : "Upload"}
            </button>
          </div>
          {msg && <p className="muted" style={{ marginBottom: 0 }}>{msg}</p>}
        </div>

        <div className="card">
          <h3>Uploaded</h3>
          {docs.length === 0 ? (
            <div className="empty">No documents yet. Upload your first PDF above.</div>
          ) : (
            <div className="stack" style={{ gap: 10, marginTop: 14 }}>
              {docs.map((d) => (
                <div key={d.name} className="between" style={{ borderBottom: "1px solid var(--line)", paddingBottom: 10 }}>
                  <span>✓ {d.name}</span>
                  <span className="muted">{d.total_chunks} chunks</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
