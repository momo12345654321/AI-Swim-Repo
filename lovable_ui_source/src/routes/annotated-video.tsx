import { createFileRoute } from "@tanstack/react-router";
import { Card, PageShell, meta } from "@/components/PageShell";

export const Route = createFileRoute("/annotated-video")({
  head: () => meta("Annotated Video", "Pose landmarks and stroke phases overlaid on your swim footage."),
  component: Page,
});

function Page() {
  return (
    <PageShell eyebrow="Output 01" title="Annotated video" intro="After analysis, your clip is replayed with pose landmarks, skeleton lines, and stroke-phase labels drawn over each frame.">
      <div className="relative aspect-video overflow-hidden rounded-lg bg-video">
        <svg viewBox="0 0 160 90" className="h-full w-full">
          <g stroke="var(--color-accent)" strokeWidth="1.2" fill="none">
            <polyline points="30,50 50,46 75,45 100,47 120,50" />
            <polyline points="50,46 62,36 78,30" />
            <polyline points="100,47 115,56 135,58" />
          </g>
          {[[30,50],[50,46],[75,45],[100,47],[120,50],[62,36],[78,30],[115,56],[135,58]].map(([x,y],i)=>(
            <circle key={i} cx={x} cy={y} r="1.8" fill="var(--color-primary)" />
          ))}
        </svg>
        <span className="absolute left-4 top-4 rounded bg-video-overlay px-2 py-1 font-mono text-xs text-video-foreground">Phase: Catch · Frame 128</span>
      </div>
      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <Card title="Landmarks">33 body keypoints tracked per frame.</Card>
        <Card title="Stroke phases">Entry, catch, pull, push, and recovery labelled automatically.</Card>
        <Card title="Download">Export the annotated MP4 once a real analysis service is connected.</Card>
      </div>
    </PageShell>
  );
}
