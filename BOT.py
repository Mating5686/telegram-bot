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

    # واکنش به کلمه‌های AMG و امگ تو گروه با جملات رندم
    if update.message.chat.type in ["group", "supergroup"]:
        low_text = text.lower()
        if any(word in low_text for word in ["amg", "امگ"]):
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

    # پنل شیشه‌ای گروهی با دکمه‌ها وقتی «پنل ربات» گفته بشه
    if update.message.chat.type in ["group", "supergroup"]:
        if text == "پنل ربات":
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("فعال‌سازی ضد لینک", callback_data="enable_anti_link")],
                [InlineKeyboardButton("دریافت پروکسی", callback_data="get_proxy")],
                [InlineKeyboardButton("اطلاعات ربات", callback_data="bot_info")],
                [InlineKeyboardButton("درخواست پشتیبانی", callback_data="support")]
            ])
            await update.message.reply_text("🎛️ پنل گروهی:", reply_markup=keyboard)
            return

    if text == "💬 چت با AMG":
        if user_id in special_users:
            await update.message.reply_text(special_users[user_id])
        else:
            await update.message.reply_text("📨 پیام‌تو برای AMG بنویس.")
        context.user_data['chat_amg'] = True

    elif text == "📢 سفارش تبلیغ":
        await update.message.reply_text("✍️ لطفاً نوع تبلیغ و توضیحاتت رو کامل بفرست.")

    elif text == "🌐 دریافت پروکسی":
        if proxy_list:
            proxies = "\n".join(proxy_list[-5:])
            await update.message.reply_text(f"🌐 پروکسی‌های جدید:\n\n{proxies}")
        else:
            await update.message.reply_text("⚠️ هنوز پروکسی‌ای ثبت نشده.")

    elif text == "🤖 چت با هوش مصنوعی":
        if await check_channel_membership(user_id, context):
            await update.message.reply_text("❓ سوالت رو با دستور `/ask سوالت` بپرس.")
        else:
            await update.message.reply_text("⚠️ برای استفاده از هوش مصنوعی، باید عضو کانال‌های اسپانسر بشی:\n" +
                                            "\n".join([f"📢 {channel}" for channel in SPONSORED_CHANNELS]))

    elif text == "ℹ️ اطلاعات ربات":
        await update.message.reply_text(
            "ℹ️ اطلاعات ربات:\n\n"
            "🤖 نام: 𓄂AMG𓆃\n"
            "✨ قابلیت‌ها:\n"
            " ├─ 💬 چت خصوصی با ادمین (AMG)\n"
            " ├─ 🧠 پاسخگویی با هوش مصنوعی GPT-3.5\n"
            " ├─ 🛡️ ضد لینک هوشمند مخصوص گروه‌ها\n"
            " ├─ 👋 خوش‌آمدگویی خودکار\n"
            " └─ 🌐 ارائه پروکسی‌های به‌روز\n\n"
            "👤 سازنده: @AMG_ir\n"
            "🧠 مدل: OpenRouter - GPT-3.5-Turbo\n"
            "🔖 نسخه: v2.1.3-AR\n"
            "📅 تاریخ: ۲۰۲۵/۰۷/۱۰"
        )

    elif context.user_data.get('chat_amg'):
        await context.bot.send_message(ADMIN_ID, f"💬 پیام از {update.effective_user.full_name}:\n\n{text}")
        await update.message.reply_text("پیام شما به ادمین ارسال شد. منتظر پاسخ باشید.")
        context.user_data['chat_amg'] = False

# --- دستور ادمین: افزودن پروکسی ---

async def add_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
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
    if user_id != ADMIN_ID:
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
    if user_id != ADMIN_ID:
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
    if user_id != ADMIN_ID:
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
    if user_id != ADMIN_ID:
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
        answer = response_json['choices'][0]['message']['content']
        await update.message.reply_text(f"🧠 پاسخ AMG:\n\n{answer}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ارتباط با هوش مصنوعی:\n{e}")

# --- حذف منوی ویژه و اضافه کردن گزینه‌های درخواست پشتیبانی و افزودن به گروه در منوی پایین ---

# (اینکار در منوی start انجام شده)

# --- ضد لینک ---

async def anti_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in anti_link_groups:
        if update.message.entities:
            for entity in update.message.entities:
                if entity.type in ["url", "text_link"]:
                    await update.message.delete()
                    await update.message.reply_text(f"⚠️ لینک در گروه ممنوع است، {update.effective_user.first_name}!")
                    return

# --- اضافه کردن هندلر‌ها ---

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addproxy", add_proxy))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("adminpanel", admin_panel))
    app.add_handler(CommandHandler("ask", ask_ai))

    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CallbackQueryHandler(admin_panel_callback, pattern="^(ban_user|unban_user|bot_stats)$"))

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_user_msg))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_user_msg))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=ADMIN_ID), admin_action_handler))
    app.add_handler(MessageHandler(filters.Entity("url") & filters.ChatType.GROUPS, anti_link_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
