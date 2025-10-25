import os
import logging
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# === Настройки ===
# BOT_TOKEN will be read from environment variables or passed during setup
# BASE_DIR is now the current working directory
BASE_DIR = Path(".")

# Список товаров: (название, цена, имя файла)
PRODUCTS = [
    ("Штаны Amiri", 2890, "amiri_pants.jpg"),
    ("Худи Hellstar", 2990, "hellstar_hoodie.jpg"),
    ("Nike Air Force Off White", 12900, "nike_offwhite.jpg"),
    ("Balenciaga Track", 7890, "balenciaga_track.jpg"),
    ("Рюкзак Sprayground", 10890, "sprayground_backpack.jpg"),
    ("Balenciaga Track Bordeaux", 8890, "balenciaga_bordeaux.jpg"),
    ("Salomon XT-6 GTX", 5490, "salomon_xt6.jpg"),
]

# Path to the logo - assuming 'photo_2025-10-25_15-22-53.jpg' is the logo
# I will rename 'photo_2025-10-25_15-22-53.jpg' to 'logo.jpg' for clarity and use it as the logo
LOGO_PATH = BASE_DIR / "logo.jpg"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Отправляем логотип
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as logo:
            await update.message.reply_photo(photo=logo)
    else:
        await update.message.reply_text("⚠️ Логотип не найден.")

    # Кнопки товаров
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"product_{i}")]
        for i, (name, _, _) in enumerate(PRODUCTS)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔥 Выберите товар из каталога CRANKSTORE:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("product_"):
        index = int(query.data.split("_")[1])
        name, price, photo_name = PRODUCTS[index]
        photo_path = BASE_DIR / photo_name  # ← Фото ищем в корне папки!

        if not photo_path.exists():
            await query.message.reply_text(f"❌ Фото для {name} не найдено. Путь: {photo_path}")
            return

        caption = (
            f"**{name}**\n"
            f"Цена: {price} ₽\n\n"
            f"📍 Магазин: [@krank66](https://t.me/krank66)\n"
            f"👤 Менеджер: [@junkmafia](https://t.me/junkmafia)\n\n"
            f"Напишите менеджеру для оформления заказа!"
        )
        with open(photo_path, "rb") as photo:
            await query.message.reply_photo(photo=photo, caption=caption, parse_mode="Markdown")

        # Повторно показываем меню после выбора
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"product_{i}")]
            for i, (name, _, _) in enumerate(PRODUCTS)
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите другой товар:", reply_markup=reply_markup)

def setup_application(token: str) -> Application:
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    return application

# Removed main() and application.run_polling() for webhook deployment
# The token is expected to be passed from the main deployment file

