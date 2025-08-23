import requests
from hafez_fortunes import hafez_fortunes
from telegram.ext import MessageHandler, filters
import os
from dotenv import load_dotenv
import random
from collections import defaultdict
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import math, time, random, asyncio
from collections import defaultdict


# تنظیمات
load_dotenv()
TOKEN = os.getenv("BOT_AMG") 
ADMIN_IDS = 6807376124
ADMIN_ID = {6807376124}  # ادمین اصلی (ست اول)
OPENROUTER_API_KEY = "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"


# کانال‌های اسپانسر
SPONSORED_CHANNELS = [
    "@starssell_ir",
    "@amg_chanel_ir"
]


# کاربران خاص
special_users = {
    6807376124: "💎 سلام آدریانو! به منطقه ویژه خودت خوش اومدی.",
    1296533127: "🎤 به به سلام عباس نفسم یه دست برامون بخون",
    5692880940: "👧🏻 عه سلام هلی کوشولو چی میخوای بهم بگی؟",
    6543935749: "🔥 سلام به به چه کون طلایی چی‌ میخوای بهم بگی؟",
    5880712187: "🕌 عه سلام مساجد چی میخوای بهم بگی؟",
    7506391284: "✅ این اومده یعنی درسته نگران نباش"
}

group_stats = defaultdict(lambda: {
    "messages": defaultdict(int),        # user_id: تعداد پیام‌ها
    "links": 0,
    "replies": 0,
    "last_day": datetime.now().date()
})



invite_count = defaultdict(int)  # user_id: تعداد دعوت‌شده‌ها
referrer_map = {}  # user_id: معرف چه کسی بوده
user_data = {} 
vip_users = set()
anti_link_groups = set()
proxy_list = []
user_scores = defaultdict(int)  # user_id: total_score
user_ids = set()
banned_users = set()
tickets = {}  # user_id: {"status": str, "messages": list}
subscribed_users = set()
# دیکشنری برای نگهداری وضعیت بازی هر کاربر
user_games = {}
rps_games = {}  # user_id : {"playing": bool}

# تنظیمات XP
XP_PER_MESSAGE_MIN = 10
XP_PER_MESSAGE_MAX = 15
MIN_XP_INTERVAL = 30  # فاصله مجاز بین کسب XP (ثانیه)
# دیتای موقت
user_xp = defaultdict(lambda: {"xp": 0, "level": 1, "last_ts": 0})
xp_lock = asyncio.Lock()

def compute_level_from_xp(xp: int) -> int:
    return int(math.sqrt(xp / 100)) + 1

# --- صفحات راهنما (فارسی و انگلیسی) ---

help_pages = {
    "fa": [
        "📖 *راهنمای ربات AMG — نسخه ۲۰۲۵ (صفحه ۱)*\n\n"
        "⚡ امکانات عمومی:\n"
        "💬 چت مستقیم با ادمین (AMG)\n"
        "🤖 دستیار هوش مصنوعی (GPT-3.5 — فقط برای VIP)\n"
        "📜 فال حافظ با تعبیر کامل\n"
        "🎮 بازی‌ها:\n ├ 🎯 حدس عدد (محدود/نامحدود)\n └ ✂️ سنگ‌کاغذ‌قیچی (امتیازی)\n\n"
        "📝 دستورها:\n/start — شروع ربات\n/ask <سوال> — پرسیدن از AI\n/start_game — شروع بازی حدس عدد\n/exit_game — خروج از بازی\n/rps — سنگ‌کاغذ‌قیچی",

        "📖 *راهنمای ربات AMG — نسخه ۲۰۲۵ (صفحه ۲)*\n\n"
        "🛡️ امکانات گروهی:\n"
        "🛡️ ضد لینک هوشمند (فعال/غیرفعال)\n"
        "👋 خوشامدگویی خودکار\n"
        "📢 سفارش تبلیغ\n"
        "🌐 اشتراک پروکسی (ادمین فقط)\n\n"
        "📝 دستورها:\n'ضد لینک روشن/خاموش' — مدیریت ضد لینک\nپنل ربات — نمایش پنل گروهی\n/addproxy <proxy> — افزودن پروکسی\n/removeproxy — حذف پروکسی‌ها",

        "📖 *راهنمای ربات AMG — نسخه ۲۰۲۵ (صفحه ۳)*\n\n"
        "🎉 سیستم کاربری:\n"
        "🆘 پشتیبانی و تیکت\n"
        "📊 پروفایل کاربر (/profile)\n"
        "🎯 سیستم XP و Level در گروه‌ها\n"
        "🎉 VIP با دعوت ۳ نفر\n"
        "🏆 جدول برترین‌ها (/top)\n\n"
        "📝 دستورها:\n/vipme — وضعیت VIP\n/users — لیست کاربران\n/rank — مشاهده سطح و XP\n/tickets — لیست تیکت‌ها (ادمین)",

        "📖 *راهنمای ربات AMG — نسخه ۲۰۲۵ (صفحه ۴)*\n\n"
        "👑 امکانات ادمین‌ها:\n"
        "🔨 بن/آن‌بن کاربران\n"
        "📢 پیام همگانی\n"
        "👑 مدیریت ادمین‌ها (افزودن/حذف)\n"
        "📋 مدیریت کانال‌های اسپانسر\n"
        "🌐 مدیریت پروکسی‌ها\n"
        "🎉 مدیریت VIP\n"
        "✨ پیام ویژه برای کاربران خاص\n\n"
        "📝 دستورها:\n/adminpanel — پنل ادمین\n/addadmin <id>\n/removeadmin <id>\n/addchannel <@channel>\n/removechannel <@channel>\n/vipadd <id>\n/vipremove <id>"
    ],

    "en": [
        "📖 *AMG Bot Guide — 2025 Edition (Page 1)*\n\n"
        "⚡ General Features:\n"
        "💬 Direct chat with Admin (AMG)\n"
        "🤖 AI Assistant (GPT-3.5 — VIP only)\n"
        "📜 Hafez Fortune Telling\n"
        "🎮 Games:\n ├ 🎯 Number Guessing (Limited/Unlimited)\n └ ✂️ Rock-Paper-Scissors (with scores)\n\n"
        "📝 Commands:\n/start — Start bot\n/ask <question> — Ask AI\n/start_game — Start Number Guessing\n/exit_game — Exit game\n/rps — Rock-Paper-Scissors",

        "📖 *AMG Bot Guide — 2025 Edition (Page 2)*\n\n"
        "🛡️ Group Tools:\n"
        "🛡️ Smart Anti-Link (enable/disable)\n"
        "👋 Auto Welcome Messages\n"
        "📢 Ad Requests\n"
        "🌐 Proxy Sharing (admin only)\n\n"
        "📝 Commands:\nضد لینک روشن / خاموش — Manage Anti-Link\nپنل ربات — Show Group Panel\n/addproxy <proxy> — Add proxy\n/removeproxy — Remove proxies",

        "📖 *AMG Bot Guide — 2025 Edition (Page 3)*\n\n"
        "🎉 User System:\n"
        "🆘 Support & Ticketing\n"
        "📊 User Profile (/profile)\n"
        "🎯 XP & Level system in groups\n"
        "🎉 VIP System (Invite 3 users = AI Access)\n"
        "🏆 Leaderboard (/top)\n\n"
        "📝 Commands:\n/vipme — Check VIP\n/users — List users\n/rank — Show XP & Level\n/tickets — Tickets list (admin)",

        "📖 *AMG Bot Guide — 2025 Edition (Page 4)*\n\n"
        "👑 Admin Tools:\n"
        "🔨 Ban & Unban users\n"
        "📢 Broadcast messages\n"
        "👑 Manage Admins (add/remove)\n"
        "📋 Manage Sponsor Channels\n"
        "🌐 Manage Proxies\n"
        "🎉 Manage VIPs\n"
        "✨ Add/Remove Special Messages\n\n"
        "📝 Commands:\n/adminpanel — Admin Panel\n/addadmin <id>\n/removeadmin <id>\n/addchannel <@channel>\n/removechannel <@channel>\n/vipadd <id>\n/vipremove <id>"
    ]
}


