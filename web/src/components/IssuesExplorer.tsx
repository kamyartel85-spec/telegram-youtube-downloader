import React, { useState } from 'react';
import { ISSUES_DATA, IssueDetail } from '../data/issuesData';
import { 
  AlertCircle, 
  CheckCircle2, 
  Code2, 
  Copy, 
  Check, 
  Database, 
  Download, 
  HardDrive, 
  Languages, 
  Music, 
  ArrowRight,
  Sparkles,
  HelpCircle
} from 'lucide-react';

export const IssuesExplorer: React.FC = () => {
  const [selectedIssueId, setSelectedIssueId] = useState<string>(ISSUES_DATA[0].id);
  const [copiedFile, setCopiedFile] = useState<string | null>(null);

  const currentIssue = ISSUES_DATA.find(i => i.id === selectedIssueId) || ISSUES_DATA[0];

  const handleCopy = (code: string, label: string) => {
    navigator.clipboard.writeText(code);
    setCopiedFile(label);
    setTimeout(() => setCopiedFile(null), 2000);
  };

  const getCategoryIcon = (category: IssueDetail['category']) => {
    switch (category) {
      case 'download':
        return <Download className="w-5 h-5 text-rose-400" />;
      case 'database':
        return <Database className="w-5 h-5 text-amber-400" />;
      case 'cache':
        return <HardDrive className="w-5 h-5 text-cyan-400" />;
      case 'i18n':
        return <Languages className="w-5 h-5 text-emerald-400" />;
      case 'audio':
        return <Music className="w-5 h-5 text-violet-400" />;
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 sm:gap-4">
        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>کیفیت‌های ۱۴۴ و ۲۴۰ و ۳۶۰</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl font-bold text-white font-mono">100% OK</div>
          <div className="text-[11px] text-emerald-400/90 mt-1">تست و رفع قطعی خطا</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>ماندگاری دیتابیس</span>
            <Database className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-xl font-bold text-white font-mono">پایدار (Persistent)</div>
          <div className="text-[11px] text-amber-400/90 mt-1">بدون ریست اطلاعات و زبان</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>حجم کش و دیسک</span>
            <HardDrive className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-xl font-bold text-white font-mono">۰ مگابایت</div>
          <div className="text-[11px] text-cyan-400/90 mt-1">فوروارد فوری تلگرام</div>
        </div>

        <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>اطلاعات ویدیو</span>
            <Languages className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl font-bold text-white">کاملاً فارسی</div>
          <div className="text-[11px] text-emerald-400/90 mt-1">عناوین، بازدید و زمان</div>
        </div>

        <div className="col-span-2 md:col-span-1 p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 text-xs mb-2">
            <span>پلیر موزیک تلگرام</span>
            <Music className="w-4 h-4 text-violet-400" />
          </div>
          <div className="text-xl font-bold text-white">پخش استریم</div>
          <div className="text-[11px] text-violet-400/90 mt-1">گوش دادن قبل از دانلود</div>
        </div>
      </div>

      {/* Main Container: Left navigation / Right issue details */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Issue Selector Menu (5 items) */}
        <div className="lg:col-span-4 space-y-2.5">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-1">
            ۵ مسئله‌ی مطرح‌شده توسط شما
          </div>

          {ISSUES_DATA.map(issue => {
            const isSelected = issue.id === selectedIssueId;
            return (
              <button
                key={issue.id}
                onClick={() => setSelectedIssueId(issue.id)}
                className={`w-full text-right p-4 rounded-2xl border transition text-sm flex items-start gap-3.5 cursor-pointer ${
                  isSelected
                    ? 'bg-slate-800/90 border-indigo-500/50 shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500/30'
                    : 'bg-slate-900/50 border-slate-800/80 hover:bg-slate-800/50 hover:border-slate-700'
                }`}
              >
                <div className="mt-0.5 p-2 rounded-xl bg-slate-800 border border-slate-700/60 shrink-0">
                  {getCategoryIcon(issue.category)}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold text-white text-xs sm:text-sm truncate">
                      {issue.number}. {issue.title}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 line-clamp-2 mt-1 leading-relaxed">
                    {issue.shortDesc}
                  </p>
                  <div className="flex items-center gap-2 mt-2.5">
                    {issue.affectedFiles.map(file => (
                      <span
                        key={file}
                        className="font-mono text-[10px] px-2 py-0.5 rounded-md bg-slate-950 text-slate-300 border border-slate-800"
                      >
                        {file}
                      </span>
                    ))}
                    <span className="text-[10px] text-emerald-400 font-medium mr-auto">
                      حل شده ✓
                    </span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Detailed Issue Card & Code Diff */}
        <div className="lg:col-span-8 bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-7 space-y-6">
          {/* Header */}
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-5">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-400">
                {getCategoryIcon(currentIssue.category)}
              </div>
              <div>
                <span className="text-xs text-indigo-400 font-semibold font-mono">
                  مسئله شماره {currentIssue.number} از ۵
                </span>
                <h2 className="text-lg sm:text-xl font-bold text-white mt-0.5">
                  {currentIssue.title}
                </h2>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                پچ در مخزن اعمال شد
              </span>
            </div>
          </div>

          {/* Root cause analysis */}
          <div className="space-y-4">
            <div className="bg-rose-500/5 border border-rose-500/20 rounded-xl p-4 sm:p-5">
              <div className="flex items-center gap-2 text-rose-400 font-bold text-sm mb-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>ریشه اصلی مشکل در کد قبلی چیست؟</span>
              </div>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed whitespace-pre-line">
                {currentIssue.rootCause}
              </p>
            </div>

            {/* Why other bots worked */}
            <div className="bg-indigo-950/30 border border-indigo-800/30 rounded-xl p-4 sm:p-5">
              <div className="flex items-center gap-2 text-indigo-300 font-bold text-sm mb-2">
                <HelpCircle className="w-4 h-4 shrink-0" />
                <span>چرا بات‌های دیگر با همین لینک بدون خطا دانلود می‌کردند؟</span>
              </div>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                {currentIssue.whyOtherBotsWorked}
              </p>
            </div>

            {/* Solution Summary */}
            <div className="bg-emerald-950/20 border border-emerald-800/30 rounded-xl p-4 sm:p-5">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm mb-2">
                <Sparkles className="w-4 h-4 shrink-0" />
                <span>راهکار اعمال‌شده و نحوه عملکرد نسخه اصلاح‌شده:</span>
              </div>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                {currentIssue.solutionExplanation}
              </p>
            </div>
          </div>

          {/* Code Comparison (Before vs After) */}
          <div className="space-y-4 pt-2">
            <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Code2 className="w-4 h-4 text-indigo-400" />
              <span>مقایسه کد: قبل از پچ در برابر بعد از پچ</span>
            </h3>

            {/* Before Code (Buggy) */}
            <div className="border border-rose-900/40 rounded-xl overflow-hidden bg-slate-950">
              <div className="flex items-center justify-between bg-rose-950/40 px-4 py-2 border-b border-rose-900/40 text-xs">
                <span className="text-rose-300 font-medium flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                  کد قبلی (دارای باگ): {currentIssue.beforeCode.file}
                </span>
                <span className="text-slate-400 text-[11px]">
                  {currentIssue.beforeCode.description}
                </span>
              </div>
              <pre dir="ltr" className="p-4 text-xs font-mono text-rose-300/80 overflow-x-auto leading-relaxed">
                <code>{currentIssue.beforeCode.code}</code>
              </pre>
            </div>

            {/* After Code (Fixed) */}
            <div className="border border-emerald-900/50 rounded-xl overflow-hidden bg-slate-950 shadow-lg shadow-emerald-950/20">
              <div className="flex items-center justify-between bg-emerald-950/40 px-4 py-2 border-b border-emerald-900/50 text-xs">
                <span className="text-emerald-300 font-medium flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  کد جدید و اصلاح‌شده (Fixed): {currentIssue.afterCode.file}
                </span>
                <button
                  onClick={() => handleCopy(currentIssue.afterCode.code, 'after-' + currentIssue.id)}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-emerald-900/60 hover:bg-emerald-800/80 text-emerald-200 text-xs transition cursor-pointer"
                >
                  {copiedFile === 'after-' + currentIssue.id ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-300" />
                      <span>کپی شد!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>کپی کد اصلاح‌شده</span>
                    </>
                  )}
                </button>
              </div>
              <pre dir="ltr" className="p-4 text-xs font-mono text-emerald-300 overflow-x-auto leading-relaxed">
                <code>{currentIssue.afterCode.code}</code>
              </pre>
            </div>
          </div>

          {/* Key Takeaway */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-300 flex items-start gap-2.5">
            <span className="font-bold text-amber-400 shrink-0">💡 نکته کلیدی:</span>
            <span>{currentIssue.keyTakeaway}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
