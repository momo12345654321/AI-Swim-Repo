import { createFileRoute } from "@tanstack/react-router";
import { ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, PageShell, meta } from "@/components/PageShell";

export const Route = createFileRoute("/feedback-learning")({
  head: () => meta("Feedback Learning", "Rate coaching insights so the models improve over time."),
  component: Page,
});

const insights = ["Right-hand entry crosses the center line", "Hips drop during breathing", "Kick tempo is consistent"];

function Page() {
  const [votes, setVotes] = useState<Record<string, "up" | "down">>({});
  return (
    <PageShell eyebrow="Model lab" title="Feedback learning" intro="Swimmers and coaches confirm or reject each insight. Those ratings become new training labels.">
      <div className="space-y-3">
        {insights.map((i) => (
          <div key={i} className="flex items-center justify-between gap-4 rounded-md border border-border bg-card p-4 shadow-panel">
            <span className="text-sm">{i}</span>
            <div className="flex gap-2">
              <Button size="icon" variant={votes[i] === "up" ? "default" : "outline"} aria-label="Accurate" onClick={() => setVotes({ ...votes, [i]: "up" })}><ThumbsUp /></Button>
              <Button size="icon" variant={votes[i] === "down" ? "default" : "outline"} aria-label="Inaccurate" onClick={() => setVotes({ ...votes, [i]: "down" })}><ThumbsDown /></Button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6"><Card title="Ratings this session">{Object.keys(votes).length} of {insights.length} insights rated (stored in this browser only).</Card></div>
    </PageShell>
  );
}
