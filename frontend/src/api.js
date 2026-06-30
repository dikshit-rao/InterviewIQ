// All calls to the FastAPI backend live here.
// If your backend runs on a different port, change BASE.
const BASE = "http://127.0.0.1:8000";

async function json(res) {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  getDashboard: () => fetch(`${BASE}/dashboard`).then(json),

  getDocuments: () => fetch(`${BASE}/documents`).then(json),

  uploadPdf: (file) => {
    const form = new FormData();
    form.append("file", file);
    return fetch(`${BASE}/upload-pdf`, { method: "POST", body: form }).then(json);
  },

  ask: (question, documents) =>
    fetch(`${BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, documents }),
    }).then(json),

  startInterview: (subject, difficulty) =>
    fetch(`${BASE}/interview/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject, difficulty }),
    }).then(json),

  submitAnswer: (interview_id, question, user_answer) =>
    fetch(`${BASE}/interview/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ interview_id, question, user_answer }),
    }).then(json),

  getPerformance: () => fetch(`${BASE}/performance`).then(json),
};
