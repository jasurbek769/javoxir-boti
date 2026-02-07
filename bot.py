import telebot
from telebot import types
import time

# ================= SOZLAMALAR =================
TOKEN = "8520853563:AAHIeut62ZZeUC22FTYWJHBEIo9WR670Ux0"
ADMIN_ID = 7950261926
CALL_PHONE = "+998945061080"
# ==============================================

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
user_data = {}

# ========== ADMIN GA YUBORISH ==========
def notify_admin(text):
    try:
        bot.send_message(ADMIN_ID, text)
    except:
        pass

# ========== START ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_data.pop(message.chat.id, None)

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
        "🏛 <b>TEXNIK XIZMAT MUROJAAT BOTI</b>\n\n"
        "Iltimos, nosozlik bo‘lgan qurilmani tanlang:",
        reply_markup=markup
    )

# ========== ADMIN PANEL ==========
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.chat.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔ Siz admin emassiz!")
        return

    bot.send_message(
        message.chat.id,
        "👨‍💼 <b>ADMIN PANEL</b>\n\n"
        "• Barcha murojaatlar shu bot orqali keladi\n"
        "• Yarim murojaatlar ham yo‘qolmaydi\n"
        "• Bot barqaror ishlayapti ✅"
    )

# ========== ADMIN ID ==========
@bot.message_handler(commands=['myid'])
def myid(message):
    bot.send_message(message.chat.id, f"Sizning ID: <b>{message.chat.id}</b>")

# ========== QO‘NG‘IROQ ==========
@bot.message_handler(func=lambda m: m.text == "📞 Texnik xizmatga qo‘ng‘iroq qilish")
def call_service(message):
    inline = types.InlineKeyboardMarkup()
    inline.add(types.InlineKeyboardButton("📞 Qo‘ng‘iroq qilish", callback_data="CALL_PHONE"))

    bot.send_message(
        message.chat.id,
        f"📞 Texnik xizmat raqami:\n<b>{CALL_PHONE}</b>",
        reply_markup=inline
    )

@bot.callback_query_handler(func=lambda call: call.data == "CALL_PHONE")
def call_phone(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"📞 Qo‘ng‘iroq uchun raqam:\n<b>{CALL_PHONE}</b>")

# ========== QURILMALAR ==========
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
    user_data[message.chat.id] = {
        "device": message.text,
        "problem": None,
        "location": None,
        "time": time.strftime("%d.%m.%Y %H:%M")
    }

    notify_admin(
        f"🟡 <b>YANGI MUROJAAT BOSHLANDI</b>\n"
        f"👤 {message.from_user.full_name}\n"
        f"🔧 {message.text}\n"
        f"🆔 {message.chat.id}"
    )

    bot.send_message(message.chat.id, "📝 Muammoni qisqacha yozib bering:")
    bot.register_next_step_handler(message, get_problem)

def get_problem(message):
    if message.chat.id not in user_data:
        return

    user_data[message.chat.id]["problem"] = message.text
    bot.send_message(message.chat.id, "📍 Joylashuvni kiriting:")
    bot.register_next_step_handler(message, get_location)

def get_location(message):
    if message.chat.id not in user_data:
        return

    user_data[message.chat.id]["location"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True))

    bot.send_message(
        message.chat.id,
        "📞 Aloqa uchun telefon raqamingizni yuboring:",
        reply_markup=markup
    )

# ========== CONTACT → YAKUNIY ==========
@bot.message_handler(content_types=['contact'])
def get_contact(message):
    data = user_data.get(message.chat.id, {})

    admin_text = (
        "📥 <b>YANGI TEXNIK MUROJAAT</b>\n\n"
        f"👤 {message.from_user.full_name}\n"
        f"📞 {message.contact.phone_number}\n"
        f"🔧 {data.get('device','-')}\n"
        f"📝 {data.get('problem','-')}\n"
        f"📍 {data.get('location','-')}\n"
        f"🕒 {data.get('time','-')}\n"
        f"🆔 {message.chat.id}"
    )

    notify_admin(admin_text)

    bot.send_message(
        message.chat.id,
        "✅ <b>Murojaatingiz qabul qilindi!</b>\n\n"
        "Texnik xodimlar tez orada siz bilan bog‘lanadi.",
        reply_markup=types.ReplyKeyboardRemove()
    )

    user_data.pop(message.chat.id, None)

# ========== FALLBACK (ADMIN BUYRUQLARIGA TEGMAYDI) ==========
@bot.message_handler(
    func=lambda m: (
        m.chat.id in user_data and
        not m.text.startswith("/") and
        m.text not in DEVICES
    )
)
def fallback(message):
    data = user_data.get(message.chat.id)

    notify_admin(
        "⚠️ <b>YARIM MUROJAAT</b>\n"
        f"👤 {message.from_user.full_name}\n"
        f"🆔 {message.chat.id}\n"
        f"🔧 {data.get('device')}\n"
        f"📝 {data.get('problem')}\n"
        f"📍 {data.get('location')}\n"
        f"✍️ Oxirgi xabar: {message.text}"
    )

# ========== ISHGA TUSHIRISH ==========
bot.remove_webhook()
bot.infinity_polling()
