import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.getDashboard().then(setData).catch((e) => setErr(e.message));
  }, []);

  return (
    <div>
      <div className="page-head">
        <h1>Dashboard</h1>
        <p>Your interview readiness at a glance.</p>
      </div>

      {err && <div className="alert">Couldn't load dashboard — is the backend running? ({err})</div>}
      {!data && !err && <div className="spin">Loading…</div>}

      {data && (
        <div className="stack">
          <div className="grid grid-3">
            <div className="card stat">
              <div className="label">Documents uploaded</div>
              <div className="value">{data.uploaded_documents}</div>
            </div>
            <div className="card stat">
              <div className="label">Interviews taken</div>
              <div className="value">{data.interviews_taken}</div>
            </div>
            <div className="card stat">
              <div className="label">Average score</div>
              <div className="value">
                {data.average_score}
                <small> / 10</small>
              </div>
            </div>
          </div>

          <div className="grid grid-2">
            <div className="card">
              <h3>Strong areas</h3>
              <div className="chips">
                {data.strong_areas?.length ? (
                  data.strong_areas.map((s) => (
                    <span key={s} className="chip good">✓ {s}</span>
                  ))
                ) : (
                  <span className="muted">Take a few interviews to see your strengths.</span>
                )}
              </div>
            </div>
            <div className="card">
              <h3>Needs work</h3>
              <div className="chips">
                {data.weak_areas?.length ? (
                  data.weak_areas.map((s) => (
                    <span key={s} className="chip bad">! {s}</span>
                  ))
                ) : (
                  <span className="muted">Nothing flagged yet. Keep practicing.</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
