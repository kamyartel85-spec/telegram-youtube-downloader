import JSZip from 'jszip';
import { BOT_FILES } from '../data/botFilesData';

export async function downloadFixedProjectZip() {
  const zip = new JSZip();

  // Add all files from BOT_FILES
  for (const [filename, fileObj] of Object.entries(BOT_FILES)) {
    zip.file(filename, fileObj.content);
  }

  // Add a handy README with the 5 fixes summary
  const patchReadme = `# پچ اختصاصی ربات تلگرام دانلود از یوتیوب
مخزن: https://github.com/kamyartel85-spec/telegram-youtube-downloader

## خلاصه‌ی ۵ اصلاحات انجام شده:
1. رفع خطای کیفیت‌های ۱۴۴p، ۲۴۰p و ۳۶۰p در youtube.py و FFmpeg
2. حل ریست شدن اطلاعات و زبان کاربران با انتقال دیتابیس به مسیر پایدار data/bot.db و افزودن ولوم در Dockerfile
3. بهینه‌سازی کش تلگرام با ذخیره شناسه معتبر telethon_utils.pack_bot_file_id و پاکسازی ۱۰۰٪ تامبنیل‌های موقت در utils.py
4. فارسی‌سازی کامل متون اطلاعات ویدیو در i18n.py (عنوان، مدت زمان، کانال، بازدید، نظرات، تاریخ انتشار)
5. ارسال صداها با supports_streaming=True و DocumentAttributeAudio(voice=False) با کاور و تگ‌های ID3 جهت پخش آنلاین قبل از دانلود کامل

## نحوه استفاده:
فایل‌های این پوشه را جایگزین فایل‌های قبلی پروژه خود کنید و با دستورات زیر روی گیت‌پوش نمایید:
git add .
git commit -m "fix: resolve 144p/240p/360p errors, persistent db, audio streaming, and persian i18n"
git push origin main
`;
  zip.file('PATCH_NOTES_FA.md', patchReadme);

  const content = await zip.generateAsync({ type: 'blob' });
  const url = URL.createObjectURL(content);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'telegram-youtube-downloader-fixed.zip';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function downloadSingleFile(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
