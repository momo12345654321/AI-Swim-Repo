import { createFileRoute } from "@tanstack/react-router";
import {
  Activity,
  ArrowRight,
  BarChart3,
  Check,
  ChevronRight,
  CircleGauge,
  FileVideo,
  Gauge,
  Info,
  Menu,
  Play,
  RotateCcw,
  ShieldCheck,
  Sparkle,
  Timer,
  Upload,
  Waves,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Slider } from "@/components/ui/slider";
import { SectionNav } from "@/components/PageShell";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "AI Swimming Coach — Video Technique Analysis" },
      {
        name: "description",
        content: "Upload swimming footage and review pose, pacing, symmetry, and technique insights.",
      },
      { property: "og:title", content: "AI Swimming Coach — Video Technique Analysis" },
      {
        property: "og:description",
        content: "A focused video analysis workspace for swimmers and coaches.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: SwimCoach,
});

type Settings = {
  engine: string;
  maxFrames: number;
  stride: number;
  width: number;
  poseDetection: number;
  poseTracking: number;
};

const initialSettings: Settings = {
  engine: "automatic",
  maxFrames: 450,
  stride: 2,
  width: 720,
  poseDetection: 0.5,
  poseTracking: 0.5,
};

function RangeSetting({
  label,
  value,
  display,
  min,
  max,
  step = 1,
  onChange,
}: {
  label: string;
  value: number;
  display?: string;
  min: number;
  max: number;
  step?: number;
  onChange: (value: number) => void;
}) {
  return (
    <div className="space-y-2.5">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3">
        <label className="min-w-0 text-xs font-medium text-sidebar-foreground">{label}</label>
        <span className="shrink-0 font-mono text-xs font-semibold text-primary">
          {display ?? value}
        </span>
      </div>
      <Slider
        aria-label={label}
        min={min}
        max={max}
        step={step}
        value={[value]}
        onValueChange={(next) => onChange(next[0] ?? value)}
      />
    </div>
  );
}

function SettingsPanel({ settings, setSettings }: { settings: Settings; setSettings: (value: Settings) => void }) {
  const update = <K extends keyof Settings>(key: K, value: Settings[K]) =>
    setSettings({ ...settings, [key]: value });

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-sidebar-border px-5 py-6">
        <div className="flex items-center gap-2.5">
          <div className="grid size-9 shrink-0 place-items-center rounded-md bg-sidebar-primary text-sidebar-primary-foreground">
            <Waves className="size-5" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-bold text-sidebar-foreground">AI Swimming Coach</p>
            <p className="text-xs text-muted-foreground">Motion intelligence lab</p>
          </div>
        </div>
      </div>

      <div className="flex-1 space-y-7 overflow-y-auto px-5 py-6">
        <section>
          <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.14em] text-muted-foreground">Project team</p>
          <div className="space-y-1 text-xs leading-5 text-sidebar-foreground">
            <p><span className="text-muted-foreground">Author</span> · Jasper Ding</p>
            <p><span className="text-muted-foreground">Advisor</span> · Dr. Qingyang Xiao</p>
          </div>
        </section>

        <section className="space-y-5 border-t border-sidebar-border pt-6">
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-sidebar-foreground">Analysis settings</p>
            <CircleGauge className="size-4 text-primary" />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-sidebar-foreground">Analysis engine</label>
            <Select value={settings.engine} onValueChange={(value) => update("engine", value)}>
              <SelectTrigger className="h-10 bg-sidebar-accent text-xs shadow-none">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="automatic">Automatic · MediaPipe</SelectItem>
                <SelectItem value="precision">Precision pose model</SelectItem>
                <SelectItem value="opencv">OpenCV fallback</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <RangeSetting label="Maximum processed frames" value={settings.maxFrames} min={150} max={900} step={50} onChange={(v) => update("maxFrames", v)} />
          <RangeSetting label="Frame stride" value={settings.stride} min={1} max={6} onChange={(v) => update("stride", v)} />
          <RangeSetting label="Analysis width" value={settings.width} display={`${settings.width}px`} min={480} max={1080} step={120} onChange={(v) => update("width", v)} />
          <RangeSetting label="Pose detection confidence" value={settings.poseDetection} display={settings.poseDetection.toFixed(2)} min={0.1} max={0.9} step={0.05} onChange={(v) => update("poseDetection", v)} />
          <RangeSetting label="Pose tracking confidence" value={settings.poseTracking} display={settings.poseTracking.toFixed(2)} min={0.1} max={0.9} step={0.05} onChange={(v) => update("poseTracking", v)} />
        </section>
      </div>

      <div className="border-t border-sidebar-border p-5">
        <div className="flex items-start gap-2 text-xs leading-5 text-muted-foreground">
          <Info className="mt-0.5 size-3.5 shrink-0" />
          <p>For best results, use a stable 5–20 second side-view clip with the full swimmer visible.</p>
        </div>
      </div>
    </div>
  );
}

