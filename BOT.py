import requests
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram import ChatMember

# تنظیمات
ADMIN_ID = 6807376124
TOKEN = "8183707654:AAGqEcAConlQICPB3sGdbZ5aDMtrVpPHdKQ"
OPENROUTER_API_KEY = "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"

# کانال‌های اسپانسر
SPONSORED_CHANNELS = [
    "@starssell_ir",  # لینک کانال اول اسپانسر
    "@starssell_ir"   # لینک کانال دوم اسپانسر
]

# کاربران خاص
special_users = {
    6807376124: " سلام آدریانو! به منطقه ویژه خودت خوش اومدی.",
    1296533127: "به به سلام عباس نفسم یه دست برامون بخون",
    5692880940: "عه سلام هلی کوشولو چی میخوای بهم بگی؟",
    6543935749: "سلام به به چه کون طلایی چی‌ میخوای بهم بگی؟",
    5880712187: "عه سلام مساجد چی میخوای بهم بگی؟",
    7506391284: "این اومده یعنی درسته نگران نباش"
}

# کاربران VIP
vip_users = set()
anti_link_groups = set()
proxy_list = []

# لیست کاربران و بن‌شده‌ها
user_ids = set()  # لیست کاربران ثبت‌شده
banned_users = set()  # لیست کاربران بن‌شده
tickets = {}  # تیکت‌ها: user_id -> متن

# استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    inline_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(" افزودن به گروه", url=f"https://t.me/{context.bot.username}?startgroup=true")],
        [InlineKeyboardButton(" فعال‌سازی ضد لینک", callback_data="enable_anti_link")],
        [InlineKeyboardButton(" چت با AMG", callback_data="chat_amg")],
        [InlineKeyboardButton(" اطلاعات ربات", callback_data="bot_info")],
        [InlineKeyboardButton(" درخواست پشتیبانی", callback_data="support")]  # دکمه درخواست پشتیبانی اضافه شد
    ])
    # نمایش کانال‌های اسپانسر در منوی شیشه‌ای
    channels_buttons = [
        [InlineKeyboardButton(f" پیوستن به کانال {channel[1:]}", url=f"https://t.me/{channel[1:]}")]
        for channel in SPONSORED_CHANNELS
    ]
    channels_buttons.append([InlineKeyboardButton(" درخواست پشتیبانی", callback_data="support")])
    reply_keyboard = ReplyKeyboardMarkup([
        [" چت با AMG"],
        [" سفارش تبلیغ"],
        [" دریافت پروکسی"],
        [" چت با هوش مصنوعی"],
        [" اطلاعات ربات"]
    ], resize_keyboard=True)
    await update.message.reply_text("سلام! یکی از گزینه‌ها رو انتخاب کن:", reply_markup=reply_keyboard)
    await update.message.reply_text(" منوی ویژه:", reply_markup=inline_keyboard)
    await update.message.reply_text(" کانال‌های اسپانسر:", reply_markup=InlineKeyboardMarkup(channels_buttons))
    user_ids.add(update.effective_user.id)  # ثبت کاربر جدید

# بررسی عضویت در کانال
async def check_channel_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    for channel in SPONSORED_CHANNELS:
        chat_member = await context.bot.get_chat_member(channel, user_id)
        if chat_member.status != ChatMember.MEMBER:
            return False  # کاربر عضو نیست
    return True  # کاربر عضو همه کانال‌ها است

# دکمه‌های شیشه‌ای
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "enable_anti_link":
        chat = query.message.chat
        if chat.type in ["supergroup", "group"]:
            anti_link_groups.add(chat.id)
            await query.edit_message_text(" ضد لینک در این گروه فعال شد.")
        else:
            await query.edit_message_text(" فقط تو گروه می‌تونی ضد لینک فعال کنی.")
    elif query.data == "chat_amg":
        if user_id in special_users:
            await query.message.reply_text(special_users[user_id])
        else:
            await query.message.reply_text(" پیام‌تو بنویس، AMG جواب می‌ده.")
        context.user_data['chat_amg'] = True
    elif query.data == "bot_info":
        await query.message.reply_text(
            " اطلاعات ربات:\n\n"
            " نام: 𓄂AMG𓆃\n"
            " قابلیت‌ها:\n"
            " ├─ چت خصوصی با ادمین (AMG)\n"
            " ├─ پاسخگویی با هوش مصنوعی GPT-3.5\n"
            " ├─ ضد لینک هوشمند مخصوص گروه‌ها\n"
            " ├─ خوش‌آمدگویی خودکار به اعضای جدید\n"
            " └─ ارائه پروکسی‌های به‌روز و امن\n\n"
            " سازنده: @AMG_ir (AMG)\n"
            " مدل هوش مصنوعی: OpenRouter - GPT-3.5-Turbo\n"
            " نسخه ربات: v2.1.3-AR (AMG Release)\n"
            " تاریخ انتشار: ۲۰۲۵/۰۷/۱۰"
        )
    elif query.data == "support":
        await query.message.reply_text(" درخواست پشتیبانی شما ثبت شد. لطفاً سوال یا مشکل خود را ارسال کنید.")
        tickets[user_id] = "درخواست پشتیبانی ثبت شده"

