import requests
import random
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# تنظیمات
ADMIN_ID = 6807376124
TOKEN = "8183707654:AAGqEcAConlQICPB3sGdbZ5aDMtrVpPHdKQ"
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

vip_users = set()
anti_link_groups = set()
proxy_list = []
user_ids = set()
banned_users = set()
tickets = {}
subscribed_users = set()

# --- استارت و منوی اصلی ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_ids.add(user_id)
    
    reply_keyboard = ReplyKeyboardMarkup([
        ["🤖 چت هوش مصنوعی", "💬 چت با AMG"],
        ["🌐 دریافت پروکسی", "📢 سفارش تبلیغ"],
        ["➕ افزودن به گروه", "🆘 پشتیبانی"],
        ["ℹ️ درباره ربات"]
    ], resize_keyboard=True)

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
        await update.message.reply_text("👋 سلام! یکی از گزینه‌ها یا دستورها را انتخاب کن.", reply_markup=reply_keyboard)

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
        context.user_data['chat_amg'] = True

    elif query.data == "bot_info":
        await query.message.reply_text(
            "ℹ️ اطلاعات ربات:\n\n"
            "🤖 نام: 𓄂AMG𓆃\n"
            "✨ قابلیت‌ها:\n"
            " ├─ 💬 چت خصوصی با ادمین (AMG)\n"
            " ├─ 🧠 پاسخگویی با هوش مصنوعی GPT-3.5\n"
            " ├─ 🛡️ ضد لینک هوشمند مخصوص گروه‌ها\n"
            " ├─ 👋 خوش‌آمدگویی خودکار\n"
            " └─ 🌐 ارائه پروکسی‌های به‌روز\n\n"
            "👤 سازنده: @AMG_ir\n"
            "🧠 مدل AI: OpenRouter - GPT-3.5-Turbo\n"
            "🔖 نسخه: v2.1.3-AR\n"
            "📅 تاریخ: ۲۰۲۵/۰۷/۱۰"
        )

    elif query.data == "support":
        await query.message.reply_text("🆘 درخواست پشتیبانی شما ثبت شد. لطفاً سوال یا مشکل خود را ارسال کنید.")
        tickets[user_id] = "درخواست پشتیبانی ثبت شده"

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

    if user_id in banned_users:
        return

    # پاسخ به ریپلای روی ربات در گروه‌ها با جمله‌های رندم ایموجی‌دار
    if update.message.chat.type in ["group", "supergroup"]:
        if update.message.reply_to_message:
            if update.message.reply_to_message.from_user.id == context.bot.id:
                replies = [
                    "😤 با من چیکار داری؟",
                    "🙄 به من دست نزن!",
                    "🤨 چی‌ می‌خوای؟",
                    "😏 چرا منو اذیت می‌کنی؟",
                    "😎 باشه باشه، حرفت رو شنیدم!",
                    "😒 خب جدی باشیم!"
                ]
                await update.message.reply_text(random.choice(replies))
                return

    # واکنش به کلمه‌های AMG و متین و کلمات مشابه تو گروه با جملات رندم ایموجی‌دار
    if update.message.chat.type in ["group", "supergroup"]:
        low_text = text.lower()
        if any(word in low_text for word in ["amg", "امگ", "متین"]):
            responses = [
                "💬 سلام رفیق، چی می‌خوای بگی؟",
                "🤖 امگ همیشه اینجاست!",
                "🔥 AMG، بهترین ربات!",
                "⚡️ حالا چی شده؟",
                "🎉 خوش اومدی به گروه!",
                "👋 یه سلام ویژه از AMG!"
            ]
            await update.message.reply_text(random.choice(responses))
            return

    # اگر در گروه پیام دارای لینک بود و ضد لینک فعال بود پیام حذف شود
    if update.message.chat.type in ["group", "supergroup"]:
        if update.message.entities:
            for ent in update.message.entities:
                if ent.type in ["url", "text_link"]:
                    if update.message.chat.id in anti_link_groups:
                        try:
                            await update.message.delete()
                            await update.message.reply_text("🚫 ارسال لینک در این گروه ممنوع است!")
                            return
                        except:
                            pass

    # فرمان‌ها (دستورات متنی ساده)
    if text == "🤖 چت هوش مصنوعی":
        # فعال کردن چت با هوش مصنوعی در حالت پیام به پیام
        context.user_data['chat_ai'] = True
        context.user_data['chat_amg'] = False
        await update.message.reply_text("🤖 حالت چت با هوش مصنوعی فعال شد. هر سوالی داری بپرس!")

    elif text == "💬 چت با AMG":
        context.user_data['chat_amg'] = True
        context.user_data['chat_ai'] = False
        await update.message.reply_text("💬 حالت چت با AMG فعال شد. هر سوالی داری بپرس!")

    elif text == "➕ افزودن به گروه":
        await update.message.reply_text("برای افزودن ربات به گروه، لینک زیر را ارسال کن:\n\nhttps://t.me/YourBotUsername?startgroup=true")

    elif text == "🆘 پشتیبانی":
        tickets[user_id] = "درخواست پشتیبانی ثبت شده"
        await update.message.reply_text("🆘 درخواست شما ثبت شد. لطفاً سوال یا مشکل خود را ارسال کنید.")

    elif text == "ℹ️ درباره ربات":
        await update.message.reply_text(
            "🤖 ربات هوش مصنوعی AMG\n"
            "نسخه ۲.۱.۳\n"
            "برای استفاده از هوش مصنوعی ابتدا عضو کانال‌ها شوید.\n"
            "ساخته شده توسط @AMG_ir"
        )

    elif text == "📢 سفارش تبلیغ":
        await update.message.reply_text("برای سفارش تبلیغ لطفاً با پشتیبانی تماس بگیرید.")

    elif text == "🌐 دریافت پروکسی":
        if proxy_list:
            proxies = "\n".join(proxy_list[-5:])
            await update.message.reply_text(f"🌐 پروکسی‌های جدید:\n\n{proxies}")
        else:
            await update.message.reply_text("⚠️ هنوز پروکسی‌ای ثبت نشده.")

    elif text and text.startswith("/ask "):
        question = text[5:]
        response = await ask_ai(question)
        await update.message.reply_text(response)

    elif context.user_data.get('chat_ai'):
        # ارسال پیام به هوش مصنوعی (OpenRouter) و دریافت پاسخ
        response = await ask_ai(text)
        await update.message.reply_text(response)

    elif context.user_data.get('chat_amg'):
        # ارسال پیام به AMG (همان هوش مصنوعی ولی با رفتار متفاوت)
        response = await ask_ai(text, amg=True)
        await update.message.reply_text(response)

# --- تابع پرسش از هوش مصنوعی ---

async def ask_ai(question, amg=False):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    if amg:
        # پیام با قالب متفاوت برای AMG
        messages = [{"role": "user", "content": question}]
    else:
        # پیام معمولی برای هوش مصنوعی
        messages = [{"role": "user", "content": question}]

    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            return answer
        else:
            return "❌ مشکلی پیش آمده، دوباره تلاش کن."
    except Exception:
        return "❌ خطا در اتصال به سرور هوش مصنوعی."

# --- اجرای برنامه ---

async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_msg))

    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