const metrics = [
  { label: "Stroke rate", value: "31", suffix: "spm", icon: Activity, trend: "Optimal" },
  { label: "Symmetry", value: "92", suffix: "%", icon: BarChart3, trend: "+4%" },
  { label: "Est. pace", value: "1:42", suffix: "/100m", icon: Timer, trend: "−0:03" },
];

function SwimCoach() {
  const [settings, setSettings] = useState(initialSettings);
  const [file, setFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<"ready" | "processing" | "complete">("ready");
  const [progress, setProgress] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!file) {
      setVideoUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setVideoUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  useEffect(() => {
    if (status !== "processing") return;
    const timer = window.setInterval(() => {
      setProgress((current) => {
        if (current >= 100) {
          window.clearInterval(timer);
          setStatus("complete");
          return 100;
        }
        return Math.min(current + 4, 100);
      });
    }, 90);
    return () => window.clearInterval(timer);
  }, [status]);

  const selectFile = (next?: File) => {
    if (!next) return;
    setFile(next);
    setStatus("ready");
    setProgress(0);
  };

  const reset = () => {
    setFile(null);
    setStatus("ready");
    setProgress(0);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <main className="min-h-screen bg-background text-foreground">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-sidebar-border bg-sidebar lg:block">
        <SettingsPanel settings={settings} setSettings={setSettings} />
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-10 border-b border-border bg-background/90 backdrop-blur-xl">
          <div className="mx-auto grid h-16 max-w-7xl grid-cols-[minmax(0,1fr)_auto] items-center gap-4 px-4 sm:px-7 lg:px-10">
            <div className="flex min-w-0 items-center gap-3">
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon" className="shrink-0 lg:hidden" aria-label="Open analysis settings">
                    <Menu />
                  </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-[88vw] max-w-80 border-sidebar-border bg-sidebar p-0">
                  <SheetTitle className="sr-only">Analysis settings</SheetTitle>
                  <SettingsPanel settings={settings} setSettings={setSettings} />
                </SheetContent>
              </Sheet>
              <div className="min-w-0">
                <p className="truncate text-sm font-bold">Performance workspace</p>
                <p className="hidden text-xs text-muted-foreground sm:block">Video pose & technique analysis</p>
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-2">
              <span className="hidden items-center gap-1.5 rounded-full bg-success-soft px-3 py-1.5 text-xs font-semibold text-success sm:flex">
                <span className="size-1.5 rounded-full bg-success" /> Models ready
              </span>
              {file && (
                <Button variant="ghost" size="icon" onClick={reset} aria-label="Start over" title="Start over">
                  <RotateCcw />
                </Button>
              )}
            </div>
          </div>
          <SectionNav />
        </header>

        <div className="mx-auto max-w-7xl px-4 py-7 sm:px-7 sm:py-10 lg:px-10">
          <section className="mb-8 overflow-hidden rounded-lg bg-hero px-6 py-8 text-hero-foreground shadow-hero sm:px-9 sm:py-10">
            <div className="max-w-3xl">
              <div className="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-hero-muted">
                <Sparkle className="size-4" /> Computer vision coaching
              </div>
              <h1 className="text-3xl font-extrabold sm:text-4xl">See what your stroke is saying.</h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-hero-muted sm:text-base">
                Turn a short poolside video into clear technique signals, movement metrics, and focused coaching cues.
              </p>
            </div>
          </section>

          <div className="mb-8 flex items-start gap-3 rounded-md border border-info-border bg-info-soft px-4 py-3 text-sm text-info-foreground">
            <ShieldCheck className="mt-0.5 size-4 shrink-0" />
            <p><strong>Prototype analysis.</strong> Pose-derived scores support coaching review and are not a substitute for an in-person qualified coach.</p>
          </div>

          {status !== "complete" ? (
            <section className="grid gap-8 xl:grid-cols-[minmax(0,1.4fr)_minmax(280px,0.6fr)]">
              <div>
                <div className="mb-3 grid gap-1 sm:grid-cols-[minmax(0,1fr)_auto] sm:items-end sm:gap-4">
                  <div className="min-w-0">
                    <p className="text-xs font-semibold uppercase tracking-[0.13em] text-primary">Step 01</p>
                    <h2 className="mt-1 text-xl font-bold">Upload a swimming video</h2>
                  </div>
                  <span className="text-xs text-muted-foreground sm:shrink-0">MP4, MOV, AVI · 300MB max</span>
                </div>

                {!file ? (
                  <button
                    type="button"
                    onClick={() => inputRef.current?.click()}
                    onDragOver={(event) => event.preventDefault()}
                    onDrop={(event) => {
                      event.preventDefault();
                      selectFile(event.dataTransfer.files[0]);
                    }}
                    className="group grid min-h-80 w-full cursor-pointer place-items-center rounded-lg border border-dashed border-upload-border bg-upload p-8 text-center transition-colors hover:border-primary hover:bg-upload-active focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  >
                    <div>
                      <div className="mx-auto grid size-14 place-items-center rounded-full bg-primary text-primary-foreground shadow-primary">
                        <Upload className="size-6" />
                      </div>
                      <p className="mt-5 text-base font-bold">Drop your swim clip here</p>
                      <p className="mt-1 text-sm text-muted-foreground">or click to choose a file from your device</p>
                      <span className="mt-5 inline-flex items-center gap-2 text-sm font-semibold text-primary">
                        Choose video <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
                      </span>
                    </div>
                  </button>
                ) : (
                  <div className="overflow-hidden rounded-lg border border-border bg-card shadow-panel">
                    <div className="relative aspect-video bg-video">
                      {videoUrl && <video src={videoUrl} controls className="h-full w-full object-contain" />}
                      {status === "processing" && (
                        <div className="absolute inset-0 grid place-items-center bg-video-overlay backdrop-blur-sm">
                          <div className="w-full max-w-xs px-6 text-center text-video-foreground">
                            <Activity className="mx-auto size-8 animate-pulse text-accent" />
                            <p className="mt-4 font-bold">Mapping swimmer motion</p>
                            <p className="mt-1 text-xs text-video-muted">Detecting landmarks and stroke phases</p>
                            <Progress value={progress} className="mt-5 bg-video-track" />
                            <p className="mt-2 font-mono text-xs">{progress}%</p>
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4 p-4">
                      <div className="flex min-w-0 items-center gap-3">
                        <div className="grid size-9 shrink-0 place-items-center rounded-md bg-secondary text-primary"><FileVideo className="size-4" /></div>
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold">{file.name}</p>
                          <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(1)} MB · Ready for analysis</p>
                        </div>
                      </div>
                      <Button
                        onClick={() => {
                          setProgress(0);
                          setStatus("processing");
                        }}
                        disabled={status === "processing"}
                        className="shrink-0"
                      >
                        <Play /> <span className="hidden sm:inline">Analyze video</span>
                      </Button>
                    </div>
                  </div>
                )}
                <input
                  ref={inputRef}
                  className="sr-only"
                  type="file"
                  accept="video/mp4,video/quicktime,video/x-msvideo,video/webm"
                  onChange={(event) => selectFile(event.target.files?.[0])}
                />
              </div>

              <aside className="border-l border-border pl-6 xl:pt-8">
                <p className="text-sm font-bold">Recording checklist</p>
                <div className="mt-4 space-y-3">
                  {["Keep the entire swimmer in frame", "Prefer a stable side view", "Reduce glare, splashes, and obstructions", "Avoid uploading sensitive footage"].map((item) => (
                    <div key={item} className="flex items-start gap-2.5 text-sm leading-5 text-muted-foreground">
                      <Check className="mt-0.5 size-4 shrink-0 text-success" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
                <div className="mt-7 rounded-md bg-secondary p-4">
                  <p className="text-xs font-bold uppercase tracking-[0.12em] text-primary">Capture tip</p>
                  <p className="mt-2 text-sm leading-5 text-secondary-foreground">Place the camera near hip height and keep it still through at least three full stroke cycles.</p>
                </div>
              </aside>
            </section>
          ) : (
            <Results fileName={file?.name ?? "swim-session.mp4"} onReset={reset} />
          )}

          {status !== "complete" && (
            <section className="mt-14 border-t border-border pt-9">
              <div className="grid gap-8 lg:grid-cols-[0.55fr_1fr]">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.13em] text-primary">Analysis output</p>
                  <h2 className="mt-2 text-2xl font-bold">From footage to focused feedback.</h2>
                </div>
                <div className="grid gap-x-8 gap-y-6 sm:grid-cols-2">
                  {[
                    ["Annotated movement", "Pose landmarks reveal alignment and stroke timing frame by frame."],
                    ["Time-series data", "Joint angles, movement speed, symmetry, and body-line features."],
                    ["Coaching insights", "Clear observations and training cues grounded in the detected motion."],
                    ["Trainable baseline", "Structured outputs prepared for future model comparison and feedback."],
                  ].map(([title, copy], index) => (
                    <div key={title} className="flex gap-3">
                      <span className="font-mono text-xs font-bold text-primary">0{index + 1}</span>
                      <div><h3 className="text-sm font-bold">{title}</h3><p className="mt-1 text-sm leading-6 text-muted-foreground">{copy}</p></div>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          )}
        </div>
      </div>
    </main>
  );
}

function Results({ fileName, onReset }: { fileName: string; onReset: () => void }) {
  return (
    <section className="animate-in fade-in slide-in-from-bottom-2 duration-500">
      <div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4 border-b border-border pb-5">
        <div className="min-w-0">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.13em] text-success"><Check className="size-4" /> Analysis complete</div>
          <h2 className="mt-1 truncate text-2xl font-bold">Session performance</h2>
          <p className="truncate text-sm text-muted-foreground">{fileName}</p>
        </div>
        <Button variant="outline" onClick={onReset} className="shrink-0"><RotateCcw /> <span className="hidden sm:inline">New analysis</span></Button>
      </div>

      <div className="mt-6 grid gap-3 sm:grid-cols-3">
        {metrics.map(({ label, value, suffix, icon: Icon, trend }) => (
          <div key={label} className="rounded-md border border-border bg-card p-5 shadow-panel">
            <div className="flex items-center justify-between"><Icon className="size-4 text-primary" /><span className="text-xs font-semibold text-success">{trend}</span></div>
            <p className="mt-5 text-xs text-muted-foreground">{label}</p>
            <p className="mt-1 text-3xl font-extrabold">{value}<span className="ml-1 text-sm font-medium text-muted-foreground">{suffix}</span></p>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-md border border-border bg-card p-5 shadow-panel sm:p-6">
          <div className="flex items-center justify-between"><h3 className="font-bold">Stroke consistency</h3><span className="text-xs text-muted-foreground">8 cycles</span></div>
          <div className="mt-7 flex h-48 items-end gap-3 border-b border-border px-2">
            {[68, 76, 72, 84, 79, 91, 86, 93].map((height, index) => (
              <div key={index} className="flex h-full flex-1 flex-col items-center justify-end gap-2">
                <div className="w-full max-w-10 rounded-t-sm bg-chart-1 transition-all" style={{ height: `${height}%` }} />
                <span className="pb-2 font-mono text-[10px] text-muted-foreground">{index + 1}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-md bg-coach px-5 py-6 text-coach-foreground shadow-panel sm:px-6">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.13em] text-coach-muted"><Sparkle className="size-4 text-accent" /> Coach's focus</div>
          <h3 className="mt-4 text-xl font-bold">Hold your line through entry.</h3>
          <p className="mt-3 text-sm leading-6 text-coach-muted">Your right-hand entry crosses the center line on cycles 3–5. Aim fingertips forward at shoulder width before beginning the catch.</p>
          <div className="mt-6 space-y-3 border-t border-coach-border pt-5">
            {["6 × 25m single-arm drill", "Focus: right-side alignment", "Rest 20 seconds between reps"].map((item) => (
              <div key={item} className="flex items-center gap-2 text-sm"><ChevronRight className="size-4 shrink-0 text-accent" /> {item}</div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
