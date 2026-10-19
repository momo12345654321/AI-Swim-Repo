import { createFileRoute } from "@tanstack/react-router";
import { Card, PageShell, meta } from "@/components/PageShell";

export const Route = createFileRoute("/about")({
  head: () => meta("About", "The research project behind the AI Swimming Coach."),
  component: Page,
});

function Page() {
  return (
    <PageShell eyebrow="Project" title="About" intro="AI Swimming Coach explores how computer vision and machine learning can give swimmers accessible technique feedback from a simple video.">
      <div className="grid gap-4 sm:grid-cols-2">
        <Card title="Team">Author · Jasper Ding<br />Advisor · Dr. Qingyang Xiao</Card>
        <Card title="Disclaimer">This is a research prototype. Insights support, but do not replace, a qualified in-person coach.</Card>
      </div>
    </PageShell>
  );
}