# --- استارت و منوی اصلی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_ids.add(user_id)
    
    if update.message.text and update.message.text.startswith("/start ref_"):
        try:
            ref_id = int(update.message.text.split("ref_")[1])
            user_id = update.effective_user.id
    
            if ref_id != user_id and user_id not in referrer_map:
                invite_count[ref_id] += 1
                referrer_map[user_id] = ref_id
            
                if invite_count[ref_id] >= 3:
                    vip_users.add(ref_id)
                    await context.bot.send_message(ref_id, "🎉 تبریک! با دعوت ۳ نفر، دسترسی VIP گرفتی!")


        except:
            pass

    # ثبت اولین ورود
    if user_id not in user_data:
        user_data[user_id] = {
            "join_date": datetime.now().strftime("%Y-%m-%d"),
            "ai_uses": 0
        }

    if update.message.chat.type == "private":
        reply_keyboard = ReplyKeyboardMarkup([
            ["🤖 چت هوش مصنوعی", "💬 چت با AMG"],
            ["🌐 دریافت پروکسی", "📢 سفارش تبلیغ"],
            ["➕ افزودن به گروه", "🆘 پشتیبانی"],
            ["ℹ️ درباره ربات", "📖 راهنما"]
        ], resize_keyboard=True)
    else:
        reply_keyboard = None  # توی گروه کیبورد نمی‌خوایم


    if not await check_channel_membership(user_id, context):
        inline_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تایید عضویت", callback_data="check_subscription")]
        ])
        channel_list = "\n".join([f"📢 {channel}" for channel in SPONSORED_CHANNELS])
        await update.message.reply_text(
            f"⚠️ برای استفاده از هوش مصنوعی و امکانات ربات، لطفاً ابتدا عضو کانال‌های زیر شو و بعد دکمه زیر رو بزن:\n\n{channel_list}",
            reply_markup=inline_keyboard
        )
    else:
        if user_id in vip_users:
            await update.message.reply_text("❓ برای پرسیدن سوال از هوش مصنوعی، از دستور `/ask سوالت` استفاده کن.")
        else:
            await update.message.reply_text(
                "📌 برای استفاده از چت هوش مصنوعی، باید ۳ نفر رو با لینک اختصاصی خودت به ربات دعوت کنی:\n"
                f"https://t.me/{context.bot.username}?start=ref_{user_id}"
            )
        if reply_keyboard:
            await update.message.reply_text("👋 سلام! یکی از گزینه‌ها یا دستورها را انتخاب کن.", reply_markup=reply_keyboard)
        else:
            await update.message.reply_text("👋 سلام! برای استفاده از منو، به چت خصوصی ربات بیا.")

# --- چک کردن عضویت در کانال‌ها ---

async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    for channel in SPONSORED_CHANNELS:
        try:
            chat_member = await context.bot.get_chat_member(channel, user_id)
            if chat_member.status not in [ChatMember.MEMBER, ChatMember.OWNER, ChatMember.ADMINISTRATOR]:
                return False
        except Exception:
            # خطا در گرفتن اطلاعات یعنی احتمالا عضو نیست یا دسترسی نیست، پس کانال رو رد کن
            return False
    return True


# --- دکمه‌های inline ---

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "enable_anti_link":
        chat = query.message.chat
        if chat.type in ["supergroup", "group"]:
            anti_link_groups.add(chat.id)
            await query.edit_message_text("🛡️ ضد لینک در این گروه فعال شد.")
        else:
            await query.edit_message_text("⚠️ فقط تو گروه می‌تونی ضد لینک فعال کنی.")

    elif query.data == "chat_amg":
        if user_id in special_users:
            await query.message.reply_text(special_users[user_id])
        else:
            await query.message.reply_text("📨 پیام‌تو بنویس، AMG جواب می‌ده.")
    
    elif query.data == "bot_info":
        await query.message.reply_text(
            "ℹ️ اطلاعات ربات:\n\n"
            "🤖 نام: 𓄂AMG𓆃\n"
            "✨ قابلیت‌ها:\n"
            " ├─ 💬 چت مستقیم با ادمین (AMG) + پاسخ ریپلای\n"
            " ├─ 🧠 دستیار هوش مصنوعی GPT-3.5 (VIP only)\n"
            " ├─ 🛡️ سیستم ضد لینک هوشمند گروهی\n"
            " ├─ 👋 خوش‌آمدگویی خودکار\n"
            " ├─ 🌐 اشتراک پروکسی‌ها (مدیریت توسط ادمین)\n"
            " ├─ 📜 فال حافظ با تعبیر کامل\n"
            " ├─ 🎮 بازی‌ها (حدس عدد + سنگ‌کاغذ‌قیچی)\n"
            " ├─ 🆘 سیستم تیکتینگ و پشتیبانی حرفه‌ای\n"
            " └─ 🎯 سیستم XP و Level + VIP با دعوت\n\n"
            "👤 سازنده: @AMG_ir\n"
            "🧠 مدل AI: OpenRouter - GPT-3.5-Turbo\n"
            "🔖 نسخه: v3.5.0-AR\n"
            "📅 تاریخ: ۲۰۲۵/۰۸/۲۳"
        )


    elif query.data == "support":
        await query.message.reply_text("🆘 درخواست پشتیبانی شما ثبت شد. لطفاً سوال یا مشکل خود را ارسال کنید.")
        tickets[user_id] = "درخواست پشتیبانی ثبت شده"
        context.user_data["chat_support"] = True

    elif query.data == "check_subscription":
        if await check_channel_membership(user_id, context):
            subscribed_users.add(user_id)
            await query.message.reply_text("✅ عضویت شما تایید شد، ممنون که عضو هستی! اکنون می‌تونی از همه امکانات استفاده کنی.")
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
            # ارسال منوی اصلی
            reply_keyboard = ReplyKeyboardMarkup([
                ["➕ افزودن به گروه", "🆘 درخواست پشتیبانی"],
                ["💬 چت با AMG"],
                ["📢 سفارش تبلیغ"],
                ["🌐 دریافت پروکسی"],
                ["🤖 چت با هوش مصنوعی"],
                ["ℹ️ اطلاعات ربات"]
            ], resize_keyboard=True)
            await context.bot.send_message(chat_id=user_id, text="👋 سلام! یکی از گزینه‌ها یا دستورها را انتخاب کن.", reply_markup=reply_keyboard)
        else:
            await query.message.reply_text("⚠️ هنوز عضو همه کانال‌ها نیستی، لطفاً عضو شو و دوباره تایید کن.")

    elif query.data == "get_proxy":
        if proxy_list:
            proxies = "\n".join(proxy_list[-5:])
            await query.message.reply_text(f"🌐 پروکسی‌های جدید:\n\n{proxies}")
        else:
            await query.message.reply_text("⚠️ هنوز پروکسی‌ای ثبت نشده.")

# --- مدیریت پیام‌ها از کاربران و گروه‌ها ---

