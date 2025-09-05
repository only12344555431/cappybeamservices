import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import html
import json

# Bot tokenınızı buraya ekleyin
BOT_TOKEN = "7664476297:AAFKYsvjCW318-A9N8FYurPD1fFtzwMFozU"

# Sorgu durumları
SELECT_CATEGORY, SELECT_SORGUTIPI, ENTER_PARAMETERS = range(3)

# Tüm sorgu tipleri ve API uç noktaları
SORGU_TIPLERI = {
    "temel": {
        "name": "Temel Sorgular",
        "sorgular": {
            "tcpro": {
                "api": "https://api.hexnox.pro/sowixapi/tcpro.php",
                "params": ["tc"],
                "display": "TC Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "adsoyadilice": {
                "api": "https://api.hexnox.pro/sowixapi/adsoyadilice.php",
                "params": ["ad", "soyad"],
                "display": "Ad Soyad Sorgu",
                "input_text": "Ad ve soyad girin (örn: Ahmet Yılmaz):"
            },
            "tcgsm": {
                "api": "https://api.hexnox.pro/sowixapi/tcgsm.php",
                "params": ["tc"],
                "display": "TC GSM Sorgu",
                "input_text": "TC kimlik no girin:"
            }
        }
    },
    "aile": {
        "name": "Aile Sorguları",
        "sorgular": {
            "anne": {
                "api": "https://api.hexnox.pro/sowixapi/anne.php",
                "params": ["tc"],
                "display": "Anne Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "baba": {
                "api": "https://api.hexnox.pro/sowixapi/baba.php",
                "params": ["tc"],
                "display": "Baba Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "cocuk": {
                "api": "http://api.hexnox.pro/sowixapi/cocuk.php",
                "params": ["tc"],
                "display": "Çocuk Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "sulale": {
                "api": "https://api.hexnox.pro/sowixapi/sulale.php",
                "params": ["tc"],
                "display": "Sülale Sorgu",
                "input_text": "TC kimlik no girin:"
            }
        }
    },
    "iletisim": {
        "name": "İletişim Sorguları",
        "sorgular": {
            "gsm": {
                "api": "https://api.hexnox.pro/sowixapi/gsm.php",
                "params": ["gsm"],
                "display": "GSM Sorgu",
                "input_text": "Telefon numarası girin (örn: 5551234567):"
            },
            "gsmdetay": {
                "api": "https://api.hexnox.pro/sowixapi/gsmdetay.php",
                "params": ["gsm"],
                "display": "GSM Detay Sorgu",
                "input_text": "Telefon numarası girin (örn: 5551234567):"
            },
            "operator": {
                "api": "https://api.hexnox.pro/sowixapi/operator.php",
                "params": ["gsm"],
                "display": "Operatör Sorgu",
                "input_text": "Telefon numarası girin (örn: 5551234567):"
            },
            "email_sorgu": {
                "api": "http://api.hexnox.pro/sowixapi/email_sorgu.php",
                "params": ["email"],
                "display": "Email Sorgu",
                "input_text": "Email adresi girin:"
            }
        }
    },
    "sosyal": {
        "name": "Sosyal Medya Sorguları",
        "sorgular": {
            "telegram_sorgu": {
                "api": "https://api.hexnox.pro/sowixapi/telegram_sorgu.php",
                "params": ["username"],
                "display": "Telegram Sorgu",
                "input_text": "Telegram kullanıcı adı girin:"
            },
            "facebook": {
                "api": "https://hexnox.pro/sowixfree/facebook.php",
                "params": ["numara"],
                "display": "Facebook Sorgu",
                "input_text": "Telefon numarası girin:"
            }
        }
    },
    "adres": {
        "name": "Adres Sorguları",
        "sorgular": {
            "adres": {
                "api": "https://api.hexnox.pro/sowixapi/adres.php",
                "params": ["tc"],
                "display": "Adres Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "tapu": {
                "api": "https://api.hexnox.pro/sowixapi/tapu.php",
                "params": ["tc"],
                "display": "Tapu Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "premadres": {
                "api": "https://hexnox.pro/sowixfree/premadres.php",
                "params": ["tc"],
                "display": "Premadres Sorgu",
                "input_text": "TC kimlik no girin:"
            }
        }
    },
    "arac": {
        "name": "Araç Sorguları",
        "sorgular": {
            "plaka": {
                "api": "http://hexnox.pro/sowixfree/plaka.php",
                "params": ["plaka"],
                "display": "Plaka Sorgu",
                "input_text": "Plaka no girin (örn: 34ABC123):"
            },
            "aracparca": {
                "api": "https://hexnox.pro/sowixfree/aracparca.php",
                "params": ["plaka"],
                "display": "Araç Parça Sorgu",
                "input_text": "Plaka no girin (örn: 34ABC123):"
            }
        }
    },
    "egitim": {
        "name": "Eğitim Sorguları",
        "sorgular": {
            "okulno": {
                "api": "https://api.hexnox.pro/sowixapi/okulno.php",
                "params": ["tc"],
                "display": "Okul No Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "lgs": {
                "api": "http://hexnox.pro/sowixfree/lgs/lgs.php",
                "params": ["tc"],
                "display": "LGS Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "diploma": {
                "api": "https://hexnox.pro/sowixfree/diploma/diploma.php",
                "params": ["tc"],
                "display": "Diploma Sorgu",
                "input_text": "TC kimlik no girin:"
            }
        }
    },
    "saglik": {
        "name": "Sağlık Sorguları",
        "sorgular": {
            "mhrs": {
                "api": "https://hexnox.pro/sowixfree/mhrs/mhrs.php",
                "params": ["tc"],
                "display": "MHRS Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "boy": {
                "api": "http://api.hexnox.pro/sowixapi/boy.php",
                "params": ["tc"],
                "display": "Boy Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "ayak": {
                "api": "http://api.hexnox.pro/sowixapi/ayak.php",
                "params": ["tc"],
                "display": "Ayak No Sorgu",
                "input_text": "TC kimlik no girin:"
            }
        }
    },
    "ozel": {
        "name": "Özel Sorgular",
        "sorgular": {
            "imei": {
                "api": "https://api.hexnox.pro/sowixapi/imei.php",
                "params": ["imei"],
                "display": "IMEI Sorgu",
                "input_text": "IMEI numarası girin:"
            },
            "interpol": {
                "api": "https://hexnox.pro/sowixfree/interpol.php",
                "params": ["ad", "soyad"],
                "display": "Interpol Sorgu",
                "input_text": "Ad ve soyad girin (örn: Ahmet Yılmaz):"
            },
            "burc": {
                "api": "http://api.hexnox.pro/sowixapi/burc.php",
                "params": ["tc"],
                "display": "Burç Sorgu",
                "input_text": "TC kimlik no girin:"
            },
            "havadurumu": {
                "api": "http://api.hexnox.pro/sowixapi/havadurumu.php",
                "params": ["sehir"],
                "display": "Hava Durumu Sorgu",
                "input_text": "Şehir adı girin (örn: İstanbul):"
            }
        }
    }
}

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botu başlatan komut."""
    user = update.effective_user

    # Kategori seçim butonları oluştur
    keyboard = []
    for category_id, category_data in SORGU_TIPLERI.items():
        keyboard.append([InlineKeyboardButton(category_data["name"], callback_data=f"category_{category_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👋 Merhaba {user.first_name}! Ben Sorgu Botuyum.\n\n"
        "Aşağıdan bir sorgu kategorisi seçin:",
        reply_markup=reply_markup
    )

    return SELECT_CATEGORY

async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kategori seçimini işler."""
    query = update.callback_query
    await query.answer()

    category_id = query.data.replace("category_", "")

    if category_id not in SORGU_TIPLERI:
        await query.edit_message_text("Geçersiz kategori seçimi.")
        return SELECT_CATEGORY

    # Seçilen kategoriye ait sorgu butonlarını oluştur
    keyboard = []
    for sorgu_id, sorgu_data in SORGU_TIPLERI[category_id]["sorgular"].items():
        keyboard.append([InlineKeyboardButton(sorgu_data["display"], callback_data=f"sorgu_{sorgu_id}")])

    # Geri butonu ekle
    keyboard.append([InlineKeyboardButton("◀️ Geri", callback_data="back_to_categories")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"📋 {SORGU_TIPLERI[category_id]['name']}\n\n"
        "Aşağıdan bir sorgu tipi seçin:",
        reply_markup=reply_markup
    )

    return SELECT_SORGUTIPI

async def sorgu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sorgu tipi seçimini işler."""
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_categories":
        # Kategori seçimine geri dön
        keyboard = []
        for category_id, category_data in SORGU_TIPLERI.items():
            keyboard.append([InlineKeyboardButton(category_data["name"], callback_data=f"category_{category_id}")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Aşağıdan bir sorgu kategorisi seçin:",
            reply_markup=reply_markup
        )
        return SELECT_CATEGORY

    sorgu_id = query.data.replace("sorgu_", "")

    # Sorgu tipini bul
    sorgu_data = None
    for category_id, category_data in SORGU_TIPLERI.items():
        if sorgu_id in category_data["sorgular"]:
            sorgu_data = category_data["sorgular"][sorgu_id]
            break

    if not sorgu_data:
        await query.edit_message_text("Geçersiz sorgu tipi seçimi.")
        return SELECT_SORGUTIPI

    # Sorgu tipini context'te sakla
    context.user_data["selected_sorgu"] = {
        "id": sorgu_id,
        "data": sorgu_data
    }

    await query.edit_message_text(
        f"🔍 {sorgu_data['display']}\n\n"
        f"{sorgu_data['input_text']}\n\n"
        "İşlemi iptal etmek için /cancel yazın."
    )

    return ENTER_PARAMETERS

async def parameters_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcıdan alınan parametreleri işler ve API'yi çağırır."""
    user_input = update.message.text
    selected_sorgu = context.user_data["selected_sorgu"]
    sorgu_data = selected_sorgu["data"]

    # Parametreleri ayır ve temizle
    params_list = [p.strip() for p in user_input.split()]
    required_params = sorgu_data["params"]

    if len(params_list) != len(required_params):
        await update.message.reply_text(
            f"❌ Eksik parametre! Lütfen {len(required_params)} parametre girin.\n\n"
            f"{sorgu_data['input_text']}\n\n"
            "İşlemi iptal etmek için /cancel yazın."
        )
        return ENTER_PARAMETERS

    # API'yi çağır
    api_url = sorgu_data["api"]
    query_params = {required_params[i]: params_list[i] for i in range(len(required_params))}

    try:
        # Sorgu yapılıyor mesajı
        processing_msg = await update.message.reply_text("⏳ Sorgunuz yapılıyor, lütfen bekleyin...")

        response = requests.get(api_url, params=query_params, timeout=30)

        if response.status_code == 200:
            result = response.text

            # JSON formatında ise düzenle
            try:
                if result.strip().startswith('{') or result.strip().startswith('['):
                    json_data = json.loads(result)
                    formatted_result = json.dumps(json_data, indent=2, ensure_ascii=False)
                    result = f"<pre>{html.escape(formatted_result)}</pre>"
            except:
                pass

            # Eğer sonuç boşsa veya hata içeriyorsa
            if not result or "error" in result.lower() or "hata" in result.lower():
                result = "❌ Sorgu sonucu bulunamadı veya bir hata oluştu."

            # Sonucu göster
            await processing_msg.edit_text(
                f"✅ <b>{sorgu_data['display']} Sonucu:</b>\n\n"
                f"{result}\n\n"
                "Yeni sorgu yapmak için /sorgu yazın.",
                parse_mode="HTML"
            )
        else:
            await processing_msg.edit_text(
                "❌ Sorgu sırasında bir hata oluştu. API yanıt vermedi.\n\n"
                "Yeni sorgu yapmak için /sorgu yazın."
            )

    except Exception as e:
        logger.error(f"API çağrısı sırasında hata: {e}")
        await processing_msg.edit_text(
            "❌ Sorgu sırasında bir hata oluştu. Lütfen daha sonra tekrar deneyin.\n\n"
            "Yeni sorgu yapmak için /sorgu yazın."
        )

    # Kullanıcı verilerini temizle
    if "selected_sorgu" in context.user_data:
        del context.user_data["selected_sorgu"]

    return -1

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sorgu işlemini iptal eder."""
    # Kullanıcı verilerini temizle
    if "selected_sorgu" in context.user_data:
        del context.user_data["selected_sorgu"]

    await update.message.reply_text(
        "❌ Sorgu işlemi iptal edildi.\n\n"
        "Yeni sorgu yapmak için /sorgu yazın."
    )

    return -1

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yardım komutunu işler."""
    await update.message.reply_text(
        "🤖 <b>Sorgu Botu Kullanım Kılavuzu</b>\n\n"
        "• <b>/start</b> - Botu başlatır\n"
        "• <b>/sorgu</b> - Sorgu yapmaya başlar\n"
        "• <b>/cancel</b> - Mevcut işlemi iptal eder\n"
        "• <b>/help</b> - Yardım mesajını gösterir\n\n"
        "Sorgu yapmak için /sorgu komutunu kullanın ve açılan menülerden istediğiniz sorgu tipini seçin.",
        parse_mode="HTML"
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Düğme tıklamalarını işler."""
    query = update.callback_query
    await query.answer()
    await query.edit_messaAge_text(text=f"Seçilen seçenek: {query.data}")

def main():
    """Botu başlatır."""
    # Application oluştur
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers ekle
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sorgu", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CallbackQueryHandler(category_handler, pattern="^category_"))
    application.add_handler(CallbackQueryHandler(sorgu_handler, pattern="^sorgu_"))
    application.add_handler(CallbackQueryHandler(sorgu_handler, pattern="^back_to_categories"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, parameters_handler))

    # Botu çalıştır
    application.run_polling()

if __name__ == "__main__":
    main()

