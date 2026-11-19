import { createFileRoute } from "@tanstack/react-router";
import { useRef, useState } from "react";
import { Bug, Code2, Lightbulb, Loader2, Mic, Square, Upload, Sparkles } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { Markdown } from "@/components/Markdown";
import { callLLM, transcribe, uploadFile, type Task } from "@/lib/api";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "CodeMate AI — Generate, Debug & Explain Code" },
      { name: "description", content: "AI coding assistant for Python, Java, C, C++ and SQL with voice input, file upload and documentation-grounded answers." },
      { property: "og:title", content: "CodeMate AI — Generate, Debug & Explain Code" },
      { property: "og:description", content: "AI coding assistant grounded in real programming documentation." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Workspace,
});

const TASKS: { id: Task; label: string; icon: typeof Code2; hint: string }[] = [
  { id: "generate", label: "Generate", icon: Code2, hint: "Describe what you want to build" },
  { id: "debug", label: "Debug", icon: Bug, hint: "Paste failing code and the error" },
  { id: "explain", label: "Explain", icon: Lightbulb, hint: "Understand any piece of code" },
];
const LANGS = [["python", "Python"], ["java", "Java"], ["c", "C"], ["c++", "C++"], ["sql", "SQL"]];
const EXT: Record<string, string> = { ".py": "python", ".java": "java", ".c": "c", ".h": "c", ".cpp": "c++", ".sql": "sql" };