# پیام کاربران
async def handle_user_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id in banned_users:
        return  # اگر کاربر بن شده، هیچ پیامی ارسال نمی‌شود

    if text == " چت با AMG":
        if user_id in special_users:
            await update.message.reply_text(special_users[user_id])
        else:
            await update.message.reply_text(" پیام‌تو برای AMG بنویس.")
        context.user_data['chat_amg'] = True

    elif text == " سفارش تبلیغ":
        await update.message.reply_text(" لطفاً نوع تبلیغ و توضیحاتت رو کامل بفرست.")

    elif text == " دریافت پروکسی":
        if proxy_list:
            proxies = "\n".join(proxy_list[-5:])  # آخرین ۵ پروکسی
            await update.message.reply_text(f" پروکسی‌های جدید:\n\n{proxies}")
        else:
            await update.message.reply_text(" هنوز پروکسی‌ای ثبت نشده.")

    elif text == " چت با هوش مصنوعی":
        if await check_channel_membership(user_id, context):
            await update.message.reply_text("سوالت رو با دستور `/ask سوال تو` بپرس ")
        else:
            await update.message.reply_text(" برای استفاده از هوش مصنوعی، باید در کانال‌های اسپانسر عضو بشی.\n\nلیست کانال‌ها:\n" +
                                            "\n".join([f" پیوستن به کانال {channel[1:]}" for channel in SPONSORED_CHANNELS]))

    elif text == " اطلاعات ربات":
        await update.message.reply_text(
            " اطلاعات ربات:\n\n"
            " نام: 𓄂AMG𓆃\n"
            " قابلیت‌ها:\n"
            " ├─ چت خصوصی با ادمین (AMG)\n"
            " ├─ پاسخگویی با هوش مصنوعی GPT-3.5\n"
            " ├─ ضد لینک هوشمند مخصوص گروه‌ها\n"
            " ├─ خوش‌آمدگویی خودکار به اعضای جدید\n"
            " └─ ارائه پروکسی‌های به‌روز و امن\n\n"
            " سازنده: @amg_ai (Zed | Matin Do Hanjare)\n"
            " مدل هوش مصنوعی: OpenRouter - GPT-3.5-Turbo\n"
            " نسخه ربات: v2.1.3-AR (AMG Release)\n"
            " تاریخ انتشار: ۲۰۲۵/۰۷/۱۰"
        )

    elif context.user_data.get('chat_amg'):
        await context.bot.send_message(ADMIN_ID, f" پیام از {user_id}:\n{text}")
        await update.message.reply_text(" پیام‌ت برای AMG فرستاده شد.")
        context.user_data['chat_amg'] = False

    elif user_id == ADMIN_ID and update.message.reply_to_message:
        try:
            target_id = int(update.message.reply_to_message.text.split()[2].strip(":"))
            await context.bot.send_message(target_id, text)
            await update.message.reply_text(" پیام به کاربر ارسال شد.")
        except:
            await update.message.reply_text(" ارسال نشد. ساختار پیام پاسخ درست نیست.")
    else:
        await update.message.reply_text("لطفاً از منو استفاده کن.")

# ضد لینک
async def anti_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in anti_link_groups:
        text = update.message.text
        if any(link in text for link in ["t.me/", "http://", "https://"]):
            try:
                await update.message.delete()
            except:
                pass

# خوش‌آمدگویی
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f" خوش اومدی {member.full_name}!")

# دستور /ask برای هوش مصنوعی
async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)
    if not question:
        await update.message.reply_text(" لطفاً سوالت رو بعد از /ask بنویس.")
        return

    try:
        await update.message.chat.send_action(action="typing")
        response = requests.post(
            "https://api.openrouter.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [{"role": "user", "content": question}]
            }
        )
        if response.status_code == 200:
            data = response.json()
            answer = data['choices'][0]['message']['content']
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text(" خطا در ارتباط با سرور OpenRouter.")
    except Exception as e:
        await update.message.reply_text(f" خطا در پاسخگویی: {e}")

# اجرا
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask_ai))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, anti_link))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_user_msg))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print(" ربات 𓄂AMG𓆃 روشن شد!")
    app.run_polling()
main()