async def handle_user_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    handled = False

    # سیستم XP فقط در گروه
    if update.effective_chat.type in ["group", "supergroup"] and not update.effective_user.is_bot:
        xp_total, leveled, new_level = await add_xp(user_id)
        if leveled:
            await update.message.reply_text(
                f"🎉 {update.effective_user.first_name} به لِول {new_level} رسید!"
            )

    
    if user_id in banned_users:
        return

    # واکنش به کلمه‌های AMG و امگ تو گروه با جملات رندم
    if update.message.chat.type in ["group", "supergroup"]:
        low_text = text.lower()
        if any(word in low_text for word in ["amg", "امگ"]):
            responses = [
                "💬 سلام رفیق، چی می‌خوای بگی؟",
                "🤖 امگ همیشه اینجاست!",
                "🔥 AMG، بهترین ربات!",
                "⚡️ حالا چی شده؟",
                "میخاری هی صدام میکنی؟"
            ]
            await update.message.reply_text(random.choice(responses))
            return

    # --- ارسال فال حافظ با تعبیر ---
    # --- فال حافظ ---
    if update.message.chat.type in ["group", "supergroup"]:
        if "فال" in text or "فال حافظ" in text:
            fortune = random.choice(hafez_fortunes)
            await update.message.reply_text(
                f"📜 فال حافظ برای {update.effective_user.first_name}:\n\n"
                f"{fortune['verse']}\n\n📖 تعبیر:\n{fortune['meaning']}"
            )
            return


    
    # پنل شیشه‌ای گروهی با دکمه‌ها وقتی «پنل ربات» گفته بشه
    if update.message.chat.type in ["group", "supergroup"]:
        # --- واکنش به ریپلای به پیام ربات ---
        if update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
            replies = [
                "با من چیکار داری؟ 😐",
                "به من دست نزن، من حساسام! 😅",
                "برو پی کارت رفیق!",
                "من ماشینم ولی دل دارم 🥲",
                "عههه من که کاری نکردم 😕",
                "ای بابا چرا هی به من ریپلای میدی؟",
                "خب؟ چی شده حالا؟ 🙃"
            ]
            await update.message.reply_text(random.choice(replies))
            return
            
        if text == "پنل ربات":
            keyboard = InlineKeyboardMarkup([
                # 🔐 مدیریت گروه
                [
                    InlineKeyboardButton("🚫 فعال‌سازی ضد لینک", callback_data="enable_anti_link"),
                    InlineKeyboardButton("✅ غیرفعال‌سازی ضد لینک", callback_data="disable_anti_link")
                ],
                [
                    InlineKeyboardButton("👋 تنظیم خوشامد", callback_data="set_welcome"),
                    InlineKeyboardButton("❌ حذف خوشامد", callback_data="del_welcome")
                ],
        
                # 🌐 امکانات عمومی
                [
                    InlineKeyboardButton("🔑 دریافت پروکسی", callback_data="get_proxy"),
                    InlineKeyboardButton("📢 سفارش تبلیغ", callback_data="advertise")
                ],
                [
                    InlineKeyboardButton("ℹ️ اطلاعات ربات", callback_data="bot_info"),
                    InlineKeyboardButton("📞 پشتیبانی", callback_data="support")
                ],
        
                # 🤖 سرگرمی و هوش مصنوعی
                [
                    InlineKeyboardButton("🤖 چت هوش مصنوعی", callback_data="chat_ai"),
                    InlineKeyboardButton("📜 فال حافظ", callback_data="hafez")
                ],
                [
                    InlineKeyboardButton("🎮 بازی حدس عدد", callback_data="start_game"),
                    InlineKeyboardButton("🏆 جدول برترین‌ها", callback_data="top")
                ],
        
                # 👤 کاربری
                [
                    InlineKeyboardButton("👤 پروفایل من", callback_data="profile"),
                    InlineKeyboardButton("🎉 وضعیت VIP", callback_data="vipme")
                ]
            ])
            await update.message.reply_text(
                "🎛️ *پنل گروهی AMG*\n\nاز دکمه‌های زیر برای مدیریت و استفاده از امکانات ربات استفاده کنید:",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
            return



    # --- دکمه‌های منوی اصلی ---
    if "چت با AMG" in text:
        if user_id in special_users:
            await update.message.reply_text(special_users[user_id])
        else:
            await update.message.reply_text("📨 پیام‌تو برای AMG بنویس.")
        context.user_data['chat_amg'] = True
        return

    elif "راهنما" in text:
        await show_help_menu(update, context)
        return

    # نمایش پروفایل وقتی کاربر تایپ کند "پروفایل من"
    elif text.strip() in ["پروفایل من", "پروفایل", "/profile"]:
        await show_profile(update, context)
        return

    
    elif "سفارش تبلیغ" in text:
        await update.message.reply_text("✍️ لطفاً نوع تبلیغ و توضیحاتت رو کامل بفرست.")
        context.user_data["chat_ad"] = True
        return
    
    elif "دریافت پروکسی" in text:
        if proxy_list:
            proxies = "\n".join(proxy_list[-5:])
            await update.message.reply_text(f"🌐 پروکسی‌های جدید:\n\n{proxies}")
        else:
            await update.message.reply_text("⚠️ هنوز پروکسی‌ای ثبت نشده.")
        return
    
    elif "چت هوش مصنوعی" in text:
        if not await check_channel_membership(user_id, context):
            await update.message.reply_text("⚠️ برای استفاده از هوش مصنوعی، باید عضو کانال‌های اسپانسر بشی:\n" +
                                            "\n".join([f"📢 {channel}" for channel in SPONSORED_CHANNELS]))
        elif user_id not in vip_users:
            await update.message.reply_text("🛑 برای استفاده از هوش مصنوعی، باید ۳ نفر رو با لینک اختصاصی خودت به ربات دعوت کنی.\n\n"
                                            f"📎 لینک دعوتت:\nhttps://t.me/{context.bot.username}?start=ref_{user_id}")
        else:
            await update.message.reply_text("❓ سوالت رو با دستور `/ask سوالت` بپرس.")
        return

    
    elif "درباره ربات" in text or "اطلاعات ربات" in text:
        await update.message.reply_text(
            "ℹ️ اطلاعات ربات:\n\n"
            "🤖 نام: 𓄂AMG𓆃\n"
            "✨ قابلیت‌ها:\n"
            " ├─ 💬 چت مستقیم با ادمین (AMG) + پاسخ ریپلای\n"
            " ├─ 🧠 دستیار هوش مصنوعی GPT-3.5 (VIP only)\n"
            " ├─ 🛡️ سیستم ضد لینک هوشمند گروهی\n"
            " ├─ 👋 خوش‌آمدگویی خودکار\n"
            " ├─ 🌐 اشتراک پروکسی‌ها (مدیریت توسط ادمین)\n"
            " ├─ 📜 فال حافظ با تعبیر کامل\n"
            " ├─ 🎮 بازی‌ها (حدس عدد + سنگ‌کاغذ‌قیچی)\n"
            " ├─ 🆘 سیستم تیکتینگ و پشتیبانی حرفه‌ای\n"
            " └─ 🎯 سیستم XP و Level + VIP با دعوت\n\n"
            "👤 سازنده: @AMG_ir\n"
            "🧠 مدل AI: OpenRouter - GPT-3.5-Turbo\n"
            "🔖 نسخه: v3.5.0-AR\n"
            "📅 تاریخ: ۲۰۲۵/۰۸/۲۳"
        )
        return

    
    elif "پشتیبانی" in text:
        tickets[user_id] = {"status": "🟡 در انتظار پاسخ", "messages": []}
        await update.message.reply_text("🆘 تیکت شما باز شد. لطفاً سوال یا مشکل خود را بنویسید.")
        context.user_data["chat_support"] = True  
        return


    
    elif "افزودن به گروه" in text:
        await update.message.reply_text("📎 برای افزودن من به گروه، روی لینک زیر بزن و منو ادمین کن:\n"
                                        "https://t.me/AMG_ir_BOT?startgroup=true")
        return

    
    elif context.user_data.get('chat_amg'):
        user_name = update.effective_user.full_name
        user_id = update.effective_user.id
        caption = f"📩 پیام از {user_name} ({user_id}):"
    
        # ارسال بر اساس نوع پیام
        if update.message.text:
            msg = await context.bot.send_message(ADMIN_IDS, f"{caption}\n\n{update.message.text}")
            context.bot_data[f"reply_to:{msg.message_id}"] = user_id
    
        elif update.message.photo:
            msg = await context.bot.send_photo(ADMIN_IDS, photo=update.message.photo[-1].file_id, caption=caption)
            context.bot_data[f"reply_to:{msg.message_id}"] = user_id
    
        elif update.message.video:
            msg = await context.bot.send_video(ADMIN_IDS, video=update.message.video.file_id, caption=caption)
            context.bot_data[f"reply_to:{msg.message_id}"] = user_id
    
        elif update.message.voice:
            msg = await context.bot.send_voice(ADMIN_IDS, voice=update.message.voice.file_id, caption=caption)
            context.bot_data[f"reply_to:{msg.message_id}"] = user_id
    
        elif update.message.sticker:
            msg = await context.bot.send_sticker(ADMIN_IDS, sticker=update.message.sticker.file_id)
            context.bot_data[f"reply_to:{msg.message_id}"] = user_id
    
        elif update.message.document:
            msg = await context.bot.send_document(ADMIN_IDS, document=update.message.document.file_id, caption=caption)
            context.bot_data[f"reply_to:{msg.message_id}"] = user_id
    
        elif update.message.animation:
            msg = await context.bot.send_animation(ADMIN_IDS, animation=update.message.animation.file_id, caption=caption)
            context.bot_data[f"reply_to:{msg.message_id}"] = user_id
    
        else:
            msg = await context.bot.send_message(ADMIN_IDS, f"{caption}\n\n[پیام ناشناخته‌ای ارسال شد]")
            context.bot_data[f"reply_to:{msg.message_id}"] = user_id
    
        await update.message.reply_text("📨 پیام شما برای AMG ارسال شد. منتظر پاسخ باشید.")
        context.user_data['chat_amg'] = False
        handled = True

    elif context.user_data.get('chat_support'):
        user_name = update.effective_user.full_name
        caption = f"📨 پشتیبانی از {user_name} ({user_id}):"

        if user_id in tickets:
            tickets[user_id]["messages"].append(update.message.text or "[Media]")
            tickets[user_id]["status"] = "🟠 در حال بررسی"

    
        if update.message.text:
            await context.bot.send_message(ADMIN_IDS, f"{caption}\n\n{update.message.text}")
        elif update.message.photo:
            await context.bot.send_photo(ADMIN_IDS, photo=update.message.photo[-1].file_id, caption=caption)
        elif update.message.video:
            await context.bot.send_video(ADMIN_IDS, video=update.message.video.file_id, caption=caption)
        elif update.message.voice:
            await context.bot.send_voice(ADMIN_IDS, voice=update.message.voice.file_id, caption=caption)
        elif update.message.sticker:
            await context.bot.send_sticker(ADMIN_IDS, sticker=update.message.sticker.file_id)
        elif update.message.document:
            await context.bot.send_document(ADMIN_IDS, document=update.message.document.file_id, caption=caption)
        elif update.message.animation:
            await context.bot.send_animation(ADMIN_IDS, animation=update.message.animation.file_id, caption=caption)
        else:
            await context.bot.send_message(ADMIN_IDS, f"{caption}\n\n[پیام ناشناخته‌ای ارسال شد]")
    
        await update.message.reply_text("📨 پیام شما برای پشتیبانی ارسال شد. منتظر پاسخ باشید.")
        context.user_data['chat_support'] = False  # ⛔ ریست کن که دوباره نیاد
        handled = True


    elif context.user_data.get("chat_ad"):
        user_name = update.effective_user.full_name
        user_id = update.effective_user.id
        caption = f"📢 سفارش تبلیغ از {user_name} ({user_id}):"
    
        if update.message.text:
            await context.bot.send_message(ADMIN_IDS, f"{caption}\n\n{update.message.text}")
        elif update.message.document:
            await context.bot.send_document(ADMIN_IDS, document=update.message.document.file_id, caption=caption)
        elif update.message.photo:
            await context.bot.send_photo(ADMIN_IDS, photo=update.message.photo[-1].file_id, caption=caption)
        elif update.message.video:
            await context.bot.send_video(ADMIN_IDS, video=update.message.video.file_id, caption=caption)
        elif update.message.voice:
            await context.bot.send_voice(ADMIN_IDS, voice=update.message.voice.file_id, caption=caption)
        elif update.message.animation:
            await context.bot.send_animation(ADMIN_IDS, animation=update.message.animation.file_id, caption=caption)
        else:
            await context.bot.send_message(ADMIN_IDS, f"{caption}\n\n[پیام نامشخصی دریافت شد]")
    
        await update.message.reply_text("📨 سفارش تبلیغ شما ارسال شد. منتظر پاسخ ادمین باشید.")
        context.user_data["chat_ad"] = False
        handled = True



    

    # فعال‌سازی ضد لینک با پیام متنی
    if update.message.chat.type in ["group", "supergroup"]:
        if text.strip() in ["ضد لینک روشن", "/ضدلینک روشن"]:
            member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
            if member.status not in ["administrator", "creator"]:
                await update.message.reply_text("⚠️ فقط ادمین‌ها می‌تونن ضد لینک رو فعال کنن.")
                return
            anti_link_groups.add(update.effective_chat.id)
            print("✅ ضد لینک برای گروه فعال شد:", update.effective_chat.id)

            await update.message.reply_text("✅ ضد لینک برای این گروه فعال شد.")
            return
    
        if text.strip() in ["ضد لینک خاموش", "/ضدلینک خاموش"]:
            member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
            if member.status not in ["administrator", "creator"]:
                await update.message.reply_text("⚠️ فقط ادمین‌ها می‌تونن ضد لینک رو خاموش کنن.")
                return
            if update.message.chat_id in anti_link_groups:
                anti_link_groups.remove(update.message.chat_id)
                await update.message.reply_text("❌ ضد لینک برای این گروه خاموش شد.")
            else:
                await update.message.reply_text("ℹ️ ضد لینک قبلاً در این گروه غیرفعال بوده.")
            return


     # --- منطق بازی ---
    if context.user_data.get("game_state") == "awaiting_limit":
        try:
            limit = int(text)
            user_games[user_id]["guess_limit"] = limit
            context.user_data["game_state"] = "playing"
            start_range, end_range = user_games[user_id]["range"]
            await update.message.reply_text(
                f"✅ نسخه محدود انتخاب شد! شما {limit} حدس دارید. "
                f"حالا یک عدد بین {start_range} تا {end_range} حدس بزنید."
            )
        except ValueError:
            await update.message.reply_text("⚠️ لطفاً یک عدد صحیح وارد کنید.")
        return

    elif context.user_data.get("game_state") == "playing":
        try:
            guess = int(text)
        except ValueError:
            await update.message.reply_text("⚠️ لطفاً یک عدد صحیح وارد کنید.")
            return

        game_data = user_games[user_id]
        game_data["attempts"] += 1

        if guess == game_data["number"]:
            await update.message.reply_text(f"🎉 تبریک! عدد صحیح رو حدس زدی! امتیاز نهایی: {game_data['score']}")
            user_scores[user_id] += game_data["score"]  # ذخیره امتیاز کاربر
            game_data["playing"] = False
            context.user_data["game_state"] = None
            return
        elif guess < game_data["number"]:
            await update.message.reply_text("🔼 عدد بزرگتر از این است!")
        else:
            await update.message.reply_text("🔽 عدد کوچکتر از این است!")

        game_data["score"] -= 10

        if game_data["attempts"] >= game_data["guess_limit"]:
            await update.message.reply_text(f"🚫 بازی تموم شد! عدد صحیح: {game_data['number']}. امتیاز نهایی: {game_data['score']}")
            user_scores[user_id] += max(game_data["score"], 0)  # امتیاز منفی صفر حساب بشه
            game_data["playing"] = False
            context.user_data["game_state"] = None
            return
        return
   
    
# فقط اگر کاربر در حالت خاصی نیست
    if (
        update.message.chat.type == "private" and
        not context.user_data.get("chat_amg") and
        not context.user_data.get("chat_support") and
        not context.user_data.get("chat_ad") and
        not handled
        
    ):
        await update.message.reply_text("❓ پیام شما نامفهوم بود. لطفاً یکی از گزینه‌های منو رو انتخاب کن.")
 # در گروه‌ها پاسخ نده



# --- دستور ادمین: افزودن پروکسی ---

async def add_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما اجازه ندارید این کار را انجام دهید.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ لطفاً پروکسی را بعد از دستور وارد کنید.")
        return
    proxy = " ".join(args)
    proxy_list.append(proxy)
    await update.message.reply_text(f"✅ پروکسی جدید اضافه شد:\n{proxy}")

# --- دستور ادمین: ارسال پیام همگانی ---

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما اجازه ندارید این کار را انجام دهید.")
        return
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("⚠️ لطفاً پیام برای ارسال همگانی را وارد کنید.")
        return
    count = 0
    for uid in user_ids:
        try:
            await context.bot.send_message(uid, message)
            count += 1
        except:
            pass
    await update.message.reply_text(f"✅ پیام به {count} کاربر ارسال شد.")

# --- دستور ادمین: پنل مدیریت ---

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ فقط ادمین می‌تواند این پنل را ببیند.")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔨 بن کردن کاربر", callback_data="ban_user")],
        [InlineKeyboardButton("♻️ آنبن کردن کاربر", callback_data="unban_user")],
        [InlineKeyboardButton("📊 آمار ربات", callback_data="bot_stats")]
    ])
    await update.message.reply_text("🛠️ پنل مدیریت:", reply_markup=keyboard)

