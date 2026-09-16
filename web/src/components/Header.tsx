import React from 'react';
import { Download, Github, CheckCircle2, Bot, Sparkles, ExternalLink, Activity } from 'lucide-react';
import { downloadFixedProjectZip } from '../utils/zipExport';

export type TabType = 'issues' | 'simulator' | 'dashboard' | 'code' | 'guide';

interface HeaderProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab }) => {
  const [downloading, setDownloading] = React.useState(false);

  const handleDownloadZip = async () => {
    try {
      setDownloading(true);
      await downloadFixedProjectZip();
    } finally {
      setDownloading(false);
    }
  };

  return (
    <header className="border-b border-slate-800/80 bg-slate-900/90 backdrop-blur sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Logo & Title */}
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-sky-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 ring-1 ring-white/10">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg sm:text-xl font-bold text-white tracking-tight">
                  پچ و عیب‌یابی ربات تلگرام یوتیوب
                </h1>
                <span className="hidden sm:inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  ۵ مورد اصلاح شد
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono flex items-center gap-1.5 mt-0.5">
                <span>kamyartel85-spec/telegram-youtube-downloader</span>
              </p>
            </div>
          </div>

          {/* Right actions */}
          <div className="flex items-center gap-2.5 sm:gap-3">
            <a
              href="https://github.com/kamyartel85-spec/telegram-youtube-downloader"
              target="_blank"
              rel="noreferrer"
              className="hidden md:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg text-slate-300 bg-slate-800 hover:bg-slate-700/80 border border-slate-700 transition"
              title="مشاهده صفحه گیت‌هاب"
            >
              <Github className="w-4 h-4" />
              <span>مخزن گیت‌هاب</span>
              <ExternalLink className="w-3 h-3 text-slate-400" />
            </a>

            <button
              onClick={handleDownloadZip}
              disabled={downloading}
              className="inline-flex items-center gap-2 px-3.5 sm:px-4 py-2 text-xs sm:text-sm font-semibold rounded-xl text-white bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 shadow-md shadow-indigo-600/25 transition cursor-pointer disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              <span>{downloading ? 'در حال ایجاد زیپ...' : 'دانلود کل پروژه اصلاح‌شده (ZIP)'}</span>
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 -mb-px overflow-x-auto no-scrollbar pt-1 pb-2">
          <button
            onClick={() => setActiveTab('issues')}
            className={`flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg transition whitespace-nowrap ${
              activeTab === 'issues'
                ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Sparkles className="w-4 h-4" />
            <span>تحلیل و پچ ۵ مشکل اصلی</span>
            <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-300 text-[11px] flex items-center justify-center font-mono">
              5
            </span>
          </button>

          <button
            onClick={() => setActiveTab('simulator')}
            className={`flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg transition whitespace-nowrap ${
              activeTab === 'simulator'
                ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>شبیه‌ساز و تست زنده تلگرام</span>
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/20">
              تست فوری
            </span>
          </button>

          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg transition whitespace-nowrap ${
              activeTab === 'dashboard'
                ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Activity className="w-4 h-4" />
            <span>داشبورد زنده سیستم (CPU/RAM)</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          </button>

          <button
            onClick={() => setActiveTab('code')}
            className={`flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg transition whitespace-nowrap ${
              activeTab === 'code'
                ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Github className="w-4 h-4" />
            <span>مشاهده سورس‌کد و کپی فایل‌ها</span>
          </button>

          <button
            onClick={() => setActiveTab('guide')}
            className={`flex items-center gap-2 px-4 py-2 text-xs sm:text-sm font-semibold rounded-lg transition whitespace-nowrap ${
              activeTab === 'guide'
                ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>راهنمای استقرار در Railway و گیت‌هاب</span>
          </button>
        </nav>
      </div>
    </header>
  );
};
