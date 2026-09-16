import React, { useState } from 'react';
import { 
  GitBranch, 
  HardDrive, 
  Terminal, 
  CheckCircle2, 
  Copy, 
  Check, 
  Server, 
  Layers, 
  ExternalLink,
  ShieldCheck,
  Zap
} from 'lucide-react';

export const DeploymentGuide: React.FC = () => {
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(id);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  const gitCommands = `# ۱. کلون کردن یا باز کردن پوشه پروژه محلی
cd telegram-youtube-downloader

# ۲. استخراج فایل‌های دانلودی پچ‌شده (یا جایگزین کردن فایل‌های اصلاح شده)
# ۳. بررسی وضعیت تغییرات فایل‌ها
git status

# ۴. ثبت و ذخیره تغییرات ۵ پچ در گیت
git add .
git commit -m "fix: 144p/240p/360p errors, persistent db volume, instant cache forwarding, and persian metadata"

# ۵. ارسال به مخزن گیت‌هاب
git push origin main`;

  const railwayVolumeConfig = `# تنظیم ماندگاری دیتابیس در Railway:
# ۱. وارد پنل Railway شوید و روی پروژه و سرویس بات خود کلیک کنید.
# ۲. به زبانه Data یا Volumes بروید (در بخش تنظیمات سرویس).
# ۳. روی Add Volume یا New Volume کلیک کنید.
# ۴. مقدار Mount Path را دقیقا این مقدار قرار دهید:
/app/data

# با این کار فایل دیتابیس bot.db برای همیشه ماندگار می‌شود و با هر دیپلوی صفر نمی‌شود!`;

  const dockerCompose = `version: "3.8"

services:
  telegram-bot:
    build: .
    restart: always
    environment:
      - BOT_TOKEN=your_bot_token_here
      - API_ID=your_api_id
      - API_HASH=your_api_hash
      - OWNER_ID=your_telegram_id
      - DB_PATH=/app/data/bot.db
    volumes:
      # ذخیره دائمی دیتابیس روی هاست
      - ./bot_data:/app/data
`;

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      {/* Step 1: Git Push */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-7 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/15 text-indigo-400 border border-indigo-500/30">
              <GitBranch className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base sm:text-lg">
                گام اول: اعمال تغییرات روی مخزن گیت‌هاب شما
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                https://github.com/kamyartel85-spec/telegram-youtube-downloader
              </p>
            </div>
          </div>

          <button
            onClick={() => handleCopy(gitCommands, 'git')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs transition cursor-pointer"
          >
            {copiedSection === 'git' ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span>کپی شد</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>کپی دستورات</span>
              </>
            )}
          </button>
        </div>

        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          ساده‌ترین روش این است که دکمه <strong className="text-white">دانلود کل پروژه اصلاح‌شده (ZIP)</strong> در بالای صفحه را بزنید، فایل‌ها را داخل پوشه پروژه خود اکسترکت کنید و سپس دستورات زیر را در ترمینال اجرا کنید:
        </p>

        <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 font-mono text-xs text-indigo-300 overflow-x-auto" dir="ltr">
          <pre>{gitCommands}</pre>
        </div>
      </div>

      {/* Step 2: Persistent Volume (Railway / Server) */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-7 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/15 text-amber-400 border border-amber-500/30">
              <HardDrive className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base sm:text-lg">
                گام دوم: حل دائمی ریست شدن دیتابیس در سرور ابری (Railway / Docker)
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                جلوگیری از پاک شدن زبان کاربر، آمار و سهمیه‌های دانلود با هر ری‌استارت
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
          {/* Railway instructions */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-amber-300 font-bold text-xs sm:text-sm">
              <Server className="w-4 h-4" />
              <span>تنظیم ولوم در ریل‌وی (Railway Volume)</span>
            </div>
            <ol className="text-xs text-slate-300 space-y-2 list-decimal list-inside leading-relaxed">
              <li>وارد داشبورد پروژه خود در Railway شوید.</li>
              <li>روی سرویس بات تلگرام کلیک کرده و گزینه <span className="text-white font-mono">Volumes</span> را انتخاب کنید.</li>
              <li>روی دکمه <span className="text-white font-mono">Add Volume</span> کلیک کنید.</li>
              <li>در کادر <span className="text-amber-300 font-mono">Mount Path</span>، دقیقا آدرس زیر را تایپ کنید:</li>
            </ol>
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-700 font-mono text-xs text-emerald-400 text-center select-all" dir="ltr">
              /app/data
            </div>
            <p className="text-[11px] text-slate-400">
              دیتابیس شما اکنون در این ولوم ذخیره شده و حتی اگر هزاران بار کد جدید پوش کنید، اطلاعات کاربران پاک نمی‌شود.
            </p>
          </div>

          {/* Docker Compose */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-sky-300 font-bold text-xs sm:text-sm">
              <Layers className="w-4 h-4" />
              <span>استفاده با Docker Compose (سرور مجازی یا VPS)</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              اگر از سرور شخصی یا VPS استفاده می‌کنید، نمونه فایل <code className="text-indigo-300">docker-compose.yml</code> زیر به طور خودکار ولوم محلی ایجاد می‌کند:
            </p>
            <div className="bg-slate-900 p-2.5 rounded-lg border border-slate-800 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-36" dir="ltr">
              <pre>{dockerCompose}</pre>
            </div>
          </div>
        </div>
      </div>

      {/* Step 3: Setting Up Log Channel for 0-Byte Cache & Forwarding */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 sm:p-7 space-y-4">
        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <div className="p-2.5 rounded-xl bg-cyan-500/15 text-cyan-400 border border-cyan-500/30">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base sm:text-lg">
              گام سوم: راه‌اندازی کانال لاگ و فوروارد خودکار (مصرف ترافیک ۰ مگابایت)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              آرشیو فایل‌ها در یک کانال خصوصی تلگرام جهت ارسال بدون دانلود مجدد
            </p>
          </div>
        </div>

        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
          ربات شما دارای قابلیتی است به نام <strong className="text-cyan-300">download_log_channel_id</strong>. وقتی این کانال را ست کنید:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1.5">
            <div className="text-cyan-400 font-bold text-xs">۱. ساخت کانال خصوصی</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              یک کانال تلگرام خصوصی به نام مثلاً <span className="text-slate-200">YouTube Downloads Archive</span> بسازید و بات را ادمین با دسترسی ارسال پیام کنید.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1.5">
            <div className="text-cyan-400 font-bold text-xs">۲. دریافت آیدی کانال</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              یک پیام از کانال به بات‌هایی مانند <span className="text-slate-200">@userinfobot</span> فوروارد کنید تا شناسه عددی منفی (مثل <code className="text-slate-300">-100123456789</code>) را به شما بدهد.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1.5">
            <div className="text-cyan-400 font-bold text-xs">۳. تنظیم در پنل ادمین</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              در بات خود دستور <code className="text-slate-200">/admin</code> را بزنید، به بخش تنظیمات کانال لاگ بروید و این شناسه را ست کنید.
            </p>
          </div>
        </div>

        <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-900/30 text-xs text-cyan-200">
          ✓ از این پس هر فایلی که یک کاربر دانلود کند، یک نسخه در این کانال ذخیره می‌شود و برای کاربر بعدی بدون ۱ مگابایت دانلود از سرور، با فوروارد آنی ارسال خواهد شد!
        </div>
      </div>
    </div>
  );
};
