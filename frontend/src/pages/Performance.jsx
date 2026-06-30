import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Performance() {
  const [rows, setRows] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.getPerformance().then(setRows).catch((e) => setErr(e.message));
  }, []);

  return (
    <div>
      <div className="page-head">
        <h1>Performance</h1>
        <p>How you're scoring across subjects.</p>
      </div>

      {err && <div className="alert">{err}</div>}
      {!rows && !err && <div className="spin">Loading…</div>}

      {rows && rows.length === 0 && (
        <div className="empty">No interviews yet. Take one in Mock Interview to see your stats.</div>
      )}

      {rows && rows.length > 0 && (
        <div className="card">
          {rows.map((r) => (
            <div className="bar-row" key={r.subject}>
              <span style={{ fontWeight: 600 }}>{r.subject}</span>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${(r.average_score / 10) * 100}%` }} />
              </div>
              <span className="muted" style={{ textAlign: "right" }}>{r.average_score}</span>
            </div>
          ))}
          <p className="muted" style={{ fontSize: 13, marginTop: 16, marginBottom: 0 }}>
            Based on {rows.reduce((a, r) => a + r.interviews, 0)} interview(s),{" "}
            {rows.reduce((a, r) => a + r.questions_attempted, 0)} question(s) attempted.
          </p>
        </div>
      )}
    </div>
  );
}
