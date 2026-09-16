import React, { useState } from 'react';
import { BOT_FILES, BotFile } from '../data/botFilesData';
import { downloadSingleFile, downloadFixedProjectZip } from '../utils/zipExport';
import { 
  FileCode, 
  Copy, 
  Check, 
  Download, 
  Search, 
  CheckCircle2, 
  Sparkles,
  ExternalLink,
  FileText
} from 'lucide-react';

export const FilesViewer: React.FC = () => {
  const fileKeys = Object.keys(BOT_FILES);
  const [selectedFileKey, setSelectedFileKey] = useState<string>('youtube.py');
  const [copied, setCopied] = useState(false);
  const [searchFilter, setSearchFilter] = useState('');

  const currentFile: BotFile = BOT_FILES[selectedFileKey] || BOT_FILES['youtube.py'];

  const handleCopy = () => {
    navigator.clipboard.writeText(currentFile.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const filteredKeys = fileKeys.filter(k => 
    k.toLowerCase().includes(searchFilter.toLowerCase()) || 
    BOT_FILES[k].summary.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-12">
      {/* Top Banner */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <FileCode className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base sm:text-lg font-bold text-white">
              مشاهده فایل‌های سورس‌کد اصلاح‌شده ربات
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            تمامی فایل‌های اصلاح‌شده برای اعمال در گیت‌هاب شما (<code className="text-indigo-300">kamyartel85-spec/telegram-youtube-downloader</code>) در این بخش قرار دارند. می‌توانید تک‌تک فایل‌ها را کپی کنید یا فایل زیپ کامل را دانلود نمایید.
          </p>
        </div>

        <button
          onClick={() => downloadFixedProjectZip()}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs sm:text-sm font-semibold transition cursor-pointer shadow-md shadow-indigo-600/20 shrink-0"
        >
          <Download className="w-4 h-4" />
          <span>دانلود همه فایل‌ها در یک ZIP</span>
        </button>
      </div>

      {/* Main Files Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left File List */}
        <div className="lg:col-span-4 space-y-3">
          {/* Search box */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute right-3.5 top-3" />
            <input
              type="text"
              placeholder="جستجو در نام یا توضیح فایل..."
              value={searchFilter}
              onChange={e => setSearchFilter(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-xl pr-10 pl-4 py-2.5 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition"
            />
          </div>

          <div className="space-y-1.5 max-h-[600px] overflow-y-auto pr-1">
            {filteredKeys.map(key => {
              const file = BOT_FILES[key];
              const isSelected = key === selectedFileKey;
              return (
                <button
                  key={key}
                  onClick={() => setSelectedFileKey(key)}
                  className={`w-full text-right p-3 rounded-xl border transition text-xs flex items-start gap-3 cursor-pointer ${
                    isSelected
                      ? 'bg-slate-800 border-indigo-500 text-white shadow-md'
                      : 'bg-slate-900/60 border-slate-800/80 text-slate-300 hover:bg-slate-800/50 hover:text-white'
                  }`}
                >
                  <FileText className={`w-4 h-4 mt-0.5 shrink-0 ${file.isModified ? 'text-emerald-400' : 'text-slate-500'}`} />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-1">
                      <span className="font-mono font-bold truncate">{file.name}</span>
                      {file.isModified && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/25 shrink-0">
                          اصلاح شده ✓
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-slate-400 truncate mt-1">
                      {file.summary}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Code Viewer */}
        <div className="lg:col-span-8 bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden flex flex-col shadow-xl">
          {/* Viewer Toolbar */}
          <div className="bg-slate-800/80 px-4 sm:px-5 py-3 border-b border-slate-700/80 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <FileCode className="w-5 h-5 text-indigo-400" />
              <div>
                <span className="font-mono font-bold text-sm text-white">{currentFile.name}</span>
                <span className="text-slate-400 text-xs mr-2 font-mono">({currentFile.content.split('\n').length} خط)</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-xs transition cursor-pointer"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span>کپی شد!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>کپی محتوا</span>
                  </>
                )}
              </button>

              <button
                onClick={() => downloadSingleFile(currentFile.name, currentFile.content)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs transition cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" />
                <span>دانلود فایل</span>
              </button>
            </div>
          </div>

          {/* Code Content with Line Numbers */}
          <div className="overflow-x-auto max-h-[640px] bg-slate-950 p-4 font-mono text-xs text-slate-300 leading-relaxed select-text" dir="ltr">
            <pre className="table">
              {currentFile.content.split('\n').map((line, idx) => (
                <div key={idx} className="table-row hover:bg-slate-800/40">
                  <span className="table-cell select-none pr-4 text-slate-600 text-right w-10 text-[11px]">
                    {idx + 1}
                  </span>
                  <span className="table-cell whitespace-pre">
                    {line || ' '}
                  </span>
                </div>
              ))}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
