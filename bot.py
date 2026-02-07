import telebot
from telebot import types
import os

# ========== SOZLAMALAR ==========
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CALL_PHONE = os.getenv("CALL_PHONE")
# ===============================

bot = telebot.TeleBot(TOKEN)
user_data = {}

# ========== START ==========
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        "❄️ Konditsioner",
        "🧊 Muzlatkich",
        "🔥 Ariston",
        "📷 Kuzatuv kamerasi",
        "🌀 Kir yuvish mashinasi",
        "📺 Televizor",
        "⚡ Boshqa elektr jihozlar",
        "📞 Texnik xizmatga qo‘ng‘iroq qilish"
    )

    bot.send_message(
        message.chat.id,
        "🏛 TEXNIK XIZMAT MUROJAAT BOTI\n\n"
        "Iltimos, nosozlik bo‘lgan qurilmani tanlang:",
        reply_markup=markup
    )

# ========== QO‘NG‘IROQ ==========
@bot.message_handler(func=lambda m: m.text == "📞 Texnik xizmatga qo‘ng‘iroq qilish")
def call_service(message):
    inline = types.InlineKeyboardMarkup()
    inline.add(
        types.InlineKeyboardButton(
            "📞 Qo‘ng‘iroq qilish",
            callback_data="CALL_SERVICE_PHONE"
        )
    )

    bot.send_message(
        message.chat.id,
        f"📞 Texnik xizmat raqami:\n{CALL_PHONE}",
        reply_markup=inline
    )

@bot.callback_query_handler(func=lambda call: call.data == "CALL_SERVICE_PHONE")
def call_service_phone(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"📞 Qo‘ng‘iroq uchun raqam:\n{CALL_PHONE}")

# ========== QURILMA TANLASH ==========
DEVICES = [
    "❄️ Konditsioner",
    "🧊 Muzlatkich",
    "🔥 Ariston",
    "📷 Kuzatuv kamerasi",
    "🌀 Kir yuvish mashinasi",
    "📺 Televizor",
    "⚡ Boshqa elektr jihozlar"
]

@bot.message_handler(func=lambda m: m.text in DEVICES)
def device_selected(message):
    user_data[message.chat.id] = {"device": message.text}
    bot.send_message(message.chat.id, "📝 Muammoni qisqacha yozib bering:")
    bot.register_next_step_handler(message, get_problem)

def get_problem(message):
    user_data[message.chat.id]["problem"] = message.text
    bot.send_message(message.chat.id, "📍 Joylashuvni kiriting:\n(bino, qavat, xona)")
    bot.register_next_step_handler(message, get_location)

def get_location(message):
    user_data[message.chat.id]["location"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))

    bot.send_message(
        message.chat.id,
        "📞 Aloqa uchun telefon raqamingizni yuboring:",
        reply_markup=markup
    )

# ========== CONTACT ==========
@bot.message_handler(content_types=['contact'])
def get_contact(message):
    data = user_data.get(message.chat.id)

    admin_text = (
        "📥 YANGI TEXNIK MUROJAAT\n\n"
        f"👤 Foydalanuvchi: {message.from_user.full_name}\n"
        f"📞 Telefon: {message.contact.phone_number}\n"
        f"🔧 Qurilma: {data['device']}\n"
        f"📝 Muammo: {data['problem']}\n"
        f"📍 Joylashuv: {data['location']}\n"
        f"🆔 Chat ID: {message.chat.id}"
    )

    bot.send_message(ADMIN_ID, admin_text)

    bot.send_message(
        message.chat.id,
        "✅ Murojaatingiz qabul qilindi.\n"
        "Texnik xodimlar tez orada bog‘lanadi.",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ========== ADMIN ==========
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ Siz admin emassiz!")
        return

    bot.send_message(
        message.chat.id,
        "👨‍💼 ADMIN PANEL\n\nBot normal ishlayapti ✅"
    )

@bot.message_handler(commands=['myid'])
def myid(message):
    bot.send_message(message.chat.id, f"Sizning ID: {message.chat.id}")

# ========== ISHGA TUSHIRISH ==========
bot.remove_webhook()
bot.infinity_polling()
