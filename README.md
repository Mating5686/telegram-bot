AMG Telegram Bot

🚀 AMG Bot is a multi-functional Telegram bot built with Python and python-telegram-bot library.
It provides AI-powered chat, group management tools, and interactive features for both users and admins.

✨ Features

💬 Private Chat with Admin (AMG) — users can send messages, media, and get replies directly.

🧠 AI Assistant (GPT-3.5 via OpenRouter) — users with VIP access can ask questions and get intelligent answers.

🛡️ Anti-Link Protection — automatically deletes unwanted links in groups.

👋 Auto-Welcome System — greets new members in groups.

🌐 Proxy Sharing — admins can add and share updated proxies with users.

📜 Hafez Fortune Telling — provides random Hafez poems with interpretations.

🆘 Support Ticket System — users can submit issues or requests directly to admins.

🎮 Mini Game — number guessing game with limited/unlimited modes.

📊 Admin Panel — manage users (ban/unban), broadcast messages, add/remove admins, manage VIP users, and view bot stats.

📢 Sponsored Channel Membership Check — ensures users join sponsor channels before accessing features.

🛠️ Commands

/start – Start the bot and show the main menu.

/ask <question> – Ask the AI assistant (VIP users only).

/start_game – Start the number guessing game.

/exit_game – Exit the game.

/profile – Show your personal profile (join date, AI usage count).

/vipme – Check your referral status and VIP access.

👑 Admin Commands

/addproxy <proxy> / /removeproxy – Manage proxies.

/broadcast <message> – Send a message to all users.

/adminpanel – Open the admin panel.

/ban / /unban – Manage users.

/addchannel @channel / /removechannel @channel – Manage sponsor channels.

/addadmin <id> / /removeadmin <id> / /admins – Manage admin list.

/vipadd <id> / /vipremove <id> / /viplist – Manage VIP users.

⚙️ Setup

Clone this repository:

git clone https://github.com/yourusername/AMG-Telegram-Bot.git
cd AMG-Telegram-Bot


Install dependencies:

pip install -r requirements.txt


Create a .env file and add your Telegram Bot Token and OpenRouter API Key:

BOT_AMG=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key


Run the bot:

python BOT.py

📌 Notes

Requires Python 3.9+.

Works in both private chats and groups.

Some features (AI, proxies, etc.) are restricted to VIP users.

👤 Developer: @AMG_ir
🧠 AI Model: OpenRouter - GPT-3.5-Turbo
🔖 Version: v2.2.0-AR
📅 Release Date: 2025/07/16
