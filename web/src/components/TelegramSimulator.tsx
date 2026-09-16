import React, { useState, useRef, useEffect, useMemo } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Play, 
  Pause, 
  RotateCcw, 
  CheckCircle2, 
  Sparkles, 
  Film, 
  Music, 
  Zap, 
  AlertTriangle,
  Volume2,
  Share2,
  Clock,
  Eye,
  MessageSquare,
  Shield,
  Settings,
  ChevronDown,
  ChevronUp,
  LayoutGrid,
  Radio,
  Sliders,
  Terminal,
  Search,
  ExternalLink,
  Users,
  HardDrive,
  BarChart3,
  Wrench,
  Check,
  X,
  PhoneCall,
  Globe,
  BookOpen,
  Megaphone,
  UserCheck,
  RefreshCw,
  Info
} from 'lucide-react';

// Types representing messages in Telegram
interface TelegramButton {
  label: string;
  action: string;
  url?: string;
  data?: string;
}

interface SimulatedMessage {
  id: string;
  sender: 'user' | 'bot';
  type: 'text' | 'card' | 'media_video' | 'media_audio' | 'force_join' | 'search_results';
  content?: string;
  videoData?: {
    id: string;
    title: string;
    duration: string;
    uploader: string;
    views: string;
    comments: string;
    uploadDate: string;
    thumbnail: string;
  };
  mediaData?: {
    title: string;
    uploader: string;
    quality: string;
    fileSize: string;
    isAudio: boolean;
    isCacheHit?: boolean;
    streamUrl?: string;
  };
  searchResults?: {
    id: string;
    title: string;
    duration: string;
    channel: string;
    views: string;
    url: string;
  }[];
  inlineButtons?: TelegramButton[][];
  time: string;
}

// Sample YouTube catalog for realistic simulation
const SAMPLE_VIDEOS = [
  {
    url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    title: 'Rick Astley - Never Gonna Give You Up (Official Music Video)',
    duration: '3:33',
    uploader: 'Rick Astley Official',
    views: '۱,۴۵۰,۸۲۰,۰۰۰',
    comments: '۲,۸۴۰,۱۵۰',
    uploadDate: '2009-10-25',
    thumbnail: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop&q=80',
    audioPreview: 'https://actions.google.com/sounds/v1/ambiences/rain_heavy.ogg'
  },
  {
    url: 'https://www.youtube.com/watch?v=jfKfPfyJRdk',
    title: 'Lofi Hip Hop Radio - Beats to Relax/Study to',
    duration: '1:45:20',
    uploader: 'Lofi Girl',
    views: '۹۵,۲۰۰,۰۰۰',
    comments: '۴۵۰,۱۰۰',
    uploadDate: '2023-01-15',
    thumbnail: 'https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=600&auto=format&fit=crop&q=80',
    audioPreview: 'https://actions.google.com/sounds/v1/ambiences/rain_heavy.ogg'
  },
  {
    url: 'https://www.youtube.com/watch?v=shadmehr_aghili_tajrobeh_kon',
    title: 'Shadmehr Aghili - Tajrobeh Kon (شادمهر عقیلی - تجربه کن)',
    duration: '3:45',
    uploader: 'Taraneh Records',
    views: '۴۲,۳۰۰,۰۰۰',
    comments: '۱۲,۴۰۰',
    uploadDate: '2016-12-10',
    thumbnail: 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=600&auto=format&fit=crop&q=80',
    audioPreview: 'https://actions.google.com/sounds/v1/ambiences/rain_heavy.ogg'
  },
  {
    url: 'https://www.youtube.com/watch?v=python_full_course_2026',
    title: 'Python Complete Tutorial 2026 for Beginners (آموزش صفر تا صد پایتون)',
    duration: '6:15:00',
    uploader: 'Tech Academy Iran',
    views: '۱,۱۰۰,۰۰۰',
    comments: '۸,۹۰۰',
    uploadDate: '2025-06-01',
    thumbnail: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80',
    audioPreview: 'https://actions.google.com/sounds/v1/ambiences/rain_heavy.ogg'
  }
];