# --- هندل کردن callback برای بن و آنبن و آمار ---

async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    if user_id not in ADMIN_ID:

        await query.edit_message_text("❌ فقط ادمین می‌تواند از این قسمت استفاده کند.")
        return

    if query.data == "ban_user":
        await query.edit_message_text("👤 لطفاً آیدی عددی کاربر مورد نظر برای بن را ارسال کنید.")
        context.user_data['action'] = 'ban'

    elif query.data == "unban_user":
        await query.edit_message_text("👤 لطفاً آیدی عددی کاربر مورد نظر برای آنبن را ارسال کنید.")
        context.user_data['action'] = 'unban'

    elif query.data == "bot_stats":
        await query.edit_message_text(
            f"📊 آمار ربات:\n\n"
            f"👥 تعداد کل کاربران: {len(user_ids)}\n"
            f"⛔️ تعداد کاربران بن شده: {len(banned_users)}\n"
            f"👑 ادمین: {ADMIN_ID}"
        )

async def admin_action_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        return

    action = context.user_data.get('action')
    if not action:
        return

    target_id_text = update.message.text
    if not target_id_text.isdigit():
        await update.message.reply_text("⚠️ لطفاً فقط آیدی عددی ارسال کنید.")
        return

    target_id = int(target_id_text)

    if action == 'ban':
        banned_users.add(target_id)
        await update.message.reply_text(f"⛔️ کاربر با آیدی {target_id} بن شد.")
    elif action == 'unban':
        banned_users.discard(target_id)
        await update.message.reply_text(f"✅ کاربر با آیدی {target_id} آنبن شد.")

    context.user_data['action'] = None

