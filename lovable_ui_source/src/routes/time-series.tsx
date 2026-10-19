import { createFileRoute } from "@tanstack/react-router";
import { Card, PageShell, meta } from "@/components/PageShell";

export const Route = createFileRoute("/time-series")({
  head: () => meta("Time-Series Data", "Joint angles, speed, and symmetry tracked frame by frame."),
  component: Page,
});

const series = [
  { name: "Right elbow angle (°)", color: "var(--color-chart-1)", values: [120, 135, 150, 110, 95, 130, 148, 112, 98, 128] },
  { name: "Left elbow angle (°)", color: "var(--color-chart-2)", values: [110, 98, 125, 140, 118, 100, 122, 145, 115, 102] },
];

function Page() {
  const toPts = (v: number[]) => v.map((y, i) => `${(i / (v.length - 1)) * 300},${160 - ((y - 80) / 80) * 150}`).join(" ");
  return (
    <PageShell eyebrow="Output 02" title="Time-series data" intro="Every processed frame produces measurements you can chart, compare across sessions, and export for training models.">
      <div className="rounded-md border border-border bg-card p-5 shadow-panel">
        <svg viewBox="0 0 300 160" className="h-64 w-full" preserveAspectRatio="none">
          {series.map((s) => <polyline key={s.name} points={toPts(s.values)} fill="none" stroke={s.color} strokeWidth="2" vectorEffect="non-scaling-stroke" />)}
        </svg>
        <div className="mt-3 flex flex-wrap gap-4 text-xs">
          {series.map((s) => <span key={s.name} className="flex items-center gap-2"><span className="size-2.5 rounded-full" style={{ background: s.color }} />{s.name}</span>)}
        </div>
      </div>
      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <Card title="Joint angles">Elbow, shoulder, hip, and knee angles per frame.</Card>
        <Card title="Body line">Hip drop and head position relative to the waterline.</Card>
        <Card title="CSV export">Structured features ready for spreadsheets or ML pipelines.</Card>
      </div>
    </PageShell>
  );
}