function Workspace() {
  const [task, setTask] = useState<Task>("generate");
  const [language, setLanguage] = useState("python");
  const [prompt, setPrompt] = useState("");
  const [code, setCode] = useState("");
  const [fileId, setFileId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [level, setLevel] = useState("beginner");
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<{ text: string; model: string } | null>(null);
  const [error, setError] = useState("");
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState("");
  const recRef = useRef<MediaRecorder | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const submit = async () => {
    if (task === "generate" && !prompt.trim()) {
      setError("Describe what you want to build first.");
      return;
    }
    if (task !== "generate" && !code.trim() && !fileId) {
      setError("Paste source code or upload a file to continue.");
      return;
    }
    setLoading(true); setError(""); setAnswer(null);
    try {
      const r = await callLLM({ task, language, user_input: prompt, code: code || null, error_message: errorMsg || null, detail_level: level, file_id: fileId });
      setAnswer({ text: r.answer, model: r.model });
    } catch (e) { setError((e as Error).message || "Could not reach the backend."); }
    finally { setLoading(false); }
  };

  const toggleMic = async () => {
    if (recording) { recRef.current?.stop(); return; }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream); const chunks: Blob[] = [];
      rec.ondataavailable = (e) => chunks.push(e.data);
      rec.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop()); setRecording(false); setBusy("Transcribing…");
        try { const r = await transcribe(new Blob(chunks, { type: "audio/webm" })); setPrompt((p) => (p ? p + " " : "") + r.transcribed_text); }
        catch (e) { setError((e as Error).message); } finally { setBusy(""); }
      };
      rec.start(); recRef.current = rec; setRecording(true);
    } catch { setError("Microphone access was denied."); }
  };

  const onFile = async (f?: File) => {
    if (!f) return; setBusy("Uploading…"); setError("");
    try {
      const r = await uploadFile(f); setCode(r.content); setFileId(r.file_id);
      const l = EXT[r.file_type]; if (l) setLanguage(l);
      if (task === "generate") setTask("explain");
    } catch (e) { setError((e as Error).message); } finally { setBusy(""); if (fileRef.current) fileRef.current.value = ""; }
  };

  const field = "w-full rounded-lg border border-input bg-code px-4 py-3 font-mono text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20";

  return (
    <AppShell>
      <section className="mb-8">
        <p className="font-mono text-xs uppercase tracking-[0.2em] text-primary">// your ai pair programmer</p>
        <h1 className="mt-2 font-display text-3xl font-bold tracking-tight sm:text-5xl">Write, fix and understand code<span className="text-primary">_</span></h1>
        <p className="mt-3 max-w-2xl text-muted-foreground">Answers grounded in official docs for Python, Java, C, C++ and SQL. Speak your request or drop in a source file.</p>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-5 shadow-panel">
          <div className="grid grid-cols-3 gap-1 rounded-lg bg-muted p-1">
            {TASKS.map((t) => (
              <button key={t.id} onClick={() => setTask(t.id)}
                className={`flex items-center justify-center gap-2 rounded-md py-2 text-sm font-medium transition ${task === t.id ? "bg-background text-primary shadow" : "text-muted-foreground hover:text-foreground"}`}>
                <t.icon className="h-4 w-4" />{t.label}
              </button>
            ))}
          </div>
          <p className="mt-3 font-mono text-xs text-muted-foreground">{TASKS.find((t) => t.id === task)?.hint}</p>

          <div className="mt-4 flex flex-wrap gap-2">
            {LANGS.map(([v, l]) => (
              <button key={v} onClick={() => setLanguage(v ?? "python")}
                className={`rounded-full border px-3 py-1 font-mono text-xs transition ${language === v ? "border-primary bg-primary/10 text-primary" : "border-border text-muted-foreground hover:text-foreground"}`}>{l}</button>
            ))}
          </div>

          <div className="mt-4 space-y-3">
            <div className="relative">
              <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={task === "generate" ? 5 : 2}
                placeholder={task === "generate" ? "e.g. Write a function that validates email addresses…" : "Optional: add context or a question"} className={field + " pr-12 font-sans"} />
              <button onClick={toggleMic} title="Voice input"
                className={`absolute right-3 top-3 grid h-8 w-8 place-items-center rounded-md transition ${recording ? "animate-pulse bg-destructive text-destructive-foreground" : "bg-muted text-muted-foreground hover:text-primary"}`}>
                {recording ? <Square className="h-3.5 w-3.5" /> : <Mic className="h-4 w-4" />}
              </button>
            </div>

            {task !== "generate" && (
              <textarea value={code} onChange={(e) => { setCode(e.target.value); setFileId(null); }} rows={10} placeholder="// paste your source code here" className={field} spellCheck={false} />
            )}
            {task === "debug" && (
              <textarea value={errorMsg} onChange={(e) => setErrorMsg(e.target.value)} rows={3} placeholder="Traceback / error message (optional)" className={field + " text-destructive"} />
            )}
            {task === "explain" && (
              <div className="flex gap-2">
                {["beginner", "intermediate", "advanced"].map((l) => (
                  <button key={l} onClick={() => setLevel(l)} className={`flex-1 rounded-md border py-1.5 text-xs capitalize ${level === l ? "border-accent bg-accent/10 text-accent" : "border-border text-muted-foreground"}`}>{l}</button>
                ))}
              </div>
            )}
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button onClick={submit} disabled={loading}
              className="flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 font-medium text-primary-foreground shadow-glow transition hover:brightness-110 disabled:opacity-60">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              {loading ? "Thinking…" : `Run ${task}`}
            </button>
            <button onClick={() => fileRef.current?.click()} className="flex items-center gap-2 rounded-lg border border-border px-4 py-2.5 text-sm text-muted-foreground hover:text-foreground">
              <Upload className="h-4 w-4" />Upload file
            </button>
            <input ref={fileRef} type="file" hidden accept=".py,.c,.cpp,.h,.java,.js,.ts,.html,.css,.sql,.txt,.md,.json,.xml,.yaml,.yml" onChange={(e) => onFile(e.target.files?.[0])} />
            {busy && <span className="flex items-center gap-2 font-mono text-xs text-muted-foreground"><Loader2 className="h-3 w-3 animate-spin" />{busy}</span>}
          </div>
          {error && <p className="mt-4 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>}
        </div>

        <div className="flex min-h-[28rem] flex-col rounded-xl border border-border bg-card shadow-panel">
          <div className="flex items-center gap-2 border-b border-border px-4 py-3">
            <span className="h-3 w-3 rounded-full bg-destructive/70" /><span className="h-3 w-3 rounded-full bg-warning/70" /><span className="h-3 w-3 rounded-full bg-success/70" />
            <span className="ml-3 font-mono text-xs text-muted-foreground">output.md</span>
            {answer && <span className="ml-auto font-mono text-xs text-muted-foreground">{answer.model}</span>}
          </div>
          <div className="flex-1 overflow-y-auto p-5">
            {loading ? (
              <div className="space-y-3">{[80, 60, 90, 40].map((w, i) => <div key={i} className="h-3 animate-pulse rounded bg-muted" style={{ width: `${w}%` }} />)}</div>
            ) : answer ? <Markdown source={answer.text} /> : (
              <div className="grid h-full place-items-center text-center">
                <div><Code2 className="mx-auto h-10 w-10 text-muted-foreground/40" /><p className="mt-3 font-mono text-sm text-muted-foreground">Results will appear here</p></div>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
