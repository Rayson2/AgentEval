import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  BookOpen,
  Check,
  ChevronDown,
  Clock3,
  Copy,
  FlaskConical,
  Layers3,
  LoaderCircle,
  Menu,
  Network,
  Search,
  Server,
  Sparkles,
  X,
} from "lucide-react";

type FrameworkId = "langchain" | "crewai" | "autogen";

type Framework = {
  id: FrameworkId;
  name: string;
  caption: string;
  accent: string;
  icon: typeof Network;
  tools: string[];
};

type ResearchResponse = {
  success: boolean;
  framework: string;
  model: string;
  question: string;
  report: string;
  execution_time: number;
  status: string;
};

type Health = "checking" | "online" | "offline";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ResearchResponse;
};

const frameworks: Framework[] = [
  {
    id: "langchain",
    name: "LangChain",
    caption: "Document-grounded",
    accent: "sage",
    icon: Layers3,
    tools: ["Local documents"],
  },
  {
    id: "crewai",
    name: "CrewAI",
    caption: "Web research crew",
    accent: "coral",
    icon: Network,
    tools: ["Serper web"],
  },
  {
    id: "autogen",
    name: "AutoGen",
    caption: "Adaptive researcher",
    accent: "blue",
    icon: FlaskConical,
    tools: ["Local documents", "Serper web"],
  },
];

const starterQuestions = [
  "What are the main security challenges in federated learning?",
  "Compare symbolic AI with modern neural approaches.",
  "What research gaps exist in privacy-preserving machine learning?",
];

