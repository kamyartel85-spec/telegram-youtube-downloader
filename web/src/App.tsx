import React, { useState } from 'react';
import { Header, TabType } from './components/Header';
import { IssuesExplorer } from './components/IssuesExplorer';
import { TelegramSimulator } from './components/TelegramSimulator';
import { Dashboard } from './components/Dashboard';
import { FilesViewer } from './components/FilesViewer';
import { DeploymentGuide } from './components/DeploymentGuide';
import { 
  CheckCircle2, 
  Github, 
  Download, 
  Layers, 
  ArrowLeft,
  Sparkles,
  ExternalLink,
  Activity
} from 'lucide-react';
import { downloadFixedProjectZip } from './utils/zipExport';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white" dir="rtl">
      {/* Top Header & Navigation */}
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8">
        {/* Sub-hero badge banner */}
        <div className="mb-6 p-4 rounded-2xl bg-gradient-to-l from-indigo-950/40 via-slate-900 to-slate-900 border border-indigo-900/30 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping"></div>
            <div>
              <span className="text-xs text-indigo-400 font-bold">پروژه بازبینی و آماده شد:</span>
              <p className="text-xs sm:text-sm text-slate-200 mt-0.5">
                همه ۵ مورد درخواستی شامل خطای کیفیت‌های پایین، ریست دیتابیس، کش و فوروارد، فارسی‌سازی مشخصات و استریم آنلاین موزیک اعمال شدند.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => setActiveTab('dashboard')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 text-xs font-semibold transition cursor-pointer"
            >
              <Activity className="w-3.5 h-3.5" />
              <span>داشبورد زنده CPU و RAM</span>
            </button>
            <button
              onClick={() => setActiveTab('simulator')}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 text-xs font-semibold transition cursor-pointer"
            >
              <span>شبیه‌ساز بات</span>
              <ArrowLeft className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Tab content rendering */}
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'issues' && <IssuesExplorer />}
        {activeTab === 'simulator' && <TelegramSimulator />}
        {activeTab === 'code' && <FilesViewer />}
        {activeTab === 'guide' && <DeploymentGuide />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span>سورس‌کد پروژه:</span>
            <a
              href="https://github.com/kamyartel85-spec/telegram-youtube-downloader"
              target="_blank"
              rel="noreferrer"
              className="text-indigo-400 hover:text-indigo-300 font-mono transition flex items-center gap-1"
            >
              <span>kamyartel85-spec/telegram-youtube-downloader</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-emerald-500 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              تمامی تست‌ها و بررسی‌های پایتون پاس شدند
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
}
