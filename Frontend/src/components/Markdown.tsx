import { useState } from "react";
import { Check, Copy } from "lucide-react";

function CodeBlock({ lang, code }: { lang: string; code: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <div className="my-4 overflow-hidden rounded-lg border border-border bg-code">
      <div className="flex items-center justify-between border-b border-border px-3 py-1.5 font-mono text-xs text-muted-foreground">
        <span>{lang || "code"}</span>
        <button onClick={() => { navigator.clipboard.writeText(code); setCopied(true); setTimeout(() => setCopied(false), 1500); }}
          className="flex items-center gap-1 hover:text-primary">
          {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}{copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="overflow-x-auto p-4 font-mono text-sm leading-relaxed text-foreground"><code>{code}</code></pre>
    </div>
  );
}

function inline(text: string) {
  return text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((p, i) =>
    p.startsWith("`") && p.endsWith("`") ? <code key={i} className="rounded bg-muted px-1.5 py-0.5 font-mono text-[0.85em] text-primary">{p.slice(1, -1)}</code>
    : p.startsWith("**") && p.endsWith("**") ? <strong key={i} className="font-semibold text-foreground">{p.slice(2, -2)}</strong>
    : p);
}

export function Markdown({ source }: { source: string }) {
  const parts = source.split(/```(\w*\+*)?\n?([\s\S]*?)```/g);
  const out: React.ReactNode[] = [];
  for (let i = 0; i < parts.length; i += 3) {
    const text = parts[i];
    if (text) text.split("\n").forEach((line, j) => {
      const k = `${i}-${j}`;
      const h = line.match(/^(#{1,4})\s+(.*)/);
      if (h) out.push(<h3 key={k} className="mt-5 mb-2 font-display text-lg font-semibold text-foreground">{inline(h[2] ?? "")}</h3>);
      else if (/^\s*([-*]|\d+\.)\s+/.test(line)) out.push(<p key={k} className="ml-4 flex gap-2 text-muted-foreground"><span className="text-primary">›</span><span>{inline(line.replace(/^\s*([-*]|\d+\.)\s+/, ""))}</span></p>);
      else if (line.trim()) out.push(<p key={k} className="my-1.5 leading-relaxed text-muted-foreground">{inline(line)}</p>);
    });
    if (i + 2 < parts.length) out.push(<CodeBlock key={`c${i}`} lang={parts[i + 1] || ""} code={(parts[i + 2] ?? "").replace(/\n$/, "")} />);
  }
  return <div className="text-[0.95rem]">{out}</div>;
}
