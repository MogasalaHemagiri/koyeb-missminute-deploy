import os
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Pull API keys from Koyeb Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("Missing TELEGRAM_TOKEN or GROQ_API_KEY environment variables.")

groq_client = Groq(api_key=GROQ_API_KEY)

# Add the cloned repo to the Python path so you can import its modules
sys.path.append('/app/Missminute1')
# Example: from openclaw.main import run_task 

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello Max! Missminute1 is deployed and listening.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        # Route the command through Groq (using Llama 3 for speed)
        completion = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a specialized agent orchestrating tasks for an OpenClaw system."},
                {"role": "user", "content": user_text}
            ]
        )
        llm_response = completion.choices[0].message.content

        # --- OPENCLAW INTEGRATION POINT ---
        # Here is where you pass the parsed intent to your cloned repo:
        # result = run_task(llm_response)
        # await update.message.reply_text(f"Task Output:\n{result}")

        await update.message.reply_text(f"Groq Processed Intent:\n{llm_response}")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

def main():
    print("Starting Telegram Bot...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Run in polling mode so you don't have to deal with Webhook URLs
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

