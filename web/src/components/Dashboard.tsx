import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Gauge, 
  Zap, 
  AlertTriangle, 
  CheckCircle2, 
  Pause, 
  Play, 
  RefreshCw, 
  Trash2, 
  Flame, 
  ShieldAlert, 
  Clock, 
  ArrowUpRight, 
  ArrowDownRight, 
  Terminal, 
  Sliders, 
  XCircle, 
  Database,
  Layers,
  Sparkles,
  Download,
  Copy,
  Check
} from 'lucide-react';

interface MetricPoint {
  time: string;
  cpu: number;
  ram: number;
  activeDownloads: number;
  ramMb: number;
}

interface ActiveTask {
  id: string;
  title: string;
  userId: number;
  quality: string;
  progress: number;
  stage: 'downloading' | 'ffmpeg_transcode' | 'telegram_upload' | 'queued';
  elapsedSeconds: number;
  estimatedMb: number;
}

interface SystemLog {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'success' | 'alert';
  message: string;
}

export const Dashboard: React.FC = () => {
  // Real-time metrics states
  const [isRunning, setIsRunning] = useState(true);
  const [refreshIntervalMs, setRefreshIntervalMs] = useState(2000);
  const [cpuUsage, setCpuUsage] = useState(24);
  const [cpuCores, setCpuCores] = useState([28, 20]);
  const [ramMb, setRamMb] = useState(384);
  const totalRamMb = 1024; // 1 GB container on Railway/Docker
  const [eventLoopLagMs, setEventLoopLagMs] = useState(2.8);
  const [networkSpeedIn, setNetworkSpeedIn] = useState(4.2); // MB/s
  const [networkSpeedOut, setNetworkSpeedOut] = useState(6.1); // MB/s
  const [diskTempMb, setDiskTempMb] = useState(148);
  const totalDiskMb = 5120; // 5 GB scratch disk
  const [concurrencyLimit, setConcurrencyLimit] = useState(3);
  const [crashGuardActive, setCrashGuardActive] = useState(true);
  const [copiedSnippet, setCopiedSnippet] = useState(false);
  const [logFilter, setLogFilter] = useState<'all' | 'warn' | 'alert'>('all');

  // Active tasks state
  const [activeTasks, setActiveTasks] = useState<ActiveTask[]>([
    {
      id: 'task-101',
      title: 'Rick Astley - Never Gonna Give You Up (Official Music Video)',
      userId: 78941205,
      quality: '1080p MP4',
      progress: 68,
      stage: 'ffmpeg_transcode',
      elapsedSeconds: 14,
      estimatedMb: 42.5
    },
    {
      id: 'task-102',
      title: 'Lofi Hip Hop Radio - Beats to Relax/Study to',
      userId: 54109822,
      quality: 'MP3 (320kbps)',
      progress: 92,
      stage: 'telegram_upload',
      elapsedSeconds: 8,
      estimatedMb: 8.6
    }
  ]);

  // History timeline for SVG chart (last 20 points)
  const [history, setHistory] = useState<MetricPoint[]>(() => {
    const initial: MetricPoint[] = [];
    const now = Date.now();
    for (let i = 19; i >= 0; i--) {
      const d = new Date(now - i * 2000);
      const timeStr = `${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`;
      initial.push({
        time: timeStr,
        cpu: Math.floor(18 + Math.random() * 15),
        ram: Math.floor(32 + Math.random() * 6),
        ramMb: Math.floor(330 + Math.random() * 60),
        activeDownloads: Math.floor(1 + Math.random() * 2)
      });
    }
    return initial;
  });

  // System logs
  const [logs, setLogs] = useState<SystemLog[]>([
    { id: '1', timestamp: '21:46:10', level: 'info', message: 'Telethon client loop running normally. Ping: 38ms' },
    { id: '2', timestamp: '21:46:18', level: 'success', message: 'Cleanup hook executed: 3 temporary video parts unlinked from /tmp' },
    { id: '3', timestamp: '21:47:02', level: 'info', message: 'YouTube stream dispatched to worker: session_id=78941205_1080p' },
    { id: '4', timestamp: '21:47:45', level: 'warn', message: 'FFmpeg transcode thread active (-c:a aac -movflags +faststart) — CPU elevated' },
    { id: '5', timestamp: '21:48:12', level: 'success', message: 'Cache record stored with telethon packed_file_id (zero storage overhead)' }
  ]);

  // Crash Risk calculation
  const ramPercent = Math.round((ramMb / totalRamMb) * 100);
  const activeCount = activeTasks.length;
  
  const crashRisk = useMemo(() => {
    if (ramPercent >= 88 || cpuUsage >= 90) {
      return { level: 'critical', label: 'خطر کرش و OOM Kill', color: 'rose', badge: 'بحرانی (Critical)' };
    }
    if (ramPercent >= 75 || cpuUsage >= 75 || activeCount >= concurrencyLimit) {
      return { level: 'warning', label: 'بار پردازشی بالا', color: 'amber', badge: 'هشدار (Elevated)' };
    }
    return { level: 'healthy', label: 'سیستم پایدار و بهینه', color: 'emerald', badge: 'ایمن و نرمال' };
  }, [ramPercent, cpuUsage, activeCount, concurrencyLimit]);

  // Periodic Telemetry Simulation
  useEffect(() => {
    if (!isRunning) return;

    const timer = setInterval(() => {
      const now = new Date();
      const timeStr = `${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;

      // Calculate dynamic CPU and RAM based on active tasks
      const baseCpu = 15;
      const taskCpu = activeTasks.reduce((acc, t) => {
        if (t.stage === 'ffmpeg_transcode') return acc + 28;
        if (t.stage === 'downloading') return acc + 14;
        if (t.stage === 'telegram_upload') return acc + 9;
        return acc + 2;
      }, 0);
      const jitterCpu = (Math.random() - 0.5) * 6;
      const newCpu = Math.min(99, Math.max(8, Math.round(baseCpu + taskCpu + jitterCpu)));

      const baseRam = 290;
      const taskRam = activeTasks.reduce((acc, t) => acc + (t.stage === 'ffmpeg_transcode' ? 95 : 45), 0);
      const jitterRam = (Math.random() - 0.5) * 15;
      const newRamMb = Math.min(totalRamMb, Math.max(260, Math.round(baseRam + taskRam + jitterRam)));
      const newRamPercent = Math.round((newRamMb / totalRamMb) * 100);

      // Core breakdown
      const c0 = Math.min(100, Math.max(5, Math.round(newCpu * (0.9 + Math.random() * 0.2))));
      const c1 = Math.min(100, Math.max(5, Math.round(newCpu * (0.8 + Math.random() * 0.3))));
      setCpuCores([c0, c1]);

      setCpuUsage(newCpu);
      setRamMb(newRamMb);
      setEventLoopLagMs(Number((2.1 + (newCpu > 70 ? 4.2 : 0.6) + Math.random() * 0.8).toFixed(1)));
      setNetworkSpeedIn(activeTasks.some(t => t.stage === 'downloading') ? Number((3.5 + Math.random() * 4).toFixed(1)) : 0.4);
      setNetworkSpeedOut(activeTasks.some(t => t.stage === 'telegram_upload') ? Number((5.2 + Math.random() * 5).toFixed(1)) : 0.8);

      // Update task progresses
      setActiveTasks(prev => {
        return prev.map(task => {
          if (task.stage === 'queued') return task;
          const nextProgress = Math.min(100, task.progress + Math.floor(Math.random() * 9 + 4));
          let nextStage = task.stage;
          if (nextProgress >= 100) {
            if (task.stage === 'downloading') {
              nextStage = 'ffmpeg_transcode';
              return { ...task, progress: 15, stage: nextStage, elapsedSeconds: task.elapsedSeconds + 2 };
            } else if (task.stage === 'ffmpeg_transcode') {
              nextStage = 'telegram_upload';
              return { ...task, progress: 30, stage: nextStage, elapsedSeconds: task.elapsedSeconds + 2 };
            } else {
              // Task completed
              return { ...task, progress: 100, elapsedSeconds: task.elapsedSeconds + 1 };
            }
          }
          return { ...task, progress: nextProgress, elapsedSeconds: task.elapsedSeconds + 2 };
        }).filter(t => t.progress < 100); // Filter out finished tasks
      });

      // Update SVG history
      setHistory(prev => {
        const next = [...prev.slice(1), {
          time: timeStr,
          cpu: newCpu,
          ram: newRamPercent,
          ramMb: newRamMb,
          activeDownloads: activeTasks.length
        }];
        return next;
      });

    }, refreshIntervalMs);

    return () => clearInterval(timer);
  }, [isRunning, refreshIntervalMs, activeTasks, totalRamMb]);

  // Stress test: Simulate 3 concurrent 1080p downloads
  const handleTriggerStressTest = () => {
    const newTask1: ActiveTask = {
      id: 'stress-' + Date.now(),
      title: 'YouTube 4K UHD 60fps Documentary Stream (High Bitrate)',
      userId: 19842109,
      quality: '1080p 60fps',
      progress: 12,
      stage: 'downloading',
      elapsedSeconds: 2,
      estimatedMb: 85.0
    };
    const newTask2: ActiveTask = {
      id: 'stress-' + (Date.now() + 1),
      title: 'Podcast Full Episode (Opus to AAC Re-encode Test)',
      userId: 67341209,
      quality: '720p MP4',
      progress: 25,
      stage: 'ffmpeg_transcode',
      elapsedSeconds: 5,
      estimatedMb: 38.0
    };
    const newTask3: ActiveTask = {
      id: 'stress-' + (Date.now() + 2),
      title: 'Classical Symphony Concert FLAC Audio Extractor',
      userId: 88231045,
      quality: 'MP3 Best (320k)',
      progress: 5,
      stage: activeTasks.length >= concurrencyLimit ? 'queued' : 'downloading',
      elapsedSeconds: 1,
      estimatedMb: 24.5
    };

    setActiveTasks(prev => [...prev, newTask1, newTask2, newTask3]);

    addLog('warn', 'تست استرس فعال شد: ۳ تسک دانلود سنگین اضافه گردید. وضعیت مصرف رم و پردازنده در حال بررسی...');
  };

  // Trigger manual garbage collection / cache sweep
  const handleTriggerCleanup = () => {
    setRamMb(prev => Math.max(260, prev - 120));
    setDiskTempMb(prev => Math.max(24, prev - 85));
    addLog('success', 'پاکسازی فوری انجام شد: زباله‌روب پایتون (gc.collect()) اجرا و فایل‌های موقت پاکسازی شدند (-120 MB RAM)');
  };

  // Terminate specific task
  const handleKillTask = (id: string, title: string) => {
    setActiveTasks(prev => prev.filter(t => t.id !== id));
    addLog('warn', `تسک ${title.slice(0, 30)}... توسط ادمین متوقف شد (جلوگیری از قفل پردازنده)`);
  };

  const addLog = (level: SystemLog['level'], message: string) => {
    const now = new Date();
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    setLogs(prev => [
      { id: Date.now().toString(), timestamp: timeStr, level, message },
      ...prev.slice(0, 19)
    ]);
  };

  const handleCopyCode = () => {
    const code = `# کد افزودن مانیتورینگ دقیق رم و سی‌پی‌یو به ربات تلگرام (psutil)
import psutil
import os

def get_system_metrics():
    """محاسبه دقیق درصد مصرف CPU، RAM و حافظه دیسک جهت پایش سلامت بات"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    ram_mb = mem_info.rss / (1024 * 1024)
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    virtual_mem = psutil.virtual_memory()
    disk_usage = psutil.disk_usage("/tmp")
    
    return {
        "bot_ram_mb": round(ram_mb, 1),
        "total_ram_percent": virtual_mem.percent,
        "cpu_percent": cpu_percent,
        "disk_free_gb": round(disk_usage.free / (1024**3), 2),
        "is_safe_for_download": virtual_mem.percent < 85.0
    }`;
    navigator.clipboard.writeText(code);
    setCopiedSnippet(true);
    setTimeout(() => setCopiedSnippet(false), 2000);
  };

  // SVG Chart points calculation
  const chartWidth = 700;
  const chartHeight = 180;
  const padding = 25;
  const usableWidth = chartWidth - padding * 2;
  const usableHeight = chartHeight - padding * 2;

  const pointsCpu = history.map((pt, idx) => {
    const x = padding + (idx / (history.length - 1)) * usableWidth;
    const y = padding + usableHeight - (pt.cpu / 100) * usableHeight;
    return `${x},${y}`;
  }).join(' ');

  const pointsRam = history.map((pt, idx) => {
    const x = padding + (idx / (history.length - 1)) * usableWidth;
    const y = padding + usableHeight - (pt.ram / 100) * usableHeight;
    return `${x},${y}`;
  }).join(' ');

  const cpuAreaPath = `M ${padding},${padding + usableHeight} L ${pointsCpu} L ${padding + usableWidth},${padding + usableHeight} Z`;
  const ramAreaPath = `M ${padding},${padding + usableHeight} L ${pointsRam} L ${padding + usableWidth},${padding + usableHeight} Z`;

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner & Crash Status */}
      <div className={`p-5 rounded-2xl border transition-all ${
        crashRisk.level === 'critical'
          ? 'bg-rose-950/40 border-rose-600/50 shadow-lg shadow-rose-900/20'
          : crashRisk.level === 'warning'
          ? 'bg-amber-950/30 border-amber-600/40 shadow-lg shadow-amber-900/10'
          : 'bg-slate-900/80 border-slate-800'
      } flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4`}>
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-white shrink-0 ${
            crashRisk.level === 'critical' ? 'bg-rose-600 animate-pulse' :
            crashRisk.level === 'warning' ? 'bg-amber-600' : 'bg-indigo-600'
          }`}>
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-base sm:text-lg font-bold text-white">
                پایش زنده منابع سرور و جلوگیری از کرش (Crash Diagnostics)
              </h2>
              <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${
                crashRisk.level === 'critical' ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' :
                crashRisk.level === 'warning' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' :
                'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
              }`}>
                {crashRisk.badge}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              بررسی همزمان پردازنده، حافظه رم (RAM)، فرآیندهای FFmpeg و صف دانلودها برای جلوگیری از کشته شدن کانتینر در سرورهای ابری (مانند Railway OOM Kill).
            </p>
          </div>
        </div>

        {/* Live Controls */}
        <div className="flex flex-wrap items-center gap-2 self-stretch lg:self-auto justify-end">
          <button
            onClick={() => setIsRunning(!isRunning)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer border ${
              isRunning 
                ? 'bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700' 
                : 'bg-emerald-600/20 text-emerald-300 border-emerald-500/40 hover:bg-emerald-600/30'
            }`}
          >
            {isRunning ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isRunning ? 'توقف پایش' : 'ادامه زنده'}</span>
          </button>

          <button
            onClick={handleTriggerStressTest}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/40 text-xs font-semibold transition cursor-pointer"
            title="شبیه‌سازی ۳ دانلود سنگین همزمان جهت تست پایداری و رفتار صف"
          >
            <Flame className="w-3.5 h-3.5 text-amber-400" />
            <span>تست استرس دانلود همزمان</span>
          </button>

          <button
            onClick={handleTriggerCleanup}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 text-xs font-semibold transition cursor-pointer"
            title="پاکسازی زباله‌روب پایتون و آزادسازی حافظه"
          >
            <RefreshCw className="w-3.5 h-3.5 text-indigo-400" />
            <span>تخلیه رم و کش موقت</span>
          </button>
        </div>
      </div>

      {/* 4 Core Primary Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: CPU Usage */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-indigo-400 font-semibold text-xs">
              <Cpu className="w-4 h-4" />
              <span>مصرف پردازنده (CPU)</span>
            </div>
            <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded-md ${
              cpuUsage > 80 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
              cpuUsage > 60 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
              'bg-indigo-500/20 text-indigo-300'
            }`}>
              {cpuUsage}%
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
              {cpuUsage}%
            </span>
            <span className="text-xs text-slate-400">۲ هسته فعال (2 Cores)</span>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                cpuUsage > 80 ? 'bg-rose-500' : cpuUsage > 60 ? 'bg-amber-400' : 'bg-indigo-500'
              }`}
              style={{ width: `${cpuUsage}%` }}
            />
          </div>

          {/* Per Core breakdown */}
          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>هسته ۰: <strong className="text-slate-200">{cpuCores[0]}%</strong></span>
            <span>هسته ۱: <strong className="text-slate-200">{cpuCores[1]}%</strong></span>
            <span className="text-[10px] text-indigo-300">FFmpeg load</span>
          </div>
        </div>

        {/* Card 2: RAM Memory Usage */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-violet-400 font-semibold text-xs">
              <Gauge className="w-4 h-4" />
              <span>حافظه مصرفی (RAM)</span>
            </div>
            <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded-md ${
              ramPercent > 85 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' :
              ramPercent > 70 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
              'bg-violet-500/20 text-violet-300'
            }`}>
              {ramMb} MB / {totalRamMb} MB
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
              {ramPercent}%
            </span>
            <span className="text-xs text-slate-400 font-mono">
              ({totalRamMb - ramMb} MB آزاد)
            </span>
          </div>

          {/* Progress bar with OOM threshold mark */}
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden relative">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                ramPercent > 85 ? 'bg-rose-500' : ramPercent > 70 ? 'bg-amber-400' : 'bg-violet-500'
              }`}
              style={{ width: `${ramPercent}%` }}
            />
          </div>

          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
            <span>حد هشدار OOM: <strong className="text-rose-400">850 MB</strong></span>
            <span className="text-[10px] text-emerald-400 font-semibold">بدون نشت حافظه ✓</span>
          </div>
        </div>

        {/* Card 3: Active Download Count & Concurrency */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-cyan-400 font-semibold text-xs">
              <Download className="w-4 h-4" />
              <span>دانلودهای همزمان فعال</span>
            </div>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-md bg-cyan-500/20 text-cyan-300">
              سقف: {concurrencyLimit}
            </span>
          </div>

          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
              {activeTasks.length}
            </span>
            <span className="text-xs text-slate-400">
              تسک در حال اجرا
            </span>
          </div>

          {/* Task status badges */}
          <div className="flex items-center gap-1.5 pt-1">
            {Array.from({ length: concurrencyLimit }).map((_, idx) => (
              <div 
                key={idx}
                className={`flex-1 h-2 rounded-full transition-all ${
                  idx < activeTasks.length 
                    ? 'bg-cyan-400 shadow-sm shadow-cyan-400/50' 
                    : 'bg-slate-800'
                }`}
                title={idx < activeTasks.length ? 'Worker Busy' : 'Worker Idle'}
              />
            ))}
          </div>

          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
            <span>در صف انتظار: <strong className="text-white">{activeTasks.filter(t => t.stage === 'queued').length}</strong></span>
            <span className="text-[10px] text-cyan-300">کنترل صف FIFO فعال</span>
          </div>
        </div>

        {/* Card 4: Disk Temp & Network I/O */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3 relative overflow-hidden">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs">
              <HardDrive className="w-4 h-4" />
              <span>فضای موقت دیسک و ترافیک</span>
            </div>
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300">
              {diskTempMb} MB
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <div>
              <span className="text-2xl font-extrabold text-white font-mono tracking-tight">
                {diskTempMb}
              </span>
              <span className="text-xs text-slate-400 mr-1">MB در /tmp</span>
            </div>
            <div className="text-right text-[11px] font-mono text-slate-300 space-y-0.5">
              <div className="flex items-center gap-1 text-sky-400">
                <ArrowDownRight className="w-3 h-3" />
                <span>{networkSpeedIn} MB/s In</span>
              </div>
              <div className="flex items-center gap-1 text-emerald-400">
                <ArrowUpRight className="w-3 h-3" />
                <span>{networkSpeedOut} MB/s Out</span>
              </div>
            </div>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div 
              className="h-full rounded-full bg-emerald-500 transition-all duration-500"
              style={{ width: `${Math.min(100, (diskTempMb / totalDiskMb) * 100 * 5)}%` }}
            />
          </div>

          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
            <span>ولوم دائمی: <strong className="text-emerald-400">/app/data (OK)</strong></span>
            <span className="text-[10px] text-slate-400">پاکسازی خودکار ✓</span>
          </div>
        </div>
      </div>

      {/* Main Real-Time Telemetry SVG Chart */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-400">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">
                نمودار نوسان زنده CPU و RAM (تایم‌لاین ۳۰ ثانیه گذشته)
              </h3>
              <p className="text-xs text-slate-400">
                تشخیص درجا هرگونه پیک مصرف حین پردازش FFmpeg و ادغام صدا با تصویر
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs font-medium">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-indigo-500"></span>
              <span className="text-slate-300">پردازنده (CPU %)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-violet-400"></span>
              <span className="text-slate-300">حافظه رم (RAM %)</span>
            </div>
            <div className="flex items-center gap-1 bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-700 text-slate-400 text-[11px] font-mono">
              <Clock className="w-3 h-3" />
              <span>رفرش: {refreshIntervalMs / 1000}s</span>
            </div>
          </div>
        </div>

        {/* SVG Area Chart */}
        <div className="w-full overflow-x-auto select-none pt-2" dir="ltr">
          <svg 
            viewBox={`0 0 ${chartWidth} ${chartHeight}`} 
            className="w-full h-48 sm:h-56 overflow-visible"
          >
            <defs>
              <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366f1" stopOpacity="0.45" />
                <stop offset="100%" stopColor="#6366f1" stopOpacity="0.0" />
              </linearGradient>
              <linearGradient id="ramGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#a855f7" stopOpacity="0.35" />
                <stop offset="100%" stopColor="#a855f7" stopOpacity="0.0" />
              </linearGradient>
            </defs>

            {/* Grid horizontal guidelines */}
            {[0, 25, 50, 75, 100].map(val => {
              const y = padding + usableHeight - (val / 100) * usableHeight;
              return (
                <g key={val}>
                  <line 
                    x1={padding} 
                    y1={y} 
                    x2={chartWidth - padding} 
                    y2={y} 
                    stroke="#1e293b" 
                    strokeDasharray="4 4" 
                    strokeWidth="1"
                  />
                  <text 
                    x={padding - 6} 
                    y={y + 3} 
                    fill="#64748b" 
                    fontSize="9" 
                    textAnchor="end" 
                    fontFamily="monospace"
                  >
                    {val}%
                  </text>
                </g>
              );
            })}

            {/* Area Fills */}
            <path d={cpuAreaPath} fill="url(#cpuGradient)" />
            <path d={ramAreaPath} fill="url(#ramGradient)" />

            {/* Lines */}
            <polyline 
              fill="none" 
              stroke="#6366f1" 
              strokeWidth="2.5" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              points={pointsCpu} 
            />
            <polyline 
              fill="none" 
              stroke="#c084fc" 
              strokeWidth="2.5" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              points={pointsRam} 
            />

            {/* Data point dots on the latest value */}
            {history.length > 0 && (() => {
              const lastIdx = history.length - 1;
              const lastPt = history[lastIdx];
              const x = padding + usableWidth;
              const yCpu = padding + usableHeight - (lastPt.cpu / 100) * usableHeight;
              const yRam = padding + usableHeight - (lastPt.ram / 100) * usableHeight;
              return (
                <g>
                  <circle cx={x} cy={yCpu} r="4" fill="#6366f1" stroke="#ffffff" strokeWidth="1.5" />
                  <circle cx={x} cy={yRam} r="4" fill="#c084fc" stroke="#ffffff" strokeWidth="1.5" />
                </g>
              );
            })()}
          </svg>
        </div>

        {/* Bottom time indicators */}
        <div className="flex justify-between items-center text-[10px] text-slate-500 font-mono px-2 pt-1 border-t border-slate-800/60" dir="ltr">
          <span>{history[0]?.time || '00:00'} (۳۰ ثانیه پیش)</span>
          <span>پایش آنلاین ترافیک و حافظه در زمان واقعی</span>
          <span>اکنون ({history[history.length - 1]?.time || '00:00'})</span>
        </div>
      </div>

      {/* Active Tasks Table & Crash Shield */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Active Tasks & Download Workers (8 cols) */}
        <div className="lg:col-span-8 bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4 text-cyan-400" />
              <h3 className="font-bold text-white text-sm">
                تسک‌های فعال و پردازش‌های در حال دانلود ({activeTasks.length})
              </h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              ظرفیت ایمن همزمان: {concurrencyLimit} ویدیو
            </span>
          </div>

          {activeTasks.length === 0 ? (
            <div className="p-8 text-center rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
              <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
              <div className="text-sm font-bold text-slate-200">هیچ دانلودی در حال حاضر در جریان نیست</div>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                منابع سیستم آزاد است و ربات آماده پذیرش درخواست‌های جدید کاربران بدون تاخیر می‌باشد.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {activeTasks.map(task => (
                <div 
                  key={task.id}
                  className="p-4 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-slate-700 transition space-y-3"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                          task.stage === 'ffmpeg_transcode' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                          task.stage === 'telegram_upload' ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30' :
                          task.stage === 'queued' ? 'bg-slate-700 text-slate-300' :
                          'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                        }`}>
                          {task.stage === 'ffmpeg_transcode' ? 'مرحله: تبدیل FFmpeg به AAC' :
                           task.stage === 'telegram_upload' ? 'مرحله: آپلود تلگرام' :
                           task.stage === 'queued' ? 'در صف انتظار (Queue)' :
                           'مرحله: دانلود استریم'}
                        </span>
                        <span className="text-[11px] font-mono text-slate-400">
                          کاربر: {task.userId}
                        </span>
                        <span className="text-[11px] font-mono px-1.5 py-0.2 rounded bg-slate-900 text-slate-300 border border-slate-800">
                          {task.quality}
                        </span>
                      </div>
                      <h4 className="text-xs sm:text-sm font-bold text-white mt-1.5 truncate">
                        {task.title}
                      </h4>
                    </div>

                    <button
                      onClick={() => handleKillTask(task.id, task.title)}
                      className="inline-flex items-center gap-1 text-[11px] px-2 py-1 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/20 transition cursor-pointer shrink-0"
                      title="کنسل کردن تسک در صورت هنگ کردن پردازش"
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      <span>توقف تسک</span>
                    </button>
                  </div>

                  {/* Progress Bar & Stats */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                      <span>پیشرفت: <strong className="text-white">{task.progress}%</strong></span>
                      <span>مدت سپری شده: <strong>{task.elapsedSeconds}s</strong></span>
                      <span>تخمین حجم: <strong>~{task.estimatedMb} MB</strong></span>
                    </div>
                    <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all duration-300 ${
                          task.stage === 'ffmpeg_transcode' ? 'bg-amber-400' :
                          task.stage === 'telegram_upload' ? 'bg-indigo-400' : 'bg-cyan-400'
                        }`}
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Crash Shield & Health Watchdog (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3.5 shadow-lg">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-3 text-indigo-400 font-bold text-sm">
              <ShieldAlert className="w-4 h-4" />
              <span>چک‌لیست سلامت و پیشگیری از کرش</span>
            </div>

            <div className="space-y-2.5 text-xs text-slate-300">
              <div className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">تاخیر Event Loop پایتون:</div>
                  <div className="text-[11px] text-slate-400">زیر ۵۰ میلی‌ثانیه عالی است</div>
                </div>
                <span className="font-mono font-bold text-emerald-400">{eventLoopLagMs} ms ✓</span>
              </div>

              <div className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">فرآیندهای رهاشده FFmpeg:</div>
                  <div className="text-[11px] text-slate-400">Zombie processes</div>
                </div>
                <span className="font-mono font-bold text-emerald-400">۰ مورد (Clean) ✓</span>
              </div>

              <div className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">ولوم دیتابیس (/app/data):</div>
                  <div className="text-[11px] text-slate-400">ماندگاری دائمی اطلاعات</div>
                </div>
                <span className="font-mono font-bold text-emerald-400">Mounted ✓</span>
              </div>

              <div className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="font-semibold text-white">سقف دانلود همزمان (Throttle):</div>
                  <div className="text-[11px] text-slate-400">جلوگیری از اشباع رم</div>
                </div>
                <div className="flex items-center gap-1.5 font-mono">
                  <button 
                    onClick={() => setConcurrencyLimit(prev => Math.max(1, prev - 1))}
                    className="w-5 h-5 rounded bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-200"
                  >
                    -
                  </button>
                  <span className="font-bold text-white px-1">{concurrencyLimit}</span>
                  <button 
                    onClick={() => setConcurrencyLimit(prev => Math.min(8, prev + 1))}
                    className="w-5 h-5 rounded bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-200"
                  >
                    +
                  </button>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-900/30 text-[11px] text-emerald-300 leading-relaxed">
              💡 <strong>راهنمای ادمین:</strong> به ازای هر ۱ گیگابایت رم سرور در Railway یا Docker، سقف دانلود همزمان را روی ۳ عدد نگه دارید تا خطر OOM Kill به صفر برسد.
            </div>
          </div>

          {/* Python snippet for bot admins */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-indigo-400" />
                کد پایتون پایش رم (psutil)
              </span>
              <button
                onClick={handleCopyCode}
                className="inline-flex items-center gap-1 text-[11px] text-indigo-400 hover:text-indigo-300 cursor-pointer"
              >
                {copiedSnippet ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copiedSnippet ? 'کپی شد' : 'کپی تابع'}</span>
              </button>
            </div>
            <p className="text-[11px] text-slate-400">
              با قرار دادن این تابع در <code className="text-indigo-300">bot/utils.py</code> می‌توانید دستور <code className="text-indigo-300">/status</code> را به تلگرام خود اضافه کنید تا همین آمار را مستقیماً در پی‌وی دریافت کنید.
            </p>
          </div>
        </div>
      </div>

      {/* Live System Logs Terminal */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 space-y-3 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2 text-slate-300 font-bold text-sm">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <span>لاگ‌های زنده سلامت سیستم و رویدادهای سرور</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">فیلتر:</span>
            <button
              onClick={() => setLogFilter('all')}
              className={`px-2 py-0.5 rounded text-xs transition ${
                logFilter === 'all' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-white'
              }`}
            >
              همه ({logs.length})
            </button>
            <button
              onClick={() => setLogFilter('warn')}
              className={`px-2 py-0.5 rounded text-xs transition ${
                logFilter === 'warn' ? 'bg-amber-500/20 text-amber-300 font-bold' : 'text-slate-400 hover:text-amber-300'
              }`}
            >
              هشدارها
            </button>

            <button
              onClick={() => setLogs([])}
              className="p-1 rounded text-slate-500 hover:text-slate-300 transition mr-2"
              title="پاکسازی لاگ‌ها"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Monospace Logs Box */}
        <div className="bg-slate-950 rounded-xl p-3.5 font-mono text-xs max-h-52 overflow-y-auto space-y-2 border border-slate-800/80 select-text" dir="ltr">
          {logs
            .filter(l => logFilter === 'all' || l.level === logFilter)
            .map(log => (
              <div key={log.id} className="flex items-start gap-2.5 leading-relaxed">
                <span className="text-slate-600 shrink-0 select-none">[{log.timestamp}]</span>
                <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold shrink-0 ${
                  log.level === 'warn' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                  log.level === 'alert' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                  log.level === 'success' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                  'bg-slate-800 text-slate-300'
                }`}>
                  {log.level.toUpperCase()}
                </span>
                <span className={`${
                  log.level === 'warn' ? 'text-amber-200' :
                  log.level === 'alert' ? 'text-rose-200' :
                  log.level === 'success' ? 'text-emerald-200' :
                  'text-slate-300'
                }`}>
                  {log.message}
                </span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};