# --- دستور چت با هوش مصنوعی ---

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in vip_users:
        await update.message.reply_text(
            "🛑 برای استفاده از هوش مصنوعی، باید ۳ نفر رو با لینک اختصاصی خودت به ربات دعوت کنی.\n\n"
            "لینک دعوتت:\n"
            f"https://t.me/{context.bot.username}?start=ref_{user_id}"
        )
        return

    if not await check_channel_membership(user_id, context):
        await update.message.reply_text("⚠️ لطفاً ابتدا عضو کانال‌های اسپانسر شوید.")
        return
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text("⚠️ لطفاً سوال خود را بعد از دستور وارد کنید.")
        return

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": question}]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response_json = response.json()
        print("🔍 Response JSON:", response_json)
        answer = response_json['choices'][0]['message']['content']
# افزایش شمارنده چت‌های AI
        if user_id in user_data:
            user_data[user_id]["ai_uses"] += 1
        await update.message.reply_text(f"🧠 پاسخ AMG:\n\n{answer}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارتباط با هوش مصنوعی:\n{e}")

# --- حذف منوی ویژه و اضافه کردن گزینه‌های درخواست پشتیبانی و افزودن به گروه در منوی پایین ---

# (اینکار در منوی start انجام شده)

# --- ضد لینک ---

async def anti_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📨 پیام:", update.message.text)
    if update.effective_chat.id not in anti_link_groups:
        return

    text = update.message.text or ""
    has_link = False

    # بررسی لینک‌های آشکار در متن
    link_keywords = ["http://", "https://", "t.me/", "telegram.me/"]
    if any(keyword in text.lower() for keyword in link_keywords):
        has_link = True

    if update.message.entities:
        for entity in update.message.entities:
            if entity.type in ["url", "text_link"]:
                has_link = True
                break

    
    if has_link:
        print("🧨 لینک شناسایی شد")
        await update.message.delete()
        await update.message.reply_text(f"⚠️ ارسال لینک در این گروه ممنوعه، {update.effective_user.first_name}!")



async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        return
    if not user_ids:
        await update.message.reply_text("👥 هیچ کاربری هنوز ربات رو استفاده نکرده.")
        return
    user_list = "\n".join([f"👤 {uid}" for uid in user_ids])
    await update.message.reply_text(f"📄 لیست کاربران:\n\n{user_list}")



def format_progress_bar(current: int, goal: int, length: int = 20) -> str:
    if goal <= 0:
        return "[" + "░" * length + "]"
    ratio = min(max(current / goal, 0.0), 1.0)
    filled = int(ratio * length)
    return "█" * filled + "░" * (length - filled)


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # داده‌های پایه
    profile = user_data.get(user_id, {"join_date": "—", "ai_uses": 0})
    xp_info = user_xp.get(user_id, {"xp": 0, "level": 1})
    xp = xp_info.get("xp", 0)
    level = xp_info.get("level", 1)

    # محاسبه برای رسیدن به لِول بعدی
    next_level = level + 1
    next_level_xp = 100 * (next_level ** 2)
    xp_needed = max(next_level_xp - xp, 0)

    # نوار پیشرفت
    bar = format_progress_bar(xp, next_level_xp, length=20)

    # دعوت‌ها و وضعیت VIP
    invites = invite_count.get(user_id, 0)
    is_vip = user_id in vip_users
    vip_text = "✅ شما VIP هستید — دسترسی به AI فعال است." if is_vip else "❌ شما VIP نیستید — ۳ دعوت لازم است."

    join_date = profile.get("join_date", "—")
    ai_uses = profile.get("ai_uses", 0)

    # متن زیبا
    text = (
        f"👤 <b>{user.full_name}</b>\n"
        f"🆔 <code>{user_id}</code>\n\n"
        f"🎯 <b>سطح</b>: {level}    ⭐ <b>XP</b>: {xp}\n"
        f"{bar}\n"
        f"⏳ تا سطح {next_level}: {xp_needed} XP\n\n"
        f"👥 <b>تعداد دعوت‌ها</b>: {invites}\n"
        f"👑 <b>وضعیت VIP</b>: {vip_text}\n\n"
        f"📅 تاریخ عضویت: {join_date}\n"
        f"🧠 دفعات استفاده از AI: {ai_uses}\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ دعوت کن (لینک اختصاصی)", url=f"https://t.me/{context.bot.username}?start=ref_{user_id}")]
    ])

    if update.message:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await update.callback_query.message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)





