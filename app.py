import logging
import os
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application
from bot_logic import setup_application

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Configuration ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("BOT_TOKEN environment variable not set.")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://8000-isbaeyr18wnfwzr56fokg-8515846e.manusvm.computer{WEBHOOK_PATH}"

# --- Telegram Application Setup ---
application = setup_application(BOT_TOKEN)

# --- FastAPI Setup ---
app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Set the webhook URL on bot startup."""
    # Initialize the application
    await application.initialize()
    
    # Set the webhook URL
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logging.info(f"Webhook set to: {WEBHOOK_URL}")
    logging.info("FastAPI application started.")

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """Handle incoming Telegram updates via webhook."""
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        
        # Process the update directly
        await application.process_update(update)
            
        return Response(status_code=200)
    except Exception as e:
        logging.error(f"Error processing update: {e}")
        return Response(status_code=500)

@app.get("/")
async def root():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Telegram bot is running via webhook."}

@app.on_event("shutdown")
async def shutdown_event():
    """Clear the webhook on shutdown."""
    await application.bot.delete_webhook()
    logging.info("Webhook deleted on shutdown.")