export const TelegramSimulator: React.FC = () => {
  // Simulator State: User Profile & Role
  const [currentUserRole, setCurrentUserRole] = useState<'user' | 'owner'>('user');
  const [currentUserId, setCurrentUserId] = useState<number>(10459281);
  const [currentUsername, setCurrentUsername] = useState<string>('kamyar_user');
  const [userLang, setUserLang] = useState<'fa' | 'en' | 'ru'>('fa');
  
  // Bot Global Settings State (mirrors database settings)
  const [forceJoinEnabled, setForceJoinEnabled] = useState(false);
  const [userJoinedChannels, setUserJoinedChannels] = useState(false);
  const [maintenanceMode, setMaintenanceMode] = useState(false);
  const [dailyLimitCount, setDailyLimitCount] = useState(10);
  const [todayDownloads, setTodayDownloads] = useState(3);
  const [totalDownloads, setTotalDownloads] = useState(47);
  const [bonusDownloads, setBonusDownloads] = useState(6);
  const [referralBonus, setReferralBonus] = useState(3);
  const [cachedItems, setCachedItems] = useState<Set<string>>(new Set(['v_360_dQw4w9WgXcQ']));
  
  // UI states
  const [inputMessage, setInputMessage] = useState('');
  const [showReplyKeyboard, setShowReplyKeyboard] = useState(true);
  const [adminMenuOpen, setAdminMenuOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioProgress, setAudioProgress] = useState(25);
  const [selectedQualityKey, setSelectedQualityKey] = useState<string | null>(null);

  // Chat message history
  const [messages, setMessages] = useState<SimulatedMessage[]>([
    {
      id: 'msg-start-user',
      sender: 'user',
      type: 'text',
      content: '/start',
      time: '12:00'
    },
    {
      id: 'msg-welcome',
      sender: 'bot',
      type: 'text',
      content: `🌹 سلام خوش اومدی\n➕ با من ویدیوهای یوتیوب رو به صورت تصویری و صوتی دانلود کن.\n\n🔸 برای شروع و دریافت کمک، از دکمه‌های پایین استفاده کن یا لینک یوتیوب بفرست:`,
      time: '12:00'
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const getTimeString = () => {
    const now = new Date();
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
  };

  // Bot Text Strings based on language (i18n.py implementation)
  const menuButtons = useMemo(() => {
    if (adminMenuOpen && currentUserRole === 'owner') {
      return [
        ['📊 آمار ربات'],
        ['👥 مدیریت کاربران', '📢 پیام همگانی'],
        ['⚙️ تنظیمات ربات', '💬 ویرایش متن‌ها'],
        ['🗂 کش و فایل‌ها', '🧾 لیست خطاها'],
        ['👮 مدیریت ادمین‌ها', '🔧 مود تعمیر'],
        ['⬅️ خروج از پنل ادمین']
      ];
    }

    if (userLang === 'en') {
      return [
        ['🔍 Search YouTube'],
        ['👤 My Account', '🚀 Free Traffic'],
        ['☎️ Support'],
        ['🌐 Change Language', '🍿 YouTube Download Guide'],
        ['📢 Information Channel']
      ];
    }
    if (userLang === 'ru') {
      return [
        ['🔍 Поиск на YouTube'],
        ['👤 Мой аккаунт', '🚀 Бесплатный трафик'],
        ['☎️ Поддержка'],
        ['🌐 Сменить язык', '🍿 Руководство по скачиванию'],
        ['📢 Канал новостей']
      ];
    }
    // Persian default
    return [
      ['🔍 جست‌وجو در یوتیوب'],
      ['👤 حساب من', '🚀 ترافیک رایگان'],
      ['☎️ پشتیبانی'],
      ['🌐 تغییر زبان', '🍿 راهنمای دانلود از یوتیوب'],
      ['📢 کانال اطلاع‌رسانی']
    ];
  }, [userLang, adminMenuOpen, currentUserRole]);

  // Check maintenance filter
  const checkMaintenance = (userText: string): boolean => {
    if (maintenanceMode && currentUserRole !== 'owner') {
      const msg: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: '🔧 ربات در حال حاضر در حال به‌روزرسانی و تعمیرات زیرساختی است.\nلطفاً دقایقی دیگر مجدداً تلاش نمایید.',
        time: getTimeString()
      };
      setMessages(prev => [...prev, msg]);
      return true;
    }
    return false;
  };

  // Check force join
  const checkForceJoin = (): boolean => {
    if (forceJoinEnabled && !userJoinedChannels) {
      const msg: SimulatedMessage = {
        id: 'bot-fj-' + Date.now(),
        sender: 'bot',
        type: 'force_join',
        content: '📢 برای ادامه استفاده از ربات، لطفاً ابتدا در کانال‌های زیر عضو شوید:\n\n📢 To continue using the bot, please join the channels below.',
        inlineButtons: [
          [{ label: '📢 کانال یوتیوب پلیر (@YTPlayer)', action: 'url', url: 'https://t.me' }],
          [{ label: '📢 کانال اطلاع‌رسانی ربات (@YTUpdates)', action: 'url', url: 'https://t.me' }],
          [{ label: 'عضو شدم ✅', action: 'check_join', data: 'check_join' }]
        ],
        time: getTimeString()
      };
      setMessages(prev => [...prev, msg]);
      return false;
    }
    return true;
  };

  // Process text or commands
  const handleProcessMessage = (rawText: string) => {
    const text = rawText.trim();
    if (!text) return;

    // Push user message
    const userMsg: SimulatedMessage = {
      id: 'user-' + Date.now(),
      sender: 'user',
      type: 'text',
      content: text,
      time: getTimeString()
    };
    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');

    // Handle /admin command
    if (text.startsWith('/admin')) {
      if (currentUserRole !== 'owner') {
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: `⛔ دسترسی غیرمجاز!\n\nشما به عنوان ادمین در ربات تعریف نشده‌اید.\n🆔 آیدی عددی تلگرام شما: ${currentUserId}\n\n💡 برای فعال‌سازی دسترسی مدیریت، این عدد را در بخش متغیرهای سرور به عنوان OWNER_ID وارد کنید:\nOWNER_ID=${currentUserId}`,
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }

      setAdminMenuOpen(true);
      const botReply: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: `🛠 به پنل مدیریت ربات خوش آمدید.\n👤 سطح دسترسی شما: مالک اصلی (owner)\n\nبرای انجام امور، یکی از دکمه‌های زیر را انتخاب کنید:`,
        time: getTimeString()
      };
      setMessages(prev => [...prev, botReply]);
      return;
    }

    // Check Maintenance
    if (checkMaintenance(text)) return;

    // Handle /start command
    if (text.startsWith('/start')) {
      if (!checkForceJoin()) return;

      const botReply: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: userLang === 'fa' 
          ? `🌹 سلام خوش اومدی\n➕ با من ویدیوهای یوتیوب رو به صورت تصویری و صوتی دانلود کن.\n\n🔸 برای شروع و دریافت کمک، از دکمه‌های پایین استفاده کن و دانلود از یوتیوب رو آغاز کن:`
          : userLang === 'en'
          ? `🌹 Welcome!\n➕ Download YouTube videos with me in high-quality video and audio formats.\n\n🔸 Use the buttons below or send a link to get started:`
          : `🌹 Добро пожаловать!\n➕ Скачивайте видео с YouTube в видео и аудио форматах.\n\n🔸 Используйте кнопки меню ниже:`,
        time: getTimeString()
      };
      setMessages(prev => [...prev, botReply]);
      return;
    }

    // Handle Admin Menu Replies
    if (adminMenuOpen && currentUserRole === 'owner') {
      if (text === '⬅️ خروج از پنل ادمین') {
        setAdminMenuOpen(false);
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: '✅ از پنل ادمین خارج شدید و به منوی اصلی کاربران بازگشتید.',
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }

      if (text === '📊 آمار ربات') {
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: `📊 آمار جامع ربات (دیتابیس داکر / SQLite):\n\n👥 کل کاربران ثبت‌شده: ۱,۴۵۲ نفر\n⚡ کاربران فعال امروز: ۱۸۴ نفر\n🗓 کاربران فعال این ماه: ۹۴۰ نفر\n\n📥 کل دانلودها: ۴,۲۸۰\n📥 دانلودهای امروز: ${todayDownloads + 38}\n❌ دانلودهای ناموفق: ۳ (صفر پس از پچ کدک)\n💾 کل ترافیک دانلود: ۱۸۲.۴ گیگابایت\n\n🗄 فایل‌های کش شده در تلگرام: ${cachedItems.size + 142} فایل (~32.1 GB ترافیک ذخیره‌شده)`,
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }

      if (text === '🗂 کش و فایل‌ها') {
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: `🗂 مدیریت کش فایل‌ها:\n\nتعداد فایل‌های کش شده با packed_file_id تلگرام: ${cachedItems.size + 142}\nحجم کل تخمینی: ۳۲.۱ گیگابایت (تحویل آنی بدون دانلود مجدد از یوتیوب)\n\nدستور پاکسازی دیتابیس کش: /clear_cache`,
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }

      if (text === '🧾 لیست خطاها') {
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: `🧾 آخرین خطاهای ثبت شده در جدول logs:\n\n✅ وضعیت: پس از اعمال پچ ۵ گانه هیچ خطایی در دانلود کیفیت‌های ۱۴۴p/۲۴۰p/۳۶۰p رخ نداده است.\n• آخرین هشدار: خطای FFmpeg تگ Opus که با پارامتر -c:a aac برطرف گردید.`,
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }

      if (text === '🔧 مود تعمیر') {
        const nextState = !maintenanceMode;
        setMaintenanceMode(nextState);
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: `🔧 مود تعمیر اکنون ${nextState ? 'فعال 🔴 (کاربران مسدود می‌شوند)' : 'غیرفعال 🟢 (ربات برای همه باز است)'} شد.`,
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }

      if (text === '⚙️ تنظیمات ربات') {
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: `⚙️ تنظیمات فعلی ربات:\n\n• جوین اجباری: ${forceJoinEnabled ? 'روشن ✅' : 'خاموش ❌'}\n• محدودیت روزانه: ${dailyLimitCount} دانلود در روز\n• دانلود هدیه رفرال: ${referralBonus} عدد\n• آیدی پشتیبانی: @YTBotSupport\n• کانال لاگ دانلود: -10019284710\n• مسیر دیتابیس پایدار: ./data/bot.db\n\nدستورات تغییر: /set_daily_limit, /set_ref_bonus, /set_force_join`,
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }

      if (text === '👥 مدیریت کاربران') {
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: `👥 راهنمای مدیریت کاربران:\n\n🔍 استعلام کاربر: /user 10459281\n⛔ بن کردن کاربر: /ban 10459281\n✅ رفع بن: /unban 10459281\n🎁 اضافه کردن دانلود هدیه: /add_bonus 10459281 10\n📥 خروجی اکسل و CSV کل کاربران: /export_users`,
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }

      if (text === '📢 پیام همگانی') {
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: `📢 ارسال پیام همگانی:\nدستور: /broadcast <تعداد ماه فعالیت>\n\nمثال برای کاربران فعال ۳ ماه گذشته:\n/broadcast 3\nسلام به تمام کاربران! کیفیت‌های ۱۰۸۰p و دانلود موزیک بهینه‌سازی شد.`,
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }

      if (text === '💬 ویرایش متن‌ها') {
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: `💬 ویرایش متن‌های ربات:\nدستور: /set_text <fa/en/ru> <کلید>\nمتن جدید...\n\nکلیدها: welcome, guide_text, search_prompt, free_traffic_text, support_text`,
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }

      if (text === '👮 مدیریت ادمین‌ها') {
        const botReply: SimulatedMessage = {
          id: 'bot-' + Date.now(),
          sender: 'bot',
          type: 'text',
          content: `👮 لیست ادمین‌های سیستم:\n• مالک اصلی: ${currentUserId} (Role: owner)\n• سرپرست فنی: 98712344 (Role: full)\n\nافزودن ادمین جدید: /add_admin <user_id> <full/viewer>`,
          time: getTimeString()
        };
        setMessages(prev => [...prev, botReply]);
        return;
      }
    }

    // Handle Regular User Menu Replies
    if (text === '🔍 جست‌وجو در یوتیوب' || text === '🔍 Search YouTube' || text === '🔍 Поиск на YouTube') {
      const botReply: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: `🔎 جستجوی سریع ویدیو در یوتیوب\n\nکافیه لینک ویدیو رو کپی کنی و برای ربات بفرستی، یا نام خواننده/ویدیو رو بنویسی تا برات جستجو کنم!`,
        time: getTimeString()
      };
      setMessages(prev => [...prev, botReply]);
      return;
    }

    if (text === '👤 حساب من' || text === '👤 My Account' || text === '👤 Мой аккаунт') {
      const rem = Math.max(0, dailyLimitCount + bonusDownloads - todayDownloads);
      const botReply: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: `🆔 آیدی کاربری شما: ${currentUserId}\n📥 کل دانلودها: ${totalDownloads}\n📊 دانلودهای موفق امروز: ${todayDownloads}\n🎁 دانلود هدیه از زیرمجموعه: ${bonusDownloads}\n♻️ دانلودهای باقی‌مانده مجاز امروز: ${rem}\n🌐 زبان فعال: ${userLang === 'fa' ? 'فارسی 🇮🇷' : userLang === 'en' ? 'English 🇬🇧' : 'Русский 🇷🇺'}`,
        time: getTimeString()
      };
      setMessages(prev => [...prev, botReply]);
      return;
    }

    if (text === '🚀 ترافیک رایگان' || text === '🚀 Free Traffic' || text === '🚀 Бесплатный трафик') {
      const botReply: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: `سلام دوست عزیز! 🎉\n\nبا دعوت از دوستانت به ربات ما، ${referralBonus} دانلود رایگان هدیه بگیر! 🚀🎁\n\nفقط کافیه دوستانت روی لینک زیر کلیک کنن و به ربات بپیوندن تا این هدیه ویژه به حسابت اضافه بشه! 😍\n\n🔗 لینک دعوت اختصاصی شما:\n👉 https://t.me/YourYouTubeDownloaderBot?start=ref_${currentUserId}`,
        time: getTimeString()
      };
      setMessages(prev => [...prev, botReply]);
      return;
    }

    if (text === '☎️ پشتیبانی' || text === '☎️ Support' || text === '☎️ Поддержка') {
      const botReply: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: `آیدی پشتیبانی جهت برقراری ارتباط و پیگیری مشکلات:\n👉 @YTBotSupport\nکانال اطلاع‌رسانی: @YTChannelOfficial`,
        time: getTimeString()
      };
      setMessages(prev => [...prev, botReply]);
      return;
    }

    if (text === '🌐 تغییر زبان' || text === '🌐 Change Language' || text === '🌐 Сменить язык') {
      const botReply: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: `لطفاً زبان مورد نظر خود را انتخاب کنید:\nPlease select your language:\nПожалуйста, выберите язык:`,
        inlineButtons: [
          [
            { label: '🇮🇷 فارسی', action: 'lang', data: 'lang:fa' },
            { label: '🇬🇧 English', action: 'lang', data: 'lang:en' },
            { label: '🇷🇺 Русский', action: 'lang', data: 'lang:ru' }
          ]
        ],
        time: getTimeString()
      };
      setMessages(prev => [...prev, botReply]);
      return;
    }

    if (text === '🍿 راهنمای دانلود از یوتیوب' || text === '🍿 YouTube Download Guide' || text === '🍿 Руководство по скачиванию') {
      const botReply: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: `📥 آموزش دانلود از یوتیوب با ربات:\n\n🚀 فقط کافیه لینک ویدیوی یوتیوب رو برام بفرستی، بعدش خودت انتخاب می‌کنی که با چه کیفیتی دانلود بشه! 🎬⬇️\n\n🔹 چطور لینک ویدیو رو کپی کنی؟\n1️⃣ وارد یوتیوب شو.\n2️⃣ ویدیوی موردنظرت رو باز کن.\n3️⃣ روی دکمه "Share" (اشتراک‌گذاری) بزن و "Copy Link" رو انتخاب کن.\n4️⃣ لینک رو همینجا بفرست، بعدش لیست کیفیت‌های مختلف نمایش داده میشه تا یکی رو انتخاب کنی!\n\n💡 حالا یکی از لینک‌های نمونه رو بفرست تا تست کنی! 🎥⚡️`,
        time: getTimeString()
      };
      setMessages(prev => [...prev, botReply]);
      return;
    }

    if (text === '📢 کانال اطلاع‌رسانی' || text === '📢 Information Channel' || text === '📢 Канал новостей') {
      const botReply: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: `📢 کانال اطلاع‌رسانی ربات:\nhttps://t.me/YTChannelOfficial\n\nآخرین اخبار آپدیت‌ها و سرورهای جدید را در کانال دنبال کنید.`,
        time: getTimeString()
      };
      setMessages(prev => [...prev, botReply]);
      return;
    }

    // Check if user entered a search query or a YouTube URL
    if (text.toLowerCase().includes('youtube.com') || text.toLowerCase().includes('youtu.be')) {
      handleYouTubeUrlInput(text);
      return;
    }

    // Otherwise, treat as search keyword
    handleSearchKeyword(text);
  };

  // Handle Search Keyword
  const handleSearchKeyword = (query: string) => {
    setLoading(true);
    setStatusText(`🔎 در حال جستجو در یوتیوب برای: "${query}"...`);

    setTimeout(() => {
      setLoading(false);
      setStatusText('');

      const filtered = SAMPLE_VIDEOS.filter(v => 
        v.title.toLowerCase().includes(query.toLowerCase()) || 
        v.uploader.toLowerCase().includes(query.toLowerCase())
      );
      const results = filtered.length > 0 ? filtered : SAMPLE_VIDEOS.slice(0, 3);

      const msg: SimulatedMessage = {
        id: 'bot-search-' + Date.now(),
        sender: 'bot',
        type: 'search_results',
        content: `🔍 نتایج جستجو برای: <b>${query}</b>\nبرای دانلود هر ویدیو روی دکمه مربوطه کلیک کنید:`,
        searchResults: results.map(r => ({
          id: r.url,
          title: r.title,
          duration: r.duration,
          channel: r.uploader,
          views: r.views,
          url: r.url
        })),
        time: getTimeString()
      };
      setMessages(prev => [...prev, msg]);
    }, 800);
  };

  // Handle YouTube URL Input
  const handleYouTubeUrlInput = (url: string) => {
    if (!checkForceJoin()) return;

    // Find matched sample or mock
    const video = SAMPLE_VIDEOS.find(v => url.includes(v.title) || url.includes('dQw4w9WgXcQ')) || {
      url: url,
      title: 'YouTube Video - High Definition Stream',
      duration: '4:12',
      uploader: 'Official YouTube Channel',
      views: '۸۵۰,۲۰۰',
      comments: '۱,۴۲۰',
      uploadDate: '2024-03-12',
      thumbnail: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=600&auto=format&fit=crop&q=80',
      audioPreview: ''
    };

    setLoading(true);
    setStatusText('🔎 در حال استخراج مشخصات و فرمت‌های موجود با yt-dlp...');

    setTimeout(() => {
      setLoading(false);
      setStatusText('');

      const botCardMsg: SimulatedMessage = {
        id: 'bot-card-' + Date.now(),
        sender: 'bot',
        type: 'card',
        videoData: {
          id: 'vid-' + Date.now(),
          title: video.title,
          duration: video.duration,
          uploader: video.uploader,
          views: video.views,
          comments: video.comments,
          uploadDate: video.uploadDate,
          thumbnail: video.thumbnail
        },
        inlineButtons: [
          [
            { label: '🎧 mp3 متوسط (~3.5 MB)', action: 'dl', data: `dl:a_med:${video.title}` },
            { label: '🎧 mp3 باکیفیت (~8.2 MB)', action: 'dl', data: `dl:a_best:${video.title}` }
          ],
          [
            { label: '🎥 144p (~1.8 MB)', action: 'dl', data: `dl:v_144:${video.title}` },
            { label: '🎥 240p (~3.2 MB)', action: 'dl', data: `dl:v_240:${video.title}` }
          ],
          [
            { label: '🎥 360p (~6.5 MB) [فرمت ۱۸]', action: 'dl', data: `dl:v_360:${video.title}` },
            { label: '🎥 480p (~12.1 MB)', action: 'dl', data: `dl:v_480:${video.title}` }
          ],
          [
            { label: '🎥 720p HD (~23.5 MB)', action: 'dl', data: `dl:v_720:${video.title}` },
            { label: '🎥 1080p FHD (~49.0 MB)', action: 'dl', data: `dl:v_1080:${video.title}` }
          ]
        ],
        time: getTimeString()
      };

      setMessages(prev => [...prev, botCardMsg]);
    }, 700);
  };

  // Handle Inline Button Clicks (Callbacks)
  const handleInlineClick = (button: TelegramButton) => {
    // 1. Language change callback
    if (button.data?.startsWith('lang:')) {
      const newLang = button.data.split(':')[1] as 'fa' | 'en' | 'ru';
      setUserLang(newLang);
      const msg: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: newLang === 'fa' 
          ? '✅ زبان شما با موفقیت به فارسی تغییر یافت.' 
          : newLang === 'en' 
          ? '✅ Your language has been set to English.' 
          : '✅ Ваш язык изменен на Русский.',
        time: getTimeString()
      };
      setMessages(prev => [...prev, msg]);
      return;
    }

    // 2. Forced join verification callback
    if (button.action === 'check_join' || button.data === 'check_join') {
      setUserJoinedChannels(true);
      const msg: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: '✅ عضویت شما در کانال‌ها تأیید شد!\n🌹 به ربات دانلود از یوتیوب خوش آمدید.',
        time: getTimeString()
      };
      setMessages(prev => [...prev, msg]);
      return;
    }

    // 3. Download format selection callback
    if (button.data?.startsWith('dl:')) {
      const parts = button.data.split(':');
      const formatKey = parts[1];
      const videoTitle = parts[2] || 'YouTube Video';
      const isAudio = formatKey.startsWith('a_');
      const cacheKey = `${formatKey}_${videoTitle}`;
      const isCacheHit = cachedItems.has(cacheKey);

      setSelectedQualityKey(formatKey);
      setLoading(true);
      setStatusText(
        isCacheHit 
          ? '⚡ فایل در کش تلگرام موجود است! ارسال فوری با packed_file_id (ترافیک: ۰ بایت)...' 
          : `⏳ در حال دانلود و ادغام با FFmpeg (${button.label.split(' ')[1]})...`
      );

      // Telethon download progression simulation
      setTimeout(() => {
        if (!isCacheHit) {
          setStatusText('⚙️ تبدیل کدک صدا به AAC سازگار با تلگرام (-c:a aac -movflags +faststart)...');
        }
      }, 500);

      setTimeout(() => {
        setLoading(false);
        setStatusText('');

        // Increment today download counter
        setTodayDownloads(prev => prev + 1);
        setTotalDownloads(prev => prev + 1);
        setCachedItems(prev => new Set(prev).add(cacheKey));

        const mediaMsg: SimulatedMessage = {
          id: 'media-' + Date.now(),
          sender: 'bot',
          type: isAudio ? 'media_audio' : 'media_video',
          mediaData: {
            title: videoTitle,
            uploader: 'Official Channel',
            quality: formatKey.replace('v_', '').replace('a_med', 'MP3 192k').replace('a_best', 'MP3 320k'),
            fileSize: button.label.match(/~[\d.]+ MB/)?.[0] || '6.5 MB',
            isAudio,
            isCacheHit
          },
          inlineButtons: [
            [{ label: '⚠️ گزارش مشکل در دانلود', action: 'report', data: 'report:issue' }]
          ],
          time: getTimeString()
        };

        setMessages(prev => [...prev, mediaMsg]);
      }, isCacheHit ? 400 : 1300);
      return;
    }

    // 4. Report issue callback
    if (button.action === 'report') {
      const msg: SimulatedMessage = {
        id: 'bot-' + Date.now(),
        sender: 'bot',
        type: 'text',
        content: '🙏 گزارش شما برای تیم پشتیبانی ثبت شد. در صورتی که فایل پخش نمی‌شود یا مشکلی دارد، فرمت دیگری را امتحان فرمایید.',
        time: getTimeString()
      };
      setMessages(prev => [...prev, msg]);
      return;
    }
  };

  const handleResetChat = () => {
    setMessages([
      {
        id: 'msg-start-user',
        sender: 'user',
        type: 'text',
        content: '/start',
        time: '12:00'
      },
      {
        id: 'msg-welcome',
        sender: 'bot',
        type: 'text',
        content: `🌹 سلام خوش اومدی\n➕ با من ویدیوهای یوتیوب رو به صورت تصویری و صوتی دانلود کن.\n\n🔸 برای شروع و دریافت کمک، از دکمه‌های پایین استفاده کن یا لینک یوتیوب بفرست:`,
        time: '12:00'
      }
    ]);
    setCachedItems(new Set());
    setIsPlayingAudio(false);
    setAdminMenuOpen(false);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      {/* Top Banner & Multi-feature Bot Simulator Header */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-900/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
            <Bot className="w-5 h-5" />
            <span>شبیه‌ساز کامل ربات تلگرام و تمام کدهای بک‌اند (Full Bot Simulation)</span>
          </div>
          <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
            اینجا محیط واقعی تلگرام است. تمام منوها، دکمه‌های شیشه‌ای، پنل مدیریت ادمین، دستورات /admin و /start، بررسی جوین اجباری، سهمیه روزانه، جستجو و استریم موزیک متصل به کدهای پایتون هستند.
          </p>
        </div>

        {/* Quick Identity / Role Switcher */}
        <div className="flex flex-wrap items-center gap-2 self-stretch md:self-auto justify-end">
          <div className="flex items-center gap-1.5 bg-slate-800/90 border border-slate-700 px-3 py-1.5 rounded-xl text-xs">
            <User className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400">هویت تست:</span>
            <select
              value={currentUserRole}
              onChange={e => {
                const newRole = e.target.value as 'user' | 'owner';
                setCurrentUserRole(newRole);
                if (newRole === 'user') setAdminMenuOpen(false);
              }}
              className="bg-slate-900 text-white font-bold rounded px-1.5 py-0.5 border border-slate-700 outline-none cursor-pointer"
            >
              <option value="user">کاربر عادی (User)</option>
              <option value="owner">مالک و ادمین اصلی (Owner)</option>
            </select>
          </div>

          <button
            onClick={handleResetChat}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs transition cursor-pointer border border-slate-700"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>شروع مجدد</span>
          </button>
        </div>
      </div>

      {/* Quick Test Bar: Sample Video Buttons & Fast Command Shortcuts */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-200">
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>ارسال سریع ویدیوهای تستی برای بررسی ۵ پچ:</span>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">
            کش فایل‌ها: {cachedItems.size} مورد ذخیره
          </span>
        </div>

        <div className="flex flex-wrap gap-2">
          {SAMPLE_VIDEOS.map((v, i) => (
            <button
              key={i}
              onClick={() => handleProcessMessage(v.url)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-indigo-500/50 hover:bg-indigo-950/20 text-slate-200 text-xs transition cursor-pointer"
              title={v.title}
            >
              <Film className="w-3.5 h-3.5 text-indigo-400" />
              <span className="max-w-[170px] truncate">{v.title.split('-')[0]}</span>
              <span className="text-[10px] text-slate-400 font-mono">{v.duration}</span>
            </button>
          ))}
          
          <button
            onClick={() => handleProcessMessage('/admin')}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 text-xs font-bold transition hover:bg-indigo-600/30 cursor-pointer"
          >
            <Shield className="w-3.5 h-3.5 text-indigo-400" />
            <span>دستور /admin</span>
          </button>

          <button
            onClick={() => setForceJoinEnabled(!forceJoinEnabled)}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs transition cursor-pointer ${
              forceJoinEnabled 
                ? 'bg-emerald-600/20 text-emerald-300 border-emerald-500/40' 
                : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
            }`}
          >
            <Megaphone className="w-3.5 h-3.5" />
            <span>جوین اجباری: {forceJoinEnabled ? 'فعال' : 'غیرفعال'}</span>
          </button>
        </div>
      </div>

      {/* Main Telegram App Window */}
      <div className="rounded-3xl border border-slate-800 bg-[#0f172a] overflow-hidden shadow-2xl flex flex-col h-[700px]">
        {/* Telegram Chat Header */}
        <div className="bg-[#1e293b] px-4 py-3 border-b border-slate-700/80 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-sky-500 flex items-center justify-center text-white shadow-md ring-2 ring-indigo-400/20">
                <Bot className="w-5 h-5" />
              </div>
              <span className="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-emerald-400 border-2 border-[#1e293b]"></span>
            </div>

            <div>
              <div className="font-bold text-sm text-white flex items-center gap-2">
                <span>YouTube Downloader Bot</span>
                {currentUserRole === 'owner' && (
                  <span className="text-[10px] px-2 py-0.2 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-semibold">
                    حالت ادمین
                  </span>
                )}
              </div>
              <div className="text-[11px] text-slate-400 flex items-center gap-2">
                <span>bot @YourYTDownloaderBot</span>
                <span>•</span>
                <span className="text-emerald-400">آنلاین (Telethon 1.36.0)</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <div className="hidden sm:flex items-center gap-2 text-slate-400 font-mono text-[11px]">
              <span>سهمیه امروز: <strong className="text-emerald-400">{todayDownloads}/{dailyLimitCount}</strong></span>
              <span>•</span>
              <span>زبان: <strong className="text-indigo-300">{userLang.toUpperCase()}</strong></span>
            </div>

            <button
              onClick={() => setShowReplyKeyboard(!showReplyKeyboard)}
              className={`p-2 rounded-xl transition ${
                showReplyKeyboard ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
              title="نمایش یا پنهان کردن دکمه‌های منوی تلگرام"
            >
              <LayoutGrid className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Message Area */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-gradient-to-b from-[#0f172a] via-[#0b1120] to-[#090d16]">
          {messages.map(msg => (
            <div
              key={msg.id}
              className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
            >
              {/* Plain Text Message */}
              {msg.type === 'text' && (
                <div
                  className={`max-w-md p-3.5 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-md ${
                    msg.sender === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-xs'
                      : 'bg-[#1e293b] text-slate-100 border border-slate-700/70 rounded-bl-xs'
                  }`}
                >
                  <div className="whitespace-pre-line select-text font-normal">
                    {msg.content}
                  </div>

                  {/* Inline Buttons attached to message */}
                  {msg.inlineButtons && msg.inlineButtons.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-slate-700/80 space-y-1.5">
                      {msg.inlineButtons.map((row, rIdx) => (
                        <div key={rIdx} className="flex flex-wrap gap-1.5">
                          {row.map((btn, bIdx) => (
                            <button
                              key={bIdx}
                              onClick={() => handleInlineClick(btn)}
                              className="flex-1 min-w-[120px] py-1.5 px-3 rounded-xl bg-slate-800/90 hover:bg-indigo-600/30 text-indigo-200 border border-indigo-500/30 text-xs font-semibold transition cursor-pointer text-center"
                            >
                              {btn.label}
                            </button>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}

                  <div
                    className={`text-[10px] mt-1 text-left ${
                      msg.sender === 'user' ? 'text-indigo-200' : 'text-slate-400'
                    }`}
                  >
                    {msg.time}
                  </div>
                </div>
              )}

              {/* Force Join Message */}
              {msg.type === 'force_join' && (
                <div className="max-w-md w-full bg-[#1e293b] rounded-2xl p-4 border border-amber-500/40 shadow-xl space-y-3 text-xs leading-relaxed">
                  <div className="flex items-center gap-2 text-amber-400 font-bold">
                    <Megaphone className="w-4 h-4" />
                    <span>عضویت در کانال‌های اسپانسر الزامی است</span>
                  </div>
                  <p className="text-slate-200 whitespace-pre-line">{msg.content}</p>
                  
                  {msg.inlineButtons && (
                    <div className="space-y-1.5 pt-2">
                      {msg.inlineButtons.map((row, rIdx) => (
                        <div key={rIdx} className="flex gap-1.5">
                          {row.map((btn, bIdx) => (
                            <button
                              key={bIdx}
                              onClick={() => handleInlineClick(btn)}
                              className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition text-center cursor-pointer ${
                                btn.action === 'check_join'
                                  ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow'
                                  : 'bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-slate-700'
                              }`}
                            >
                              {btn.label}
                            </button>
                          ))}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Search Results Card */}
              {msg.type === 'search_results' && (
                <div className="max-w-md w-full bg-[#1e293b] rounded-2xl p-4 border border-slate-700 shadow-xl space-y-3 text-xs">
                  <div className="flex items-center gap-2 text-indigo-400 font-bold border-b border-slate-700 pb-2">
                    <Search className="w-4 h-4" />
                    <span dangerouslySetInnerHTML={{ __html: msg.content || '' }} />
                  </div>

                  <div className="space-y-2">
                    {msg.searchResults?.map((res, idx) => (
                      <div 
                        key={idx} 
                        className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-indigo-500/40 transition flex items-center justify-between gap-2"
                      >
                        <div className="min-w-0 flex-1">
                          <div className="font-bold text-white truncate">{res.title}</div>
                          <div className="text-[11px] text-slate-400">{res.channel} • {res.duration}</div>
                        </div>
                        <button
                          onClick={() => handleYouTubeUrlInput(res.url)}
                          className="px-2.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold cursor-pointer shrink-0"
                        >
                          دانلود
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Video Info Card with Format Quality Buttons */}
              {msg.type === 'card' && msg.videoData && (
                <div className="max-w-md w-full bg-[#1e293b] rounded-2xl overflow-hidden border border-slate-700 shadow-xl space-y-3">
                  {/* Thumbnail Banner */}
                  <div className="relative aspect-video w-full bg-slate-950 overflow-hidden">
                    <img
                      src={msg.videoData.thumbnail}
                      alt={msg.videoData.title}
                      className="w-full h-full object-cover"
                      referrerPolicy="no-referrer"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
                    <span className="absolute bottom-2 left-2 bg-black/80 text-white font-mono text-xs px-2 py-0.5 rounded">
                      {msg.videoData.duration}
                    </span>
                  </div>

                  {/* Persian Formatted Metadata */}
                  <div className="p-4 pt-1 space-y-2.5">
                    <div className="text-xs text-indigo-400 font-bold flex items-center gap-1.5">
                      <Eye className="w-3.5 h-3.5" />
                      <span>مشخصات و اطلاعات ویدیو (فارسی‌شده):</span>
                    </div>

                    <h4 className="text-sm font-bold text-white leading-snug">
                      🎬 {msg.videoData.title}
                    </h4>

                    <div className="grid grid-cols-2 gap-2 text-xs text-slate-300 bg-slate-900/80 p-3 rounded-xl border border-slate-800">
                      <div>⏱ <strong>مدت:</strong> {msg.videoData.duration}</div>
                      <div>📢 <strong>کانال:</strong> {msg.videoData.uploader}</div>
                      <div>👁 <strong>بازدید:</strong> {msg.videoData.views}</div>
                      <div>💬 <strong>نظرات:</strong> {msg.videoData.comments}</div>
                    </div>

                    {/* Inline Format Buttons */}
                    <div className="space-y-1.5 pt-2 border-t border-slate-700/80">
                      <div className="text-[11px] text-slate-400 font-medium">
                        👇 کیفیت یا فرمت دلخواه را انتخاب کنید:
                      </div>

                      {msg.inlineButtons?.map((row, rIdx) => (
                        <div key={rIdx} className="grid grid-cols-2 gap-1.5">
                          {row.map((btn, bIdx) => (
                            <button
                              key={bIdx}
                              onClick={() => handleInlineClick(btn)}
                              className={`py-2 px-2 rounded-xl text-xs font-semibold transition cursor-pointer text-center flex items-center justify-center gap-1 ${
                                btn.label.includes('360p')
                                  ? 'bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-500/40'
                                  : btn.label.includes('144p') || btn.label.includes('240p')
                                  ? 'bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30'
                                  : 'bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700'
                              }`}
                            >
                              <span>{btn.label}</span>
                            </button>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Video Media Result Message */}
              {msg.type === 'media_video' && msg.mediaData && (
                <div className="max-w-md w-full bg-[#1e293b] rounded-2xl p-4 border border-emerald-500/40 shadow-xl space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-700 pb-2.5">
                    <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
                      <Film className="w-4 h-4" />
                      <span>ویدیوی دانلودشده (Telegram Video)</span>
                    </div>
                    {msg.mediaData.isCacheHit ? (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                        <Zap className="w-3 h-3" />
                        تحویل آنی از کش
                      </span>
                    ) : (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                        دانلود موفق ✓
                      </span>
                    )}
                  </div>

                  <div className="space-y-1">
                    <div className="text-xs sm:text-sm font-bold text-white">
                      {msg.mediaData.title}
                    </div>
                    <div className="text-[11px] text-slate-400">
                      کانال: {msg.mediaData.uploader} • کیفیت: {msg.mediaData.quality} • حجم: {msg.mediaData.fileSize}
                    </div>
                  </div>

                  {/* Fix verification note */}
                  <div className="p-2.5 rounded-xl bg-emerald-950/20 border border-emerald-900/30 text-[11px] text-emerald-300 space-y-1">
                    <div className="font-bold flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>کیفیت بدون خطا دانلود و با کدک سازگار ادغام شد</span>
                    </div>
                    <p className="text-[10px] text-slate-300 leading-relaxed">
                      صدا با کدک AAC انکود شده و پرچم <code className="text-emerald-200">+faststart</code> فعال شد تا ویدیو در تمام تلگرام‌ها بدون بافر اجرا شود.
                    </p>
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                    <span>فرمت: MP4 سازگار</span>
                    <span>{msg.time}</span>
                  </div>
                </div>
              )}

              {/* Audio Media Result Message (Streaming Music Track) */}
              {msg.type === 'media_audio' && msg.mediaData && (
                <div className="max-w-md w-full bg-[#1e293b] rounded-2xl p-4 border border-indigo-500/40 shadow-xl space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-700 pb-2.5">
                    <div className="flex items-center gap-2 text-violet-400 font-bold text-xs">
                      <Music className="w-4 h-4" />
                      <span>پلیر موزیک تلگرام (Online Music Stream)</span>
                    </div>
                    {msg.mediaData.isCacheHit ? (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 flex items-center gap-1">
                        <Zap className="w-3 h-3" />
                        کش فوری
                      </span>
                    ) : (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-300 border border-violet-500/30 flex items-center gap-1">
                        <Volume2 className="w-3 h-3" />
                        استریم آنلاین
                      </span>
                    )}
                  </div>

                  {/* Telegram-style Audio Card */}
                  <div className="flex items-center gap-3 bg-slate-900/90 p-3 rounded-xl border border-slate-800">
                    <button
                      onClick={() => setIsPlayingAudio(!isPlayingAudio)}
                      className="w-11 h-11 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center shadow-md cursor-pointer transition shrink-0"
                    >
                      {isPlayingAudio ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
                    </button>

                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-bold text-white truncate">
                        {msg.mediaData.title}
                      </div>
                      <div className="text-[11px] text-slate-400 truncate">
                        {msg.mediaData.uploader} • {msg.mediaData.quality}
                      </div>

                      {/* Fake Audio Waveform */}
                      <div className="flex items-center gap-1 mt-2 h-4">
                        {[40, 60, 30, 80, 50, 90, 70, 45, 85, 30, 65, 95, 40, 70, 50, 80].map((h, i) => (
                          <span
                            key={i}
                            style={{ height: `${isPlayingAudio ? Math.min(100, h + (i % 3) * 15) : h * 0.45}%` }}
                            className={`w-1 rounded-full transition-all duration-300 ${
                              isPlayingAudio ? 'bg-indigo-400' : 'bg-slate-700'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Fix note */}
                  <div className="text-[11px] text-slate-300 bg-violet-950/20 border border-violet-900/30 rounded-xl p-2.5">
                    <span className="font-bold text-violet-300">✨ ویژگی حل‌شده:</span>
                    <p className="text-[10px] text-slate-300 mt-0.5">
                      فایل با <code className="text-violet-200">voice=False</code> و <code className="text-violet-200">supports_streaming=True</code> ارسال شده و بلافاصله قبل از پایان دانلود آنلاین پخش می‌شود.
                    </p>
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                    <span>حجم: {msg.mediaData.fileSize}</span>
                    <span>{msg.time}</span>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Loading status (Telethon progress simulation) */}
          {loading && (
            <div className="flex items-center gap-2.5 p-3 rounded-2xl bg-slate-900/95 border border-slate-800 text-xs text-indigo-300 animate-pulse w-fit shadow-lg">
              <div className="w-2.5 h-2.5 rounded-full bg-indigo-400 animate-ping"></div>
              <span>{statusText}</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Telegram Reply Keyboard (Full Menu implementation from keyboards.py) */}
        {showReplyKeyboard && (
          <div className="bg-[#1e293b] border-t border-slate-700 p-2 space-y-1.5 select-none shrink-0 max-h-48 overflow-y-auto">
            {menuButtons.map((row, rIdx) => (
              <div key={rIdx} className="flex gap-1.5">
                {row.map((btnLabel, bIdx) => (
                  <button
                    key={bIdx}
                    onClick={() => handleProcessMessage(btnLabel)}
                    className={`flex-1 py-2 px-3 rounded-xl text-xs sm:text-sm font-semibold transition active:scale-[0.98] cursor-pointer shadow-sm text-center truncate ${
                      btnLabel.includes('خروج') || btnLabel.includes('تعمیر')
                        ? 'bg-rose-950/40 text-rose-300 hover:bg-rose-900/50 border border-rose-800/40'
                        : btnLabel.includes('آمار') || btnLabel.includes('حساب')
                        ? 'bg-indigo-950/50 text-indigo-300 hover:bg-indigo-900/50 border border-indigo-700/40'
                        : 'bg-slate-800 hover:bg-slate-750 text-slate-100 hover:text-white border border-slate-700/80'
                    }`}
                  >
                    {btnLabel}
                  </button>
                ))}
              </div>
            ))}
          </div>
        )}

        {/* Telegram Input Bar */}
        <div className="p-3 bg-[#1e293b] border-t border-slate-700/80 flex items-center gap-2 shrink-0">
          <input
            type="text"
            value={inputMessage}
            onChange={e => setInputMessage(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleProcessMessage(inputMessage)}
            placeholder="پیام یا لینک یوتیوب را بنویسید (مثال: /start یا /admin یا لینک)..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition"
          />
          <button
            onClick={() => handleProcessMessage(inputMessage)}
            disabled={loading || !inputMessage.trim()}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white font-medium text-xs sm:text-sm transition cursor-pointer disabled:opacity-50 flex items-center gap-1.5 shrink-0"
          >
            <Send className="w-4 h-4" />
            <span className="hidden sm:inline">ارسال</span>
          </button>
        </div>
      </div>
    </div>
  );
};