async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما دسترسی ندارید.")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ لطفاً آیدی کانال یا گروه را وارد کنید (مثلاً: @example_channel)")
        return

    new_channel = context.args[0].strip()
    
    if not new_channel.startswith("@"):
        await update.message.reply_text("⚠️ آیدی کانال باید با @ شروع شود.")
        return

    if new_channel in SPONSORED_CHANNELS:
        await update.message.reply_text("ℹ️ این کانال قبلاً اضافه شده.")
        return

    SPONSORED_CHANNELS.append(new_channel)
    await update.message.reply_text(f"✅ کانال جدید با موفقیت اضافه شد:\n{new_channel}")



async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما دسترسی ندارید.")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ لطفاً آیدی کانال یا گروهی که می‌خوای حذف بشه رو وارد کن.")
        return

    channel_to_remove = context.args[0].strip()

    if channel_to_remove not in SPONSORED_CHANNELS:
        await update.message.reply_text("⚠️ این کانال در لیست اسپانسرها نیست.")
        return

    SPONSORED_CHANNELS.remove(channel_to_remove)
    await update.message.reply_text(f"❌ کانال با موفقیت حذف شد:\n{channel_to_remove}")


async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        return

    if not SPONSORED_CHANNELS:
        await update.message.reply_text("📭 هیچ کانالی در لیست اسپانسر نیست.")
        return

    text = "\n".join([f"📢 {ch}" for ch in SPONSORED_CHANNELS])
    await update.message.reply_text(f"📋 لیست کانال‌های اسپانسر:\n\n{text}")



async def remove_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما اجازه ندارید این کار را انجام دهید.")
        return

    if not proxy_list:
        await update.message.reply_text("📭 لیست پروکسی خالیه.")
        return

    count = 1  # پیش‌فرض فقط یکی حذف می‌کنه
    if context.args and context.args[0].isdigit():
        count = int(context.args[0])

    removed = []
    for _ in range(min(count, len(proxy_list))):
        removed.append(proxy_list.pop())

    await update.message.reply_text(f"❌ {len(removed)} پروکسی آخر حذف شد:\n" + "\n".join(removed))


async def handle_amg_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get("chat_amg") is not True:
        return

    user_name = update.effective_user.full_name
    caption = f"📩 پیام از {user_name} ({user_id}):"

    if update.message.photo:
        msg = await context.bot.send_photo(ADMIN_IDS, photo=update.message.photo[-1].file_id, caption=caption)
        context.bot_data[f"reply_to:{msg.message_id}"] = user_id


    elif update.message.video:
        msg = await context.bot.send_video(ADMIN_IDS, video=update.message.video.file_id, caption=caption)
        context.bot_data[f"reply_to:{msg.message_id}"] = user_id

    elif update.message.voice:
        msg = await context.bot.send_voice(ADMIN_IDS, voice=update.message.voice.file_id, caption=caption)
        context.bot_data[f"reply_to:{msg.message_id}"] = user_id

    elif update.message.sticker:
        msg = await context.bot.send_sticker(ADMIN_IDS, sticker=update.message.sticker.file_id)
        context.bot_data[f"reply_to:{msg.message_id}"] = user_id

    elif update.message.document:
        msg = await context.bot.send_document(ADMIN_IDS, document=update.message.document.file_id, caption=caption)
        context.bot_data[f"reply_to:{msg.message_id}"] = user_id
        
    elif update.message.animation:
        msg = await context.bot.send_animation(ADMIN_IDS, animation=update.message.animation.file_id, caption=caption)
        context.bot_data[f"reply_to:{msg.message_id}"] = user_id

    else:
        msg = await context.bot.send_message(ADMIN_IDS, f"{caption}\n\n[پیام ناشناخته]")
        context.bot_data[f"reply_to:{msg.message_id}"] = user_id

    await update.message.reply_text("📨 پیام شما برای AMG ارسال شد. منتظر پاسخ باشید.")
    context.user_data["chat_amg"] = False


async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    print("🚀 handle_admin_reply اجرا شد")
    
    if update.effective_user.id != ADMIN_IDS:
        await update.message.reply_text("❌ شما اجازه پاسخ‌دهی ندارید.")
        return
    
    # فقط اگه داره ریپلای می‌کنه
    if not update.message.reply_to_message:
        await update.message.reply_text("لطفا روی پیام کاربر ریپلای کن")
        return

    # گرفتن آیدی کاربری که بهش پاسخ داده میشه
    reply_to_msg_id = update.message.reply_to_message.message_id
    user_id = context.bot_data.get(f"reply_to:{reply_to_msg_id}")

    if not user_id:
        await update.message.reply_text("❌ نتونستم کاربری که بهش ریپلای کردی رو پیدا کنم.")
        return

    # ارسال پاسخ به کاربر اصلی
    try:
        if update.message.text:
            await context.bot.send_message(user_id, f"🧑‍💼 پاسخ AMG:\n\n{update.message.text}")
        elif update.message.photo:
            await context.bot.send_photo(user_id, photo=update.message.photo[-1].file_id, caption="🧑‍💼 پاسخ AMG:")
        elif update.message.document:
            await context.bot.send_document(user_id, document=update.message.document.file_id, caption="🧑‍💼 پاسخ AMG:")
        elif update.message.video:
            await context.bot.send_video(user_id, video=update.message.video.file_id, caption="🧑‍💼 پاسخ AMG:")
        elif update.message.voice:
            await context.bot.send_voice(user_id, voice=update.message.voice.file_id)
        elif update.message.sticker:
            await context.bot.send_sticker(user_id, sticker=update.message.sticker.file_id)
        elif update.message.animation:
            await context.bot.send_animation(user_id, animation=update.message.animation.file_id)
        else:
            await context.bot.send_message(user_id, "🧑‍💼 پاسخ AMG دریافت شد.")
        
        await update.message.reply_text("✅ پاسخ برای کاربر ارسال شد.")

    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال پیام به کاربر:\n{e}")



async def handle_chat_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    caption = f"📨 پیام از {user_name} ({user_id}):"

    # چک کن کاربر در حالت چت با AMG یا پشتیبانی هست یا نه
    if not (context.user_data.get("chat_amg") or context.user_data.get("chat_support")):
        return

    try:
        if update.message.photo:
            msg = await context.bot.send_photo(ADMIN_IDS, photo=update.message.photo[-1].file_id, caption=caption)
        elif update.message.video:
            msg = await context.bot.send_video(ADMIN_IDS, video=update.message.video.file_id, caption=caption)
        elif update.message.voice:
            msg = await context.bot.send_voice(ADMIN_IDS, voice=update.message.voice.file_id, caption=caption)
        elif update.message.document:
            msg = await context.bot.send_document(ADMIN_IDS, document=update.message.document.file_id, caption=caption)
        elif update.message.sticker:
            msg = await context.bot.send_sticker(ADMIN_IDS, sticker=update.message.sticker.file_id)
        elif update.message.animation:
            msg = await context.bot.send_animation(ADMIN_IDS, animation=update.message.animation.file_id, caption=caption)
        else:
            msg = await context.bot.send_message(ADMIN_IDS, f"{caption}\n\n[پیام ناشناخته‌ای دریافت شد]")

        # ثبت امکان ریپلای
        context.bot_data[f"reply_to:{msg.message_id}"] = user_id

        await update.message.reply_text("📨 پیام شما برای AMG ارسال شد. منتظر پاسخ باشید.")
        context.user_data["chat_amg"] = False
        context.user_data["chat_support"] = False

    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال پیام:\n{e}")

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما دسترسی ندارید.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("⚠️ لطفاً آیدی عددی کاربر را وارد کنید.")
        return

    new_admin_id = int(context.args[0])
    ADMIN_ID.add(new_admin_id)
    await update.message.reply_text(f"✅ کاربر {new_admin_id} به لیست ادمین‌ها اضافه شد.")


