export interface IssueDetail {
  id: string;
  number: number;
  title: string;
  shortDesc: string;
  category: 'download' | 'database' | 'cache' | 'i18n' | 'audio';
  severity: 'critical' | 'high' | 'medium';
  affectedFiles: string[];
  rootCause: string;
  whyOtherBotsWorked: string;
  solutionExplanation: string;
  beforeCode: {
    file: string;
    code: string;
    description: string;
  };
  afterCode: {
    file: string;
    code: string;
    description: string;
  };
  keyTakeaway: string;
}

export const ISSUES_DATA: IssueDetail[] = [
  {
    id: 'quality-144-240-360-error',
    number: 1,
    title: 'عدم دانلود کیفیت‌های ۱۴۴p، ۲۴۰p و ۳۶۰p و بروز خطا',
    shortDesc: 'ربات در کیفیت‌های پایین خطا می‌داد ولی بات‌های دیگر همان ویدیو را بدون مشکل دانلود می‌کردند.',
    category: 'download',
    severity: 'critical',
    affectedFiles: ['youtube.py', 'Dockerfile'],
    rootCause: `۱. یوتیوب در کیفیت‌های پایین (به ویژه ۱۴۴p و ۲۴۰p) استریم ویدیو را صرفاً با کدک‌های VP9 یا AV01 ارائه می‌دهد و دیگر کدک AVC1 (H.264) جداگانه برای آن‌ها ارائه نمی‌کند. در کد قبلی نوشته شده بود vcodec^=avc1 که باعث پیدا نشدن فرمت می‌شد.
۲. صدای پیش‌فرض یوتیوب با کدک Opus است. وقتی yt-dlp سعی می‌کرد ویدیو و صدای Opus را با merge_output_format="mp4" ادغام کند، کانتینر استاندارد MP4 در FFmpeg به دلیل ناسازگاری کدک Opus خطای "Could not find tag for codec opus" می‌داد و کرش می‌کرد.
۳. در کیفیت ۳۶۰p، یوتیوب فرمت شماره ۱۸ را دارد که تصویر و صدا از قبل با کدک سازگار H.264 + AAC ادغام شده‌اند، ولی الگوی جستجوی قبلی استریم‌های جداگانه با کدک نایاب avc1 را ترجیح می‌داد.
۴. استفاده از player_client حاوی android به همراه هدر مرورگر ویندوز باعث می‌شد یوتیوب خطای ۴۰۳ یا کاهش شدید سرعت (Throttling) ایجاد کند.`,
    whyOtherBotsWorked: 'بات‌های موفق از فرمت ترکیبی best[height<=q][ext=mp4] استفاده می‌کنند که برای ۳۶۰p مستقیماً فرمت ۱۸ (تک استریم بدون نیاز به مرج) را دانلود می‌کند و برای ۱۴۴p/۲۴۰p در صورت وجود صدای Opus، آرگومان -c:a aac را در FFmpeg قرار می‌دهند تا صدا به AAC تبدیل و بدون هیچ خطایی داخل MP4 قرار گیرد.',
    solutionExplanation: 'الگوی انتخاب فرمت اصلاح شد تا ابتدا فرمت‌های آماده MP4 بررسی شوند، سپس استریم‌های مجزا با تبدیل خودکار صدا به AAC از طریق فلگ‌های FFmpeg (-c:a aac -movflags +faststart) پردازش شوند. همچنین کلاینت‌های یوتیوب به کلاینت‌های مطمئن با هدر معتبر ارتقا یافتند.',
    beforeCode: {
      file: 'youtube.py',
      description: 'کد قبلی که فقط به دنبال avc1 می‌گشت و صدای Opus را بدون تبدیل به MP4 می‌فرستاد:',
      code: `# فرمت قبلی که در ۱۴۴p و ۲۴۰p شکست می‌خورد:
fmt = (
    f"bestvideo[height={q}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/"
    f"bestvideo[height={q}]+bestaudio/"
    f"bestvideo[height<={q}][vcodec^=avc1]+bestaudio[acodec^=mp4a]/"
    f"bestvideo[height<={q}]+bestaudio/"
    f"best[height<={q}][ext=mp4]/"
    f"best[height<={q}]/"
    f"worstvideo[height>={q}]+bestaudio/"
    f"bestvideo[height<={q}]+bestaudio"
)
postprocessor_args={
    "ffmpeg": ["-movflags", "+faststart"],
}`
    },
    afterCode: {
      file: 'youtube.py',
      description: 'کد اصلاح‌شده که تمام کیفیت‌ها را با موفقیت و تبدیل خودکار به فرمت سازگار تلگرام دانلود می‌کند:',
      code: `# الگوی جدید و منعطف بدون خطا:
fmt = (
    f"best[height<={q}][ext=mp4]/"
    f"bestvideo[height<={q}][ext=mp4]+bestaudio[ext=m4a]/"
    f"bestvideo[height<={q}]+bestaudio[ext=m4a]/"
    f"bestvideo[height<={q}]+bestaudio/"
    f"best[height<={q}]/"
    f"best"
)
opts = dict(
    _BASE_OPTS,
    format=fmt,
    merge_output_format="mp4",
    outtmpl=outtmpl,
    postprocessor_args={
        "ffmpeg": [
            "-c:a", "aac",             # تضمین تبدیل صدا به AAC سازگار با تلگرام
            "-b:a", "192k",
            "-movflags", "+faststart",  # فعال‌سازی استریم فوری هنگام دانلود
        ],
    },
)`
    },
    keyTakeaway: 'همیشه در یوتیوب کیفیت ۳۶۰p را اولویت اول با فرمت ۱۸ بگذارید و برای سایر کیفیت‌ها اجازه دهید FFmpeg صدای Opus را به AAC تبدیل کند تا فایل نهایی MP4 در همه دستگاه‌ها بدون خطا پخش شود.'
  },
  {
    id: 'data-reset-on-redeploy',
    number: 2,
    title: 'ریست شدن اطلاعات کاربران، سهمیه دانلود، زبان و آمار با هر تغییر',
    shortDesc: 'با هر بار آپدیت یا ریستارت سرور، کاربر دوباره باید زبان انتخاب می‌کرد و آمار و سهمیه‌ها صفر می‌شدند.',
    category: 'database',
    severity: 'critical',
    affectedFiles: ['config.py', 'Dockerfile', 'railway.json'],
    rootCause: `در فایل config.py مسیر دیتابیس به این شکل تعریف شده بود:
DB_PATH = os.environ.get("DB_PATH", "/tmp/ytdl_bot/bot.db")
در لینوکس و به ویژه محیط‌های ابری مانند Railway، Render، Koyeb و Docker:
پوشه /tmp/ موقتی (Ephemeral) است. هر بار که شما کدی را در گیت پوش می‌کنید، سرور کانتینر قبلی را حذف و یک کانتینر جدید از روی ایمیج می‌سازد. به همین دلیل تمام فایل‌های داخل /tmp پاک می‌شدند و دیتابیس نو ساخته می‌شد.`,
    whyOtherBotsWorked: 'بات‌های تجاری از یک ولوم دائمی (Persistent Volume) یا دیتابیس خارجی (Postgres / MySQL) استفاده می‌کنند، یا مسیر دیتابیس SQLite را در یک پوشه متصل به ولوم (مانند /app/data) قرار می‌دهند.',
    solutionExplanation: 'مسیر دیتابیس به ./data/bot.db تغییر یافت و در Dockerfile دستور VOLUME ["/app/data"] قرار داده شد. در Railway با یک کلیک کافیست یک Volume با مسیر /app/data متصل کنید تا برای همیشه اطلاعات باقی بمانند.',
    beforeCode: {
      file: 'config.py',
      description: 'کد قبلی که دیتابیس را در دایرکتوری موقت نگهداری می‌کرد:',
      code: `# مسیر موقت که با هر تغییر پاک می‌شد:
DB_PATH = os.environ.get("DB_PATH", "/tmp/ytdl_bot/bot.db")`
    },
    afterCode: {
      file: 'config.py & Dockerfile',
      description: 'کد جدید با پشتیبانی از دایرکتوری داده‌های دائمی:',
      code: `# config.py: ذخیره در مسیر دائمی داخل پروژه
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.getcwd(), "data", "bot.db"))

# Dockerfile:
VOLUME ["/app/data"]`
    },
    keyTakeaway: 'هرگز دیتابیس SQLite را در /tmp ذخیره نکنید. همیشه از مسیر پایدار مانند /app/data به همراه Persistent Volume در پلتفرم‌های ابری استفاده کنید.'
  },
  {
    id: 'cache-size-traffic-bloat',
    number: 3,
    title: 'برابری فایل کش با ترافیک دانلود و نحوه فوروارد پست قبلی تلگرام',
    shortDesc: 'کش نباید فایلی را دوباره روی دیسک نگه دارد یا دانلود مجدد کند؛ باید پیام قبلی تلگرام فوروارد شود.',
    category: 'cache',
    severity: 'high',
    affectedFiles: ['handlers.py', 'utils.py', 'db.py'],
    rootCause: `۱. در خط ۷۹۶ فایل handlers.py مقدار telegram_file_id برابر str(sent_msg.media) ذخیره می‌شد که یک رشته متنی پایتونی مثل MessageMediaDocument(...) بود! وقتی کاربر درخواست می‌داد، تلگرام نمی‌توانست با این متن فایل را بفرستد و خطای پیدا نشدن فایل می‌داد؛ در نتیجه بات فکر می‌کرد فایل در کش نیست و دوباره آن را از یوتیوب دانلود می‌کرد (ترافیک سرور ۲ برابر می‌شد!).
۲. تابع cleanup_files در utils.py فقط فایل‌های با فرمت session_id.* را پاک می‌کرد و تصاویر کاور session_id_thumb.jpg و session_id_raw_thumb روی هارد دیسک سرور باقی می‌ماندند و دیسک پر می‌شد.
۳. در آمار پنل ادمین، مجموع حجم فایل‌های ثبت شده به اشتباه به عنوان حجم فیزیکی کش نمایش داده می‌شد در حالی که کش فقط رکوردهای متنی در دیتابیس است.`,
    whyOtherBotsWorked: 'بات‌ها فایل دانلود شده را بلافاصله از هارد دیسک سرور حذف می‌کنند و تنها شناسه فشرده تلگرام (telethon.utils.pack_bot_file_id) یا شناسه پیام کانال لاگ را ذخیره می‌کنند. در درخواست بعدی، بدون ۱ بایت دانلود از یوتیوب، پیام را در کسری از ثانیه فوروارد می‌کنند.',
    solutionExplanation: 'استفاده از telethon.utils.pack_bot_file_id برای ذخیره دقیق شناسه تلگرام پیاده‌سازی شد. قابلیت بازیابی سریع با supports_streaming اضافه شد و تابع cleanup_files اصلاح شد تا با الگوی session_id* تمام فایل‌های کاور و قطعات موقت را ۱۰۰٪ از روی دیسک پاک کند.',
    beforeCode: {
      file: 'handlers.py & utils.py',
      description: 'کد قبلی که شناسه تلگرام را اشتباه ذخیره می‌کرد و فایل‌های کاور را روی دیسک جا می‌گذاشت:',
      code: `# handlers.py خط ۷۹۸:
telegram_file_id = sent_msg.media
db.set_cache(..., telegram_file_id=str(telegram_file_id), ...) # باگ: رشته نامعتبر!

# utils.py خط ۶۱:
pattern = os.path.join(download_dir, f"{session_id}.*") # تامبنیل‌ها با _thumb پاک نمی‌شدند!`
    },
    afterCode: {
      file: 'handlers.py & utils.py',
      description: 'کد اصلاح‌شده با بسته‌بندی استاندارد file_id تلگرام و پاکسازی کامل دیسک:',
      code: `# handlers.py: ذخیره استاندارد شناسه تلگرام
from telethon import utils as telethon_utils
packed_id = telethon_utils.pack_bot_file_id(sent_msg.media)
await asyncio.to_thread(db.set_cache, video_id, quality, media_type, packed_id, file_size)

# تحویل آنی از کش با ترافیک ۰ مگابایت:
sent_msg = await client.send_file(event.chat_id, file_id, caption=caption, supports_streaming=True)

# utils.py: پاکسازی قطعی تمام تامبنیل‌ها و فایل‌های موقت
pattern = os.path.join(download_dir, f"{session_id}*")`
    },
    keyTakeaway: 'با بسته‌بندی صحیح file_id در تلگرام و پاکسازی دیسک با session_id*، حجم مصرفی دیسک سرور همیشه نزدیک صفر می‌ماند و فایل‌های تکراری با ترافیک صفر تحویل داده می‌شوند.'
  },
  {
    id: 'persian-video-info-caption',
    number: 4,
    title: 'فارسی‌سازی کامل اطلاعات ویدیو (عنوان، زمان، کانال، بازدید و کامنت)',
    shortDesc: 'هنگام ارسال لینک یوتیوب، فیلدهای مشخصات ویدیو به انگلیسی نوشته می‌شدند.',
    category: 'i18n',
    severity: 'medium',
    affectedFiles: ['i18n.py'],
    rootCause: 'در دیکشنری زبان فارسی فایل i18n.py، برچسب‌های کلیدی مانند Title:، Duration:، Channel:، View:، Comments: و Release date: مستقیماً با کلمات انگلیسی در رشته متنی fa درج شده بودند.',
    whyOtherBotsWorked: 'بات‌های استاندارد فارسی، تمپلیت‌های پیام را با برچسب‌های فارسی خوانا، ایموجی‌های مرتبط و چینش راست‌چین تنظیم می‌کنند.',
    solutionExplanation: 'متن video_info_caption و playlist_info_caption در دیکشنری fa به طور کامل به زبان فارسی، با فونت‌بندی بولد تلگرامی و آیکون‌های متناسب بازنویسی شد.',
    beforeCode: {
      file: 'i18n.py',
      description: 'کد قبلی با برچسب‌های انگلیسی در بخش فارسی:',
      code: `"video_info_caption": {
    "fa": (
        "👀 اطلاعات ویدیو به شرح زیر می‌باشد:\\n"
        "📹 Title: {title}\\n"
        "🕰 Duration: {duration}\\n"
        "📺 Channel: {uploader}\\n"
        "👁 View: {views}\\n"
        "🖨 Comments: {comments}\\n"
        "📅 Release date: {upload_date}"
    ),
}`
    },
    afterCode: {
      file: 'i18n.py',
      description: 'کد جدید کاملاً فارسی با فرمت شکیل و خوانا:',
      code: `"video_info_caption": {
    "fa": (
        "👀 <b>مشخصات و اطلاعات ویدیو:</b>\\n\\n"
        "🎬 <b>عنوان:</b> {title}\\n"
        "⏱ <b>مدت زمان:</b> {duration}\\n"
        "📢 <b>کانال:</b> {uploader}\\n"
        "👁 <b>تعداد بازدید:</b> {views}\\n"
        "💬 <b>نظرات:</b> {comments}\\n"
        "📅 <b>تاریخ انتشار:</b> {upload_date}\\n\\n"
        "👇 کیفیت یا فرمت دلخواه را انتخاب کنید:"
    ),
}`
    },
    keyTakeaway: 'تمام متون کاربری در i18n.py اکنون به زبان فارسی اصیل تبدیل شده و برای نمایش در کلاینت‌های تلگرام کاملاً راست‌چین و خواناست.'
  },
  {
    id: 'audio-streaming-music-player',
    number: 5,
    title: 'ارسال صداها به صورت موزیک عادی تلگرام با قابلیت پخش آنلاین (Streaming)',
    shortDesc: 'کاربر باید صبر می‌کرد فایل صوتی کامل دانلود شود؛ اکنون مثل موزیک عادی قبل از اتمام دانلود پخش می‌شود.',
    category: 'audio',
    severity: 'high',
    affectedFiles: ['handlers.py', 'youtube.py'],
    rootCause: `۱. در خط ۷۹۲ فایل handlers.py صراحتاً نوشته شده بود:
supports_streaming=True if media_type == "video" else False
یعنی برای فایل‌های صوتی قابلیت استریمینگ تلگرام False شده بود! به همین خاطر کلاینت تلگرام اجازه پخش تدریجی (بافرینگ آنلاین) هنگام دانلود را نمی‌داد.
۲. در اتریبیوت DocumentAttributeAudio، مقدار voice=False تعیین نشده بود و گاهی تلگرام آن را یک فایل ناشناخته بدون پلیر در نظر می‌گرفت.
۳. در تابع download_audio در youtube.py متادیتاهای صوتی (آرتیست، عنوان، کاور آلبوم) با FFmpegMetadata تزریق نمی‌شدند.`,
    whyOtherBotsWorked: 'تلگرام وقتی فایلی را با DocumentAttributeAudio(voice=False, title=..., performer=...) و supports_streaming=True همراه با کاور دریافت کند، آن را فوراً در نوار پلیر بالای تلگرام لود می‌کند و کاربر با زدن دکمه Play می‌تواند قبل از دانلود ۱۰۰٪ به آن گوش کند.',
    solutionExplanation: 'مقدار supports_streaming برای هر دو رسانه صوتی و تصویری True شد. ویژگی voice=False فعال شد و در yt-dlp افزونه FFmpegMetadata فعال شد تا تگ‌های ID3 در فایل MP3 قرار گیرند.',
    beforeCode: {
      file: 'handlers.py & youtube.py',
      description: 'کد قبلی که استریم صدا را خاموش کرده بود:',
      code: `# handlers.py خط ۷۹۲:
sent_msg = await client.send_file(
    ...,
    supports_streaming=True if media_type == "video" else False, # باگ: برای صدا خاموش بود!
)

# youtube.py: فقط استخراج خام بدون تزریق متادیتا
postprocessors=[{
    "key": "FFmpegExtractAudio",
    "preferredcodec": "mp3",
    "preferredquality": bitrate,
}]`
    },
    afterCode: {
      file: 'handlers.py & youtube.py',
      description: 'کد جدید با پشتیبانی از استریم و پلیر رسمی تلگرام:',
      code: `# handlers.py:
attributes.append(
    DocumentAttributeAudio(
        duration=int(raw_duration or 0),
        title=title or "Audio Track",
        performer=uploader or "YouTube",
        voice=False, # تبدیل قطعی به ترک موسیقی
    )
)
sent_msg = await client.send_file(
    event.chat_id,
    file_path,
    caption=caption,
    thumb=thumb_path, # کاور موزیک برای آلبوم آرت
    attributes=attributes,
    supports_streaming=True, # فعال‌سازی استریم صوتی در پلیر تلگرام!
)

# youtube.py:
postprocessors=[
    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": bitrate},
    {"key": "FFmpegMetadata", "add_metadata": True}, # درج نام خواننده و آهنگ در تگ MP3
]`
    },
    keyTakeaway: 'با ارسال supports_streaming=True و DocumentAttributeAudio(voice=False)، تلگرام قابلیت استریم پیشرفته موزیک را فعال می‌کند و کاربر بلافاصله پس از لمس دکمه پخش به موزیک گوش می‌دهد.'
  }
];
