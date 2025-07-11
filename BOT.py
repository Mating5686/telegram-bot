import requests
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

# کاربران تاییدشده عضو کانال
subscribed_users = set()

import random

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = ReplyKeyboardMarkup([
        ["💬 چت با AMG", "📢 سفارش تبلیغ"],
        ["🌐 دریافت پروکسی", "🤖 چت با هوش مصنوعی"],
        ["ℹ️ اطلاعات ربات"],
        ["➕ افزودن به گروه", "🆘 درخواست پشتیبانی"]
    ], resize_keyboard=True)

    channels_buttons = [
        [InlineKeyboardButton(f"📢 پیوستن به {channel[1:]}", url=f"https://t.me/{channel[1:]}")]
        for channel in SPONSORED_CHANNELS
    ]
    channels_buttons.append([InlineKeyboardButton("✅ تایید عضویت", callback_data="check_subscription")])

    await update.message.reply_text("👋 سلام! یکی از گزینه‌ها رو انتخاب کن:", reply_markup=reply_keyboard)
    await update.message.reply_text("📣 کانال‌های اسپانسر:", reply_markup=InlineKeyboardMarkup(channels_buttons))
    user_ids.add(update.effective_user.id)

async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    for channel in SPONSORED_CHANNELS:
        chat_member = await context.bot.get_chat_member(channel, user_id)
        if chat_member.status != ChatMember.MEMBER:
            return False
    return True

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
            await query.message.reply_text("✅ عضویت شما تایید شد. حالا می‌تونی از امکانات ربات استفاده کنی.")
        else:
            await query.message.reply_text(
                "⚠️ هنوز عضو همه‌ی کانال‌ها نشدی!\n\n"
                "📌 لطفاً ابتدا در کانال‌های زیر عضو شو و بعد روی «تایید عضویت» بزن:\n" +
                "\n".join([f"📢 {channel}" for channel in SPONSORED_CHANNELS])
            )

async def handle_user_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in banned_users:
        return

    # بررسی پیام‌های دکمه‌ها و کامندها

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
        if user_id in subscribed_users:
            await update.message.reply_text("❓ سوالت رو با دستور `/ask سوالت` بپرس.")
        else:
            await update.message.reply_text("⚠️ برای استفاده از هوش مصنوعی، اول باید عضویت در کانال‌های اسپانسر رو تایید کنی.")

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

    elif text == "➕ افزودن به گروه":
        await update.message.reply_text(f"📌 برای افزودن من به گروه:\n👉 https://t.me/{context.bot.username}?startgroup=true")

    elif text == "🆘 درخواست پشتیبانی":
        await update.message.reply_text("🆘 لطفاً سوال یا مشکلت رو بنویس. تا حد امکان زود پاسخ می‌دیم.")
        tickets[user_id] = "درخواست پشتیبانی ثبت شده"

    # حالت چت با AMG
    elif context.user_data.get('chat_amg'):
        await context.bot.send_message(ADMIN_ID, f"📩 پیام از {user_id}:\n{text}")
        await update.message.reply_text("📤 پیام‌ت برای AMG فرستاده شد.")
        context.user_data['chat_amg'] = False

    # ارسال پیام از ادمین به کاربر (ریپلای)
    elif user_id == ADMIN_ID and update.message.reply_to_message:
        try:
            target_id = int(update.message.reply_to_message.text.split()[2].strip(":"))
            await context.bot.send_message(target_id, text)
            await update.message.reply_text("✅ پیام به کاربر ارسال شد.")
        except:
            await update.message.reply_text("❌ ارسال نشد. ساختار پیام پاسخ درست نیست.")

    # حالت ارسال پیام همگانی (broadcast)
    elif user_id == ADMIN_ID and context.user_data.get('broadcast_mode'):
        message = text
        success, failed = 0, 0

        for uid in user_ids.copy():
            try:
                await context.bot.send_message(uid, message)
                success += 1
            except:
                failed += 1
                continue

        await update.message.reply_text(f"📤 پیام برای {success} نفر ارسال شد.\n❌ ناموفق: {failed}")
        context.user_data['broadcast_mode'] = False

    else:
        # واکنش به کلمه «پنل ربات» در گروه
        if update.effective_chat.type in ["group", "supergroup"]:
            if "پنل ربات" in text:
                panel_text = (
                    "🛠️ پنل ویژه گروه:\n\n"
                    "1️⃣ فعال‌سازی ضد لینک\n"
                    "2️⃣ مدیریت اعضا\n"
                    "3️⃣ مشاهده آمار گروه\n"
                    "4️⃣ تنظیمات پیشرفته\n\n"
                    "برای استفاده، از دکمه‌ها یا دستورات مخصوص استفاده کن."
                )
                await update.message.reply_text(panel_text)
                return

            # واکنش به کلمات AMG و امگ به صورت رندوم یک حرف
            lowered = text.lower()
            if "amg" in lowered or "امگ" in text:
                chars = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
                rand_char = random.choice(chars)
                await update.message.reply_text(rand_char)
                return

        await update.message.reply_text("📋 لطفاً یکی از گزینه‌ها یا دستورها را انتخاب کن.")

async def add_proxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠️ فقط ادمین می‌تواند پروکسی اضافه کند.")
        return
    if not context.args:
        await update.message.reply_text("📝 لطفاً پروکسی را به صورت متن ارسال کن.")
        return
    proxy = " ".join(context.args)
    proxy_list.append(proxy)
    await update.message.reply_text(f"✅ پروکسی جدید اضافه شد:\n{proxy}")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠️ فقط ادمین می‌تواند کاربر را بن کند.")
        return
    if not context.args:
        await update.message.reply_text("📝 لطفاً آیدی کاربر را ارسال کن.")
        return
    try:
        ban_id = int(context.args[0])
        banned_users.add(ban_id)
        await update.message.reply_text(f"🚫 کاربر {ban_id} بن شد.")
    except:
        await update.message.reply_text("❌ آیدی معتبر نیست.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠️ فقط ادمین می‌تواند کاربر را آنبن کند.")
        return
    if not context.args:
        await update.message.reply_text("📝 لطفاً آیدی کاربر را ارسال کن.")
        return
    try:
        unban_id = int(context.args[0])
        if unban_id in banned_users:
            banned_users.remove(unban_id)
            await update.message.reply_text(f"✅ کاربر {unban_id} آنبن شد.")
        else:
            await update.message.reply_text("❌ این کاربر در لیست بن نیست.")
    except:
        await update.message.reply_text("❌ آیدی معتبر نیست.")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠️ فقط ادمین می‌تواند آمار ربات را ببیند.")
        return
    total_users = len(user_ids)
    total_banned = len(banned_users)
    total_vip = len(vip_users)
    total_subscribed = len(subscribed_users)
    await update.message.reply_text(
        f"📊 آمار ربات:\n\n"
        f"👥 کل کاربران: {total_users}\n"
        f"🚫 بن شده‌ها: {total_banned}\n"
        f"💎 کاربران ویژه: {total_vip}\n"
        f"✅ کاربران تایید شده عضو کانال‌ها: {total_subscribed}"
    )

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⚠️ فقط ادمین می‌تواند پیام همگانی ارسال کند.")
        return
    await update.message.reply_text("📢 پیام همگانی را ارسال کن:")
    context.user_data['broadcast_mode'] = True

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addproxy", add_proxy))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(CommandHandler("broadcast", broadcast_start))

    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_user_msg))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