async def remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما دسترسی ندارید.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("⚠️ لطفاً آیدی عددی کاربر را وارد کنید.")
        return

    remove_id = int(context.args[0])
    if remove_id == user_id:
        await update.message.reply_text("❌ نمی‌تونی خودتو حذف کنی!")
        return

    ADMIN_ID.discard(remove_id)
    await update.message.reply_text(f"🚫 کاربر {remove_id} از لیست ادمین‌ها حذف شد.")


async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        return
    admin_list = "\n".join([f"👑 {admin_id}" for admin_id in ADMIN_ID])
    await update.message.reply_text(f"📋 لیست ادمین‌ها:\n{admin_list}")



async def vipme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    count = invite_count.get(user_id, 0)
    is_vip = "✅ شما در لیست VIP هستید." if user_id in vip_users else "❌ شما هنوز VIP نیستید."
    await update.message.reply_text(
        f"👥 تعداد دعوت‌شده‌ها: {count}\n{is_vip}\n\n"
        f"📎 لینک اختصاصی شما:\nhttps://t.me/{context.bot.username}?start=ref_{user_id}"
    )




async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_IDS:
        await update.message.reply_text("❌ فقط ادمین می‌تونه از این دستور استفاده کنه.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("⚠️ استفاده صحیح: /reply <user_id> <message>")
        return

    user_id = int(context.args[0])
    message = " ".join(context.args[1:])
    try:
        await context.bot.send_message(chat_id=user_id, text=f"🧑‍💼 پاسخ AMG:\n\n{message}")

        if user_id in tickets:
            tickets[user_id]["status"] = "🟢 بسته شد"

        await update.message.reply_text("✅ پاسخ ارسال شد.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارسال: {e}")


async def vip_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما اجازه ندارید.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("⚠️ لطفاً آیدی عددی کاربر را وارد کنید.")
        return

    target_id = int(context.args[0])
    vip_users.add(target_id)
    await update.message.reply_text(f"✅ کاربر {target_id} با موفقیت VIP شد.")



async def vip_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما اجازه ندارید.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("⚠️ لطفاً آیدی عددی کاربر را وارد کنید.")
        return

    target_id = int(context.args[0])
    if target_id in vip_users:
        vip_users.remove(target_id)
        await update.message.reply_text(f"🚫 کاربر {target_id} از لیست VIP حذف شد.")
    else:
        await update.message.reply_text("ℹ️ این کاربر در لیست VIP نبود.")




async def vip_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما اجازه ندارید.")
        return

    if not vip_users:
        await update.message.reply_text("📭 هیچ کاربری در لیست VIP نیست.")
        return

    vip_text = "\n".join([f"👤 {uid}" for uid in vip_users])
    await update.message.reply_text(f"📋 لیست کاربران VIP:\n\n{vip_text}")



# تابعی برای شروع بازی
async def start_game(update, context):
    user_id = update.effective_user.id
    
    if user_id in user_games and user_games[user_id]["playing"]:
        await update.message.reply_text("شما در حال حاضر در حال بازی هستید. لطفا بازی قبلی رو تمام کنید.")
        return

    # شروع بازی و ایجاد وضعیت اولیه
    start_range = random.randint(1, 900)  # شروع بازه (۱ تا ۹۰۰، چون باید ۱۰۰ عدد جا بشه)
    end_range = start_range + 99
    
    user_games[user_id] = {
        "playing": True,
        "attempts": 0,
        "score": 100,   # امتیاز اولیه
        "guess_limit": 0,  # تعداد حدس‌ها در نسخه محدود
        "number": random.randint(start_range, end_range),  # عدد تصادفی در بازه
        "range": (start_range, end_range),  # ذخیره بازه برای استفاده بعدی
    }


    # ارسال پنل شیشه‌ای برای انتخاب نسخه بازی
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("نسخه نامحدود", callback_data="unlimited_version")],
        [InlineKeyboardButton("نسخه محدود", callback_data="limited_version")],
    ])
    
    await update.message.reply_text(
        f"🎮 بازی حدس عدد شروع شد! لطفاً نسخه بازی رو انتخاب کنید.\n"
        f"(بازه این بار: {start_range} تا {end_range})",
        reply_markup=keyboard
    )




# تابعی برای انتخاب نسخه بازی (محدود یا نامحدود)
async def choose_game_version(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if user_id not in user_games or user_games[user_id]["playing"] == False:
        await query.edit_message_text("لطفاً ابتدا بازی رو شروع کنید.")
        return

    if query.data == "unlimited_version":
        user_games[user_id]["guess_limit"] = float("inf")
        context.user_data["game_state"] = "playing"
        start_range, end_range = user_games[user_id]["range"]
        await query.edit_message_text(f"✅ نسخه نامحدود انتخاب شد! حالا یک عدد بین {start_range} تا {end_range} حدس بزنید.")
    elif query.data == "limited_version":
        context.user_data["game_state"] = "awaiting_limit"
        await query.edit_message_text("✍️ چند حدس می‌خواهید؟ (مثلاً 5)")



async def exit_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in user_games and user_games[user_id]["playing"]:
        user_games[user_id]["playing"] = False
        context.user_data["game_state"] = None
        await update.message.reply_text("🚪 شما از بازی خارج شدید. هر وقت خواستید با دستور /start_game دوباره بازی کنید.")
    else:
        await update.message.reply_text("ℹ️ شما در حال حاضر داخل هیچ بازی‌ای نیستید.")



# --- سیستم راهنما ---

async def show_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇷 فارسی", callback_data="help_lang_fa")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="help_lang_en")]
    ])
    if update.message:
        await update.message.reply_text("📖 Please choose your language:\n\n📖 لطفاً زبان خود را انتخاب کنید:", reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.message.reply_text("📖 Please choose your language:\n\n📖 لطفاً زبان خود را انتخاب کنید:", reply_markup=keyboard)


async def help_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = query.data.split("_")[-1]
    context.user_data["help_lang"] = lang
    context.user_data["help_page"] = 0

    text = help_pages[lang][0]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Next", callback_data=f"help_next_{lang}_0")]
    ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)


async def help_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data_parts = query.data.split("_")
    action, lang, page_index = data_parts[1], data_parts[2], int(data_parts[3])

    if action == "next":
        page_index += 1
    elif action == "prev":
        page_index -= 1

    context.user_data["help_page"] = page_index
    text = help_pages[lang][page_index]

    # دکمه‌ها
    buttons = []
    if page_index > 0:
        buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"help_prev_{lang}_{page_index}"))
    if page_index < len(help_pages[lang]) - 1:
        buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"help_next_{lang}_{page_index}"))

    keyboard = InlineKeyboardMarkup([buttons]) if buttons else None
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)




async def show_top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_scores:
        await update.message.reply_text("📭 هنوز کسی امتیاز بازی نگرفته.")
        return

    # مرتب‌سازی کاربران بر اساس امتیاز
    top_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    
    text = "🏆 جدول برترین‌ها:\n\n"
    for i, (uid, score) in enumerate(top_users, start=1):
        try:
            user = await context.bot.get_chat(uid)
            name = user.first_name
        except:
            name = f"User {uid}"
        text += f"{i}. 👤 {name} — {score} امتیاز\n"

    await update.message.reply_text(text)