function App() {
  const [framework, setFramework] = useState<FrameworkId>("autogen");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState("");
  const [health, setHealth] = useState<Health>("checking");
  const [copied, setCopied] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const selected = frameworks.find((item) => item.id === framework)!;
  const SelectedIcon = selected.icon;

  useEffect(() => {
    fetch("/api/health")
      .then((result) => {
        if (!result.ok) throw new Error("offline");
        setHealth("online");
      })
      .catch(() => setHealth("offline"));
  }, []);

  async function runResearch() {
    if (question.trim().length < 10 || isRunning) return;

    setIsRunning(true);
    setError("");
    const submittedQuestion = question.trim();
    setMessages((current) => [...current, { id: `${Date.now()}-user`, role: "user", content: submittedQuestion }]);
    setQuestion("");

    try {
      const result = await fetch(`/api/research/${framework}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: submittedQuestion }),
      });

      const payload = (await result.json()) as ResearchResponse | { detail?: string };
      if (!result.ok) throw new Error("detail" in payload ? payload.detail : "Research request failed.");
      const completedResponse = payload as ResearchResponse;
      setMessages((current) => [...current, { id: `${Date.now()}-assistant`, role: "assistant", content: completedResponse.report, response: completedResponse }]);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to reach the research API.");
    } finally {
      setIsRunning(false);
    }
  }

  async function copyReport(report: string) {
    await navigator.clipboard.writeText(report);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
        <div className="brand-row">
          <div className="brand-mark"><Sparkles size={17} strokeWidth={2.5} /></div>
          <div>
            <div className="brand-name">AGENT<span>/</span>LAB</div>
            <div className="brand-subtitle">Research console</div>
          </div>
          <button className="icon-button mobile-close" onClick={() => setSidebarOpen(false)} aria-label="Close navigation"><X size={18} /></button>
        </div>

        <div className="sidebar-section">
          <div className="eyebrow">Workspace</div>
          <button className="nav-item nav-item-active"><Search size={16} /> Research desk <span className="nav-pulse" /></button>
          <div className="nav-item nav-item-muted"><BookOpen size={16} /> Evidence library</div>
        </div>

        <div className="sidebar-section framework-section">
          <div className="section-heading"><div className="eyebrow">Frameworks</div><span className="count-badge">03</span></div>
          <div className="framework-list">
            {frameworks.map((item) => {
              const Icon = item.icon;
              return <button key={item.id} className={`framework-option ${framework === item.id ? "framework-selected" : ""}`} onClick={() => { setFramework(item.id); setSidebarOpen(false); }}>
                <span className={`framework-icon ${item.accent}`}><Icon size={17} /></span>
                <span className="framework-copy"><strong>{item.name}</strong><small>{item.caption}</small></span>
                {framework === item.id && <Check className="selected-check" size={15} />}
              </button>;
            })}
          </div>
        </div>

        <div className="sidebar-footer">
          <div className={`health-row ${health}`}><span className="health-dot" /><span>Ollama {health === "checking" ? "checking" : health === "online" ? "connected" : "unavailable"}</span></div>
          <div className="model-row"><Server size={14} /> qwen3:1.7b</div>
        </div>
      </aside>

      {sidebarOpen && <button className="sidebar-scrim" onClick={() => setSidebarOpen(false)} aria-label="Close navigation" />}

      <main className="main-content">
        <header className="topbar">
          <button className="icon-button mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu size={20} /></button>
          <div className="crumb"><span>Workspace</span><ChevronDown size={14} /><strong>Research desk</strong></div>
          <div className="topbar-right"><span className="live-label"><span className="live-dot" /> Local session</span><button className="avatar" aria-label="Profile">R</button></div>
        </header>

        <div className="content-wrap">
          <section className="chat-header"><div><p className="kicker">Open-ended inquiry / {String(messages.filter((message) => message.role === "user").length + 1).padStart(2, "0")}</p><h1>Research <em>together.</em></h1></div><div className="session-caption"><span className="live-dot" /> Threaded session</div></section>

          <section className={`chat-thread ${messages.length || isRunning || error ? "chat-active" : ""}`}>
            {!messages.length && !isRunning && !error && <div className="chat-welcome"><div className="empty-icon"><Sparkles size={21} /></div><h2>What are you curious about?</h2><p>Ask a question and your selected agent will investigate it with the tools available in this workspace.</p></div>}
            {messages.map((message) => message.role === "user" ? <div className="message-row user-row" key={message.id}><div className="message-bubble user-bubble">{message.content}</div><div className="message-avatar user-avatar">R</div></div> : <div className="message-row assistant-row" key={message.id}><div className={`message-avatar assistant-avatar ${selected.accent}`}><Sparkles size={15} /></div><div className="assistant-column"><div className="message-label"><strong>{message.response?.framework || selected.name}</strong><span>researcher</span></div><div className="message-bubble assistant-bubble"><div className="report-body">{message.content.split("\n").map((paragraph, index) => paragraph.trim() ? <p key={`${paragraph}-${index}`}>{paragraph}</p> : <div className="report-gap" key={`gap-${index}`} />)}</div></div>{message.response && <div className="message-meta"><span><Clock3 size={13} /> {message.response.execution_time.toFixed(2)}s</span><span><SelectedIcon size={13} /> {message.response.model}</span><button onClick={() => copyReport(message.content)}>{copied ? <Check size={13} /> : <Copy size={13} />} {copied ? "Copied" : "Copy"}</button></div>}</div></div>)}
            {isRunning && <div className="message-row assistant-row"><div className={`message-avatar assistant-avatar ${selected.accent}`}><Sparkles size={15} /></div><div className="assistant-column"><div className="message-label"><strong>{selected.name}</strong><span>researcher</span></div><div className="typing-bubble"><span /><span /><span /></div></div></div>}
            {error && <div className="error-state"><div className="error-icon">!</div><div><strong>Research could not be completed</strong><p>{error}. Check that the backend and Ollama are running.</p></div></div>}
          </section>

          {!messages.length && <div className="suggestions"><span>Try a direction</span>{starterQuestions.map((item) => <button key={item} onClick={() => setQuestion(item)}>{item}</button>)}</div>}

          <section className="composer-panel chat-composer">
            <div className="composer-meta"><span className="panel-label">Message research agent</span><span className="char-count">{question.length} / 2,000</span></div>
            <textarea value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); void runResearch(); } }} placeholder="Ask a follow-up or start a new investigation..." maxLength={2000} />
            <div className="composer-footer"><div className="selected-framework"><span className={`framework-icon small ${selected.accent}`}><SelectedIcon size={15} /></span><span><strong>{selected.name}</strong> · {selected.tools.join(" + ")}</span><ChevronDown size={14} /></div><button className="run-button" onClick={runResearch} disabled={isRunning || question.trim().length < 10}>{isRunning ? <><LoaderCircle className="spin" size={17} /> Thinking</> : <>Send <ArrowUpRight size={17} /></>}</button></div>
          </section>
        </div>
        <footer className="page-footer"><span>AGENT / LAB</span><span>Local inference · Evidence-aware research</span></footer>
      </main>
    </div>
  );
}

export default App;
