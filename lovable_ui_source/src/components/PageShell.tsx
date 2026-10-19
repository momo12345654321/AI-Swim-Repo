import { Link } from "@tanstack/react-router";
import { Waves } from "lucide-react";
import type { ReactNode } from "react";

export const sections = [
  { to: "/", label: "Analyze" },
  { to: "/annotated-video", label: "Annotated video" },
  { to: "/time-series", label: "Time-series data" },
  { to: "/supervised-ml", label: "Supervised ML" },
  { to: "/deep-learning", label: "Deep learning" },
  { to: "/feedback-learning", label: "Feedback learning" },
  { to: "/about", label: "About" },
] as const;

export function SectionNav() {
  return (
    <nav className="flex gap-1 overflow-x-auto border-b border-border px-4 sm:px-7 lg:px-10">
      {sections.map((s) => (
        <Link
          key={s.to}
          to={s.to}
          activeOptions={{ exact: true }}
          className="shrink-0 border-b-2 border-transparent px-3 py-3 text-sm font-medium text-muted-foreground hover:text-foreground"
          activeProps={{ className: "border-primary text-foreground" }}
        >
          {s.label}
        </Link>
      ))}
    </nav>
  );
}

export function PageShell({ eyebrow, title, intro, children }: { eyebrow: string; title: string; intro: string; children: ReactNode }) {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-10 bg-background/90 backdrop-blur-xl">
        <div className="flex h-16 items-center gap-2.5 px-4 sm:px-7 lg:px-10">
          <div className="grid size-9 place-items-center rounded-md bg-primary text-primary-foreground"><Waves className="size-5" /></div>
          <p className="text-sm font-bold">AI Swimming Coach</p>
        </div>
        <SectionNav />
      </header>
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-7 lg:px-10">
        <p className="text-xs font-semibold uppercase tracking-[0.13em] text-primary">{eyebrow}</p>
        <h1 className="mt-2 text-3xl font-extrabold">{title}</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">{intro}</p>
        <div className="mt-8">{children}</div>
      </div>
    </main>
  );
}

export function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-md border border-border bg-card p-5 shadow-panel">
      <h3 className="font-bold">{title}</h3>
      <div className="mt-3 text-sm leading-6 text-muted-foreground">{children}</div>
    </div>
  );
}

export function meta(title: string, description: string) {
  return {
    meta: [
      { title: `${title} — AI Swimming Coach` },
      { name: "description", content: description },
      { property: "og:title", content: `${title} — AI Swimming Coach` },
      { property: "og:description", content: description },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  };
}
