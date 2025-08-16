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
user_ids = set()
banned_users = set()
tickets = {}
subscribed_users = set()
# دیکشنری برای نگهداری وضعیت بازی هر کاربر
user_games = {}


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
            ["ℹ️ درباره ربات"]
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
            " ├─ 💬 چت خصوصی با ادمین (AMG) + پاسخ ریپلای\n"
            " ├─ 🧠 پاسخگویی با هوش مصنوعی GPT-3.5\n"
            " ├─ 🛡️ ضد لینک هوشمند مخصوص گروه‌ها\n"
            " ├─ 👋 خوش‌آمدگویی خودکار\n"
            " ├─ 🌐 ارائه پروکسی‌های به‌روز (مدیریت توسط ادمین)\n"
            " ├─ 📜 فال حافظ با تعبیر دقیق\n"
            " └─ 🆘 سیستم پشتیبانی حرفه‌ای\n\n"
            "👤 سازنده: @AMG_ir\n"
            "🧠 مدل AI: OpenRouter - GPT-3.5-Turbo\n"
            "🔖 نسخه: v2.2.0-AR\n"
            "📅 تاریخ: ۲۰۲۵/۰۷/۱۶"
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
                [InlineKeyboardButton("🚫 فعال‌سازی ضد لینک", callback_data="enable_anti_link")],
                [InlineKeyboardButton("🔑 دریافت پروکسی", callback_data="get_proxy")],
                [InlineKeyboardButton("ℹ️ اطلاعات ربات", callback_data="bot_info")],
                [InlineKeyboardButton("📞 درخواست پشتیبانی", callback_data="support")]
            ])
            await update.message.reply_text("🎛️ پنل گروهی:", reply_markup=keyboard)
            return


    # --- دکمه‌های منوی اصلی ---
    if "چت با AMG" in text:
        if user_id in special_users:
            await update.message.reply_text(special_users[user_id])
        else:
            await update.message.reply_text("📨 پیام‌تو برای AMG بنویس.")
        context.user_data['chat_amg'] = True
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
            " ├─ 💬 چت خصوصی با ادمین (AMG) + پاسخ ریپلای\n"
            " ├─ 🧠 پاسخگویی با هوش مصنوعی GPT-3.5\n"
            " ├─ 🛡️ ضد لینک هوشمند مخصوص گروه‌ها\n"
            " ├─ 👋 خوش‌آمدگویی خودکار\n"
            " ├─ 🌐 ارائه پروکسی‌های به‌روز (مدیریت توسط ادمین)\n"
            " ├─ 📜 فال حافظ با تعبیر دقیق\n"
            " └─ 🆘 سیستم پشتیبانی حرفه‌ای\n\n"
            "👤 سازنده: @AMG_ir\n"
            "🧠 مدل AI: OpenRouter - GPT-3.5-Turbo\n"
            "🔖 نسخه: v2.2.0-AR\n"
            "📅 تاریخ: ۲۰۲۵/۰۷/۱۶"
        )
        return

    
    elif "پشتیبانی" in text:
        await update.message.reply_text("🆘 لطفاً سوال یا مشکل خود را ارسال کنید.")
        tickets[user_id] = "درخواست پشتیبانی ثبت شده"
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
            await update.message.reply_text(f"✅ نسخه محدود انتخاب شد! شما {limit} حدس دارید. حالا یک عدد بین 1 تا 100 حدس بزنید.")
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


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        await update.message.reply_text("❌ اطلاعاتی از شما ثبت نشده.")
        return
    
    profile = user_data[user_id]
    await update.message.reply_text(
        f"👤 پروفایل شما:\n\n"
        f"🆔 آیدی: {user_id}\n"
        f"📆 تاریخ عضویت: {profile['join_date']}\n"
        f"🧠 دفعات استفاده از هوش مصنوعی: {profile['ai_uses']}"
    )



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
    user_games[user_id] = {
        "playing": True,
        "attempts": 0,
        "score": 100,  # امتیاز اولیه
        "guess_limit": 0,  # تعداد حدس‌ها در نسخه محدود
        "number": random.randint(1, 100),  # عدد تصادفی برای حدس
    }

    # ارسال پنل شیشه‌ای برای انتخاب نسخه بازی
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("نسخه نامحدود", callback_data="unlimited_version")],
        [InlineKeyboardButton("نسخه محدود", callback_data="limited_version")],
    ])
    
    await update.message.reply_text(
        "🎮 بازی حدس عدد شروع شد! لطفاً نسخه بازی رو انتخاب کنید:",
        reply_markup=keyboard
    )



# تابعی برای انتخاب نسخه بازی (محدود یا نامحدود)
async def choose_game_version(update, context):
    user_id = update.callback_query.from_user.id
    query = update.callback_query
    await query.answer()

    if user_id not in user_games or user_games[user_id]["playing"] == False:
        await query.edit_message_text("لطفاً ابتدا بازی رو شروع کنید.")
        return

    # دریافت نسخه انتخابی
    if query.data == "unlimited_version":
        user_games[user_id]["guess_limit"] = float("inf")  # بی‌نهایت حدس
        await query.edit_message_text("✅ نسخه نامحدود انتخاب شد! شروع به حدس زدن عدد کن.")
        
    elif query.data == "limited_version":
        user_games[user_id]["guess_limit"] = int(await get_user_input(update, context, "چند حدس می‌خواهید؟ (مثلاً 5)"))
        await query.edit_message_text(f"✅ نسخه محدود انتخاب شد! شما {user_games[user_id]['guess_limit']} حدس دارید. شروع به حدس زدن عدد کن.")

    # شروع بازی
    await start_guessing_game(update, context)



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
        await query.edit_message_text("✅ نسخه نامحدود انتخاب شد! حالا یک عدد بین 1 تا 100 حدس بزنید.")
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




    app.add_handler(CallbackQueryHandler(admin_panel_callback, pattern="^(ban_user|unban_user|bot_stats)$"))
    app.add_handler(CallbackQueryHandler(choose_game_version, pattern="^(unlimited_version|limited_version)$"))
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
