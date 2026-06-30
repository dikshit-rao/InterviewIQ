import { useState } from "react";
import { api } from "../api.js";

const DIFFICULTIES = ["Easy", "Medium", "Hard"];

export default function Interview() {
  const [subject, setSubject] = useState("DBMS");
  const [difficulty, setDifficulty] = useState("Medium");
  const [session, setSession] = useState(null); // {interview_id, question}
  const [answer, setAnswer] = useState("");
  const [evalResult, setEvalResult] = useState(null);
  const [running, setRunning] = useState({ score: 0, count: 0 });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const start = async () => {
    setBusy(true); setErr(""); setEvalResult(null);
    try {
      const res = await api.startInterview(subject, difficulty);
      setSession({ interview_id: res.interview_id, question: res.question });
      setRunning({ score: 0, count: 0 });
      setAnswer("");
    } catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  };

  const submit = async () => {
    if (!answer.trim()) return;
    setBusy(true); setErr("");
    try {
      const res = await api.submitAnswer(session.interview_id, session.question, answer);
      setEvalResult(res.evaluation);
      setRunning({ score: res.running_score, count: res.questions_answered });
      // queue next question (shown after they read feedback)
      setSession((s) => ({ ...s, nextQuestion: res.next_question }));
    } catch (e) { setErr(e.message); }
    finally { setBusy(false); }
  };

  const nextQuestion = () => {
    setSession((s) => ({ interview_id: s.interview_id, question: s.nextQuestion }));
    setAnswer("");
    setEvalResult(null);
  };

  // ---- setup screen ----
  if (!session) {
    return (
      <div>
        <div className="page-head">
          <h1>Mock Interview</h1>
          <p>Pick a subject and difficulty. The AI plays interviewer and scores you.</p>
        </div>
        <div className="card stack">
          <div>
            <label className="field">Subject</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="DBMS, OS, CN, OOPS…"
            />
          </div>
          <div>
            <label className="field">Difficulty</label>
            <div className="seg">
              {DIFFICULTIES.map((d) => (
                <button
                  key={d}
                  className={difficulty === d ? "on" : ""}
                  onClick={() => setDifficulty(d)}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>
          <div>
            <button className="btn" onClick={start} disabled={busy || !subject.trim()}>
              {busy ? "Starting…" : "Start interview"}
            </button>
          </div>
          {err && <div className="alert">{err}</div>}
        </div>
      </div>
    );
  }

  // ---- interview screen ----
  return (
    <div>
      <div className="page-head between">
        <div>
          <h1>{subject} · {difficulty}</h1>
          <p>Answered {running.count} · Running score {running.score}/10</p>
        </div>
        <button className="btn ghost" onClick={() => setSession(null)}>End</button>
      </div>

      <div className="stack">
        <div className="card">
          <div className="muted" style={{ fontSize: 13 }}>Interviewer asks</div>
          <h3 style={{ marginTop: 8, fontSize: 19, lineHeight: 1.4 }}>{session.question}</h3>
        </div>

        {!evalResult && (
          <div className="card">
            <label className="field">Your answer</label>
            <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} />
            <div style={{ marginTop: 12 }}>
              <button className="btn" onClick={submit} disabled={busy}>
                {busy ? "Evaluating…" : "Submit answer"}
              </button>
            </div>
          </div>
        )}

        {err && <div className="alert">{err}</div>}

        {evalResult && (
          <div className="card">
            <div className="between">
              <h3>Evaluation</h3>
              <span
                className="score-badge"
                style={{ color: evalResult.score >= 7 ? "var(--success)" : evalResult.score >= 4 ? "var(--accent)" : "var(--danger)" }}
              >
                {evalResult.score}/10
              </span>
            </div>

            {evalResult.correct_points?.length > 0 && (
              <div style={{ marginTop: 10 }}>
                <div className="muted" style={{ fontSize: 13 }}>What you got right</div>
                {evalResult.correct_points.map((p, i) => (
                  <div className="pt ok" key={i}><span className="mark">✓</span><span>{p}</span></div>
                ))}
              </div>
            )}

            {evalResult.missing_points?.length > 0 && (
              <div style={{ marginTop: 12 }}>
                <div className="muted" style={{ fontSize: 13 }}>What you missed</div>
                {evalResult.missing_points.map((p, i) => (
                  <div className="pt no" key={i}><span className="mark">✗</span><span>{p}</span></div>
                ))}
              </div>
            )}

            {evalResult.model_answer && (
              <div style={{ marginTop: 14 }}>
                <div className="muted" style={{ fontSize: 13, marginBottom: 6 }}>Model answer</div>
                <div className="answer">{evalResult.model_answer}</div>
              </div>
            )}

            <div style={{ marginTop: 16 }}>
              <button className="btn" onClick={nextQuestion}>Next question →</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
