import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Terminal, Settings2, Sun, Moon } from "lucide-react";
import { getApiBase, ping, setApiBase } from "@/lib/api";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [api, setApi] = useState("");
  const [status, setStatus] = useState<"idle" | "ok" | "down">("idle");
  const [open, setOpen] = useState(false);
  const check = () => ping().then(() => setStatus("ok")).catch(() => setStatus("down"));
  const [light, setLight] = useState(false);
  useEffect(() => { setApi(getApiBase()); check(); setLight(localStorage.getItem("codemate_theme") === "light"); }, []);
  useEffect(() => {
    const el = document.documentElement;
    el.classList.toggle("light", light); el.classList.toggle("dark", !light);
  }, [light]);
  const toggleTheme = () => { const n = !light; setLight(n); localStorage.setItem("codemate_theme", n ? "light" : "dark"); };
  const nav = "rounded-md px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground";
  return (
    <div className="min-h-screen bg-background bg-grid">
      <header className="sticky top-0 z-20 border-b border-border bg-background/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center gap-4 px-4 py-3">
          <Link to="/" className="flex items-center gap-2">
            <span className="grid h-8 w-8 place-items-center rounded-md bg-primary text-primary-foreground"><Terminal className="h-4 w-4" /></span>
            <span className="font-display text-lg font-bold tracking-tight">CodeMate<span className="text-primary">.ai</span></span>
          </Link>
          <nav className="ml-2 flex gap-1">
            <Link to="/" className={nav} activeProps={{ className: "bg-muted text-foreground" }} activeOptions={{ exact: true }}>Workspace</Link>
            <Link to="/knowledge" className={nav} activeProps={{ className: "bg-muted text-foreground" }}>Knowledge base</Link>
          </nav>
          <button onClick={toggleTheme} aria-label={light ? "Switch to dark mode" : "Switch to light mode"} title={light ? "Dark mode" : "Light mode"}
            className="ml-auto grid h-8 w-8 place-items-center rounded-md border border-border text-muted-foreground transition-colors hover:text-primary">
            {light ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
          </button>
          <div className="relative">
            <button onClick={() => setOpen(!open)} className="flex items-center gap-2 rounded-md border border-border px-3 py-1.5 font-mono text-xs text-muted-foreground hover:text-foreground">
              <span className={`h-2 w-2 rounded-full ${status === "ok" ? "bg-success" : status === "down" ? "bg-destructive" : "bg-muted-foreground"}`} />
              <span className="hidden sm:inline">{status === "ok" ? "backend online" : status === "down" ? "backend offline" : "checking…"}</span>
              <Settings2 className="h-3.5 w-3.5" />
            </button>
            {open && (
              <div className="absolute right-0 mt-2 w-80 rounded-lg border border-border bg-popover p-4 shadow-xl">
                <label className="font-mono text-xs text-muted-foreground">Backend URL</label>
                <input value={api} onChange={(e) => setApi(e.target.value)} className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none focus:border-primary" />
                <button onClick={() => { setApiBase(api); check(); setOpen(false); }} className="mt-3 w-full rounded-md bg-primary py-2 text-sm font-medium text-primary-foreground">Save & reconnect</button>
                <p className="mt-2 text-xs text-muted-foreground">Your FastAPI server must allow CORS from this site.</p>
              </div>
            )}
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8">{children}</main>
    </div>
  );
}