async def list_tickets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_ID:
        return
    if not tickets:
        await update.message.reply_text("📭 هیچ تیکتی وجود ندارد.")
        return

    text = "📋 لیست تیکت‌ها:\n\n"
    for uid, info in tickets.items():
        text += f"👤 {uid} — {info['status']} — {len(info['messages'])} پیام\n"
    await update.message.reply_text(text)





async def add_xp(user_id: int):
    now = int(time.time())
    async with xp_lock:
        user = user_xp[user_id]
        if now - user["last_ts"] < MIN_XP_INTERVAL:
            return user["xp"], False, user["level"]

        add = random.randint(XP_PER_MESSAGE_MIN, XP_PER_MESSAGE_MAX)
        user["xp"] += add
        user["last_ts"] = now

        new_level = compute_level_from_xp(user["xp"])
        leveled = new_level > user["level"]
        if leveled:
            user["level"] = new_level

        return user["xp"], leveled, user["level"]



async def rank_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    u = user_xp[user_id]
    current_level = u["level"]
    xp = u["xp"]
    next_level = current_level + 1
    next_level_xp = 100 * (next_level ** 2)
    xp_needed = max(next_level_xp - xp, 0)

    await update.message.reply_text(
        f"🏅 پروفایل شما:\n\n"
        f"👤 آیدی: {user_id}\n"
        f"🔸 لِول: {current_level}\n"
        f"⭐ XP: {xp}\n"
        f"⏳ تا لِول {next_level}: {xp_needed} XP"
    )





async def start_rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # چک کن کاربر در حال بازی نباشه
    if user_id in rps_games and rps_games[user_id]["playing"]:
        await update.message.reply_text("⏳ شما در حال حاضر در بازی سنگ‌کاغذ‌قیچی هستید!")
        return

    rps_games[user_id] = {"playing": True}

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🪨 سنگ", callback_data="rps_rock"),
            InlineKeyboardButton("📄 کاغذ", callback_data="rps_paper"),
            InlineKeyboardButton("✂️ قیچی", callback_data="rps_scissors")
        ],
        [InlineKeyboardButton("🚪 خروج", callback_data="rps_exit")]
    ])

    await update.message.reply_text("🎮 بازی سنگ‌کاغذ‌قیچی شروع شد!\nیکی از گزینه‌ها رو انتخاب کن:", reply_markup=keyboard)





async def handle_rps_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in rps_games or not rps_games[user_id]["playing"]:
        await query.answer("❌ شما بازی‌ای رو شروع نکردی.")
        return

    user_choice = query.data.replace("rps_", "")
    if user_choice == "exit":
        rps_games[user_id]["playing"] = False
        await query.edit_message_text("🚪 شما از بازی خارج شدید.")
        return

    # انتخاب ربات
    bot_choice = random.choice(["rock", "paper", "scissors"])
    emoji_map = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}

    # برنده رو مشخص کن
    if user_choice == bot_choice:
        result = "🤝 مساوی شد!"
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "scissors" and bot_choice == "paper") or \
         (user_choice == "paper" and bot_choice == "rock"):
        result = "🎉 شما برنده شدید!"
        user_scores[user_id] += 10
    else:
        result = "😢 ربات برنده شد!"

    text = (
        f"👤 شما: {emoji_map[user_choice]}\n"
        f"🤖 ربات: {emoji_map[bot_choice]}\n\n"
        f"{result}"
    )

    # دوباره گزینه‌ها برای ادامه
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🪨 سنگ", callback_data="rps_rock"),
            InlineKeyboardButton("📄 کاغذ", callback_data="rps_paper"),
            InlineKeyboardButton("✂️ قیچی", callback_data="rps_scissors")
        ],
        [InlineKeyboardButton("🚪 خروج", callback_data="rps_exit")]
    ])

    await query.edit_message_text(text, reply_markup=keyboard)




async def add_special(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:  # فقط ادمین‌ها
        await update.message.reply_text("❌ شما اجازه این کار را ندارید.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("⚠️ استفاده صحیح: /addspecial <user_id> <پیام خوشامد>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("⚠️ آیدی باید عددی باشد.")
        return

    message = " ".join(context.args[1:])
    special_users[target_id] = message
    await update.message.reply_text(f"✅ کاربر {target_id} با پیام ویژه اضافه شد:\n{message}")





async def remove_special(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_ID:
        await update.message.reply_text("❌ شما اجازه این کار را ندارید.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("⚠️ استفاده صحیح: /removespecial <user_id>")
        return

    target_id = int(context.args[0])
    if target_id in special_users:
        del special_users[target_id]
        await update.message.reply_text(f"🚫 کاربر {target_id} از لیست ویژه حذف شد.")
    else:
        await update.message.reply_text("ℹ️ این کاربر در لیست ویژه نبود.")






# --- اضافه کردن هندلر‌ها ---

def main():    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addproxy", add_proxy))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("adminpanel", admin_panel))
    app.add_handler(CommandHandler("ask", ask_ai))
    app.add_handler(CommandHandler("users", show_users))
    app.add_handler(CommandHandler("profile", show_profile))
    app.add_handler(CommandHandler("addchannel", add_channel))
    app.add_handler(CommandHandler("removechannel", remove_channel))
    app.add_handler(CommandHandler("channels", list_channels))
    app.add_handler(CommandHandler("removeproxy", remove_proxy))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("removeadmin", remove_admin))
    app.add_handler(CommandHandler("admins", list_admins))
    app.add_handler(CommandHandler("vipme", vipme))
    app.add_handler(CommandHandler("reply", reply_command))
    app.add_handler(CommandHandler("vipadd", vip_add))
    app.add_handler(CommandHandler("vipremove", vip_remove))
    app.add_handler(CommandHandler("viplist", vip_list))
    app.add_handler(CommandHandler("start_game", start_game))
    app.add_handler(CommandHandler("exit_game", exit_game))
    app.add_handler(CommandHandler("help", show_help_menu))
    app.add_handler(CommandHandler("top", show_top))
    app.add_handler(CommandHandler("tickets", list_tickets))
    app.add_handler(CommandHandler("rank", rank_command))
    app.add_handler(CommandHandler("rps", start_rps))
    app.add_handler(CommandHandler("addspecial", add_special))
    app.add_handler(CommandHandler("removespecial", remove_special))






    app.add_handler(CallbackQueryHandler(admin_panel_callback, pattern="^(ban_user|unban_user|bot_stats)$"))
    app.add_handler(CallbackQueryHandler(choose_game_version, pattern="^(unlimited_version|limited_version)$"))
    app.add_handler(CallbackQueryHandler(help_language, pattern="^help_lang_"))
    app.add_handler(CallbackQueryHandler(help_navigation, pattern="^help_(next|prev)_"))
    app.add_handler(CallbackQueryHandler(handle_rps_choice, pattern="^rps_"))
    app.add_handler(CallbackQueryHandler(button))

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_user_msg))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_user_msg))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, anti_link_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=ADMIN_ID), admin_action_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_user_msg))
    app.add_handler(MessageHandler(
        filters.REPLY & filters.ChatType.PRIVATE & filters.User(user_id=ADMIN_IDS),
        handle_admin_reply
    ))
    app.add_handler(MessageHandler(
        (filters.PHOTO | filters.VIDEO | filters.VOICE | filters.ANIMATION | filters.Document.ALL) & filters.ChatType.PRIVATE,
        handle_chat_media
    ))
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.PRIVATE, handle_amg_media))

    
    app.run_polling()

if __name__ == '__main__':
    main()
