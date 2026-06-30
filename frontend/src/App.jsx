import { useState } from "react";
import Dashboard from "./pages/Dashboard.jsx";
import Documents from "./pages/Documents.jsx";
import Chat from "./pages/Chat.jsx";
import Interview from "./pages/Interview.jsx";
import Performance from "./pages/Performance.jsx";

const NAV = [
  { id: "dashboard", label: "Dashboard", ico: "◇", el: Dashboard },
  { id: "documents", label: "Documents", ico: "▤", el: Documents },
  { id: "chat", label: "AI Chat", ico: "✦", el: Chat },
  { id: "interview", label: "Mock Interview", ico: "▶", el: Interview },
  { id: "performance", label: "Performance", ico: "▥", el: Performance },
];

export default function App() {
  const [active, setActive] = useState("dashboard");
  const Active = NAV.find((n) => n.id === active).el;

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-dot" />
          <span>InterviewIQ</span>
        </div>
        <nav className="nav">
          {NAV.map((n) => (
            <button
              key={n.id}
              className={active === n.id ? "active" : ""}
              onClick={() => setActive(n.id)}
            >
              <span className="ico">{n.ico}</span>
              <span className="txt">{n.label}</span>
            </button>
          ))}
        </nav>
      </aside>
      <main className="main">
        <Active />
      </main>
    </div>
  );
}
