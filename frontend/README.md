# InterviewIQ — Frontend (React + Vite)

## Run it

1. Install Node.js 18+ (https://nodejs.org) if you don't have it.
2. In this folder, run:

       npm install
       npm run dev

3. Open the URL it prints (usually http://localhost:5173).

## Important
- Your FastAPI backend must be running at http://127.0.0.1:8000
  (start it with `uvicorn app:app --reload` in the backend folder).
- The backend already has CORS enabled, so the browser can talk to it.
- If your backend uses a different port, change BASE in `src/api.js`.

## Pages
- Dashboard    — live counts + strong/weak areas
- Documents    — upload a PDF, see indexed docs
- AI Chat      — ask questions, get answers with page citations
- Mock Interview — start a session, answer, get scored
- Performance  — per-subject score bars
