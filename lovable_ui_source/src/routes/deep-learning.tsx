import { createFileRoute } from "@tanstack/react-router";
import { Card, PageShell, meta } from "@/components/PageShell";

export const Route = createFileRoute("/deep-learning")({
  head: () => meta("Deep Learning", "Sequence models that learn stroke patterns directly from pose sequences."),
  component: Page,
});

function Page() {
  return (
    <PageShell eyebrow="Model lab" title="Deep learning" intro="Sequence models read whole stroke cycles of pose data to recognise technique patterns that simple features miss.">
      <div className="grid gap-4 sm:grid-cols-3">
        <Card title="LSTM">Learns temporal rhythm across stroke cycles. Sample F1: 0.86.</Card>
        <Card title="1D CNN">Detects short local motion patterns such as catch timing. Sample F1: 0.84.</Card>
        <Card title="Transformer">Attends across the full clip for long-range consistency. Sample F1: 0.90.</Card>
      </div>
      <div className="mt-6 rounded-md bg-secondary p-5 text-sm text-secondary-foreground">
        Pipeline: pose sequence → normalisation → model → per-cycle technique labels and confidence.
      </div>
    </PageShell>
  );
}
