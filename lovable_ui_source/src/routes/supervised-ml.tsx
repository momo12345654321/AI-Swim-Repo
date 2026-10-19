import { createFileRoute } from "@tanstack/react-router";
import { Card, PageShell, meta } from "@/components/PageShell";

export const Route = createFileRoute("/supervised-ml")({
  head: () => meta("Supervised ML", "Classic models trained on labelled stroke features to detect technique faults."),
  component: Page,
});

const results = [["Random forest", 0.87], ["Gradient boosting", 0.89], ["Logistic regression", 0.78], ["SVM", 0.82]] as const;

function Page() {
  return (
    <PageShell eyebrow="Model lab" title="Supervised ML" intro="Labelled clips train classic classifiers that flag common faults like crossover entry, dropped elbow, and late breathing.">
      <div className="rounded-md border border-border bg-card p-5 shadow-panel">
        <h3 className="font-bold">Validation accuracy (sample)</h3>
        <div className="mt-4 space-y-3">
          {results.map(([name, acc]) => (
            <div key={name}>
              <div className="flex justify-between text-sm"><span>{name}</span><span className="font-mono">{(acc * 100).toFixed(0)}%</span></div>
              <div className="mt-1 h-2 rounded bg-secondary"><div className="h-2 rounded bg-chart-1" style={{ width: `${acc * 100}%` }} /></div>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <Card title="Features">Time-series statistics: angle ranges, cycle timing, symmetry.</Card>
        <Card title="Labels">Coach-annotated fault categories per stroke cycle.</Card>
        <Card title="Status">Sample figures shown — connect a training service for live results.</Card>
      </div>
    </PageShell>
  );
}
