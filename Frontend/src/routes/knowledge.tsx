import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { BookOpen, Loader2, Search } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { retrieve, type Chunk } from "@/lib/api";

export const Route = createFileRoute("/knowledge")({
  head: () => ({
    meta: [
      { title: "Knowledge Base Search — CodeMate AI" },
      { name: "description", content: "Search the programming documentation CodeMate AI uses to ground its answers." },
      { property: "og:title", content: "Knowledge Base Search — CodeMate AI" },
      { property: "og:description", content: "Semantic search across Python, Java, C, C++ and SQL docs." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Knowledge,
});

const LANGS: [string | null, string][] = [[null, "All"], ["python", "Python"], ["java", "Java"], ["c", "C"], ["c++", "C++"], ["sql", "SQL"]];

function Knowledge() {
  const [q, setQ] = useState("");
  const [lang, setLang] = useState<string | null>(null);
  const [k, setK] = useState(5);
  const [res, setRes] = useState<Chunk[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const go = async (e: React.FormEvent) => {
    e.preventDefault(); if (!q.trim()) return;
    setLoading(true); setErr("");
    try { setRes((await retrieve(q, lang, k)).results); } catch (e) { setErr((e as Error).message || "Search failed"); } finally { setLoading(false); }
  };
  return (
    <AppShell>
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-accent">// retrieval-augmented</p>
      <h1 className="mt-2 font-display text-3xl font-bold tracking-tight sm:text-4xl">Search the documentation</h1>
      <p className="mt-2 text-muted-foreground">See exactly which documentation passages CodeMate uses to answer.</p>
      <form onSubmit={go} className="mt-6 rounded-xl border border-border bg-card p-4 shadow-panel">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="How do Python decorators work?" className="w-full rounded-lg border border-input bg-code py-3 pl-10 pr-3 text-sm outline-none focus:border-accent" />
          </div>
          <button disabled={loading} className="flex items-center gap-2 rounded-lg bg-accent px-5 font-medium text-accent-foreground disabled:opacity-60">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Search"}
          </button>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {LANGS.map(([v, l]) => (
            <button type="button" key={l} onClick={() => setLang(v)} className={`rounded-full border px-3 py-1 font-mono text-xs ${lang === v ? "border-accent bg-accent/10 text-accent" : "border-border text-muted-foreground"}`}>{l}</button>
          ))}
          <label className="ml-auto flex items-center gap-2 font-mono text-xs text-muted-foreground">top_k
            <input type="number" min={1} max={20} value={k} onChange={(e) => setK(Math.min(20, Math.max(1, +e.target.value)))} className="w-14 rounded border border-input bg-code px-2 py-1" />
          </label>
        </div>
      </form>
      {err && <p className="mt-4 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">{err}</p>}
      <div className="mt-6 grid gap-4">
        {res?.length === 0 && <p className="text-muted-foreground">No matching passages found.</p>}
        {res?.map((c, i) => (
          <article key={i} className="rounded-xl border border-border bg-card p-5">
            <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
              <BookOpen className="h-4 w-4 text-accent" />
              <span className="text-foreground">{String(c.metadata["source"] ?? c.metadata["filename"] ?? "doc")}</span>
              <span className="rounded bg-muted px-2 py-0.5 text-muted-foreground">{String(c.metadata["language"])}</span>
              <span className="ml-auto text-primary">{((1 - c.distance) * 100).toFixed(1)}% match</span>
            </div>
            <pre className="mt-3 max-h-64 overflow-auto whitespace-pre-wrap rounded-lg bg-code p-4 font-mono text-xs leading-relaxed text-muted-foreground">{c.text}</pre>
          </article>
        ))}
      </div>
    </AppShell>
  );
}
