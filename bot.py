import os
import sys
import io
import asyncio
import contextlib
import html
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Pull API keys from Koyeb Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("Missing TELEGRAM_TOKEN environment variable.")

# Add the cloned repo to the Python path
sys.path.append('/app/Missminute1')

# --- IMPORT YOUR ACTUAL OPENCLAW FUNCTION HERE ---
# You must replace this with the actual import from your fork.
# Example: from openclaw.main import run_agent


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello Max! Missminute1 is deployed. Send me a task and I will execute it using OpenClaw.")


def run_openclaw_sync(user_text, string_buffer):
    """
    This function runs in a separate thread. It redirects all terminal output 
    (print statements) into a buffer that the Telegram bot reads from.
    """
    # Redirect standard output and errors into our buffer
    with contextlib.redirect_stdout(string_buffer), contextlib.redirect_stderr(string_buffer):
        try:
            print(f"--- Triggering OpenClaw Intent: {user_text} ---\n")
            print("Initializing agent tools and ReAct loop...\n")
            
            # --- EXECUTE OPENCLAW ---
            # Replace this placeholder block with your actual function call!
            # Example: 
            # run_agent(user_text) 
            
            # --- START PLACEHOLDER (Remove when integrating) ---
            import time
            time.sleep(2)
            print("> [Thought] Need to analyze the request.")
            time.sleep(2)
            print("> [Action] Loading browser module...")
            time.sleep(3)
            print("> [Observation] Successfully navigated to target.")
            # --- END PLACEHOLDER ---

            print("\nExecution phase completed.")
            return True
            
        except Exception as e:
            print(f"\n[CRITICAL ERROR] Agent crashed: {str(e)}")
            return False


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # 1. Send an initial message that we will update like a live dashboard
    status_message = await update.message.reply_text("⚙️ Booting up OpenClaw engine...")
    
    string_buffer = io.StringIO()
    loop = asyncio.get_running_loop()
    
    # 2. Start the heavy OpenClaw execution in a background thread so the bot doesn't freeze
    task = loop.run_in_executor(None, run_openclaw_sync, user_text, string_buffer)
    
    last_text = ""
    
    # 3. The "Heartbeat" Loop: Update Telegram with the live logs while the task runs
    while not task.done():
        await asyncio.sleep(2.5) # Update every 2.5 seconds to respect Telegram API rate limits
        
        current_log = string_buffer.getvalue()
        if not current_log:
            continue
            
        # Telegram has a 4096 character limit. Keep only the most recent logs.
        if len(current_log) > 3500:
            display_text = "...\n" + current_log[-3500:]
        else:
            display_text = current_log
            
        if display_text != last_text:
            try:
                # Use HTML to safely format the logs without breaking Telegram's parser
                escaped_text = html.escape(display_text)
                await status_message.edit_text(
                    f"<b>🧠 Agent Thinking...</b>\n<pre>{escaped_text}</pre>", 
                    parse_mode="HTML"
                )
                last_text = display_text
            except Exception:
                # Ignore errors if the text hasn't changed enough to trigger an update
                pass
                
    # 4. Task is finished. Grab the final output.
    await task 
    final_log = string_buffer.getvalue()
    final_display = final_log[-3500:] if len(final_log) > 3500 else final_log
    escaped_final = html.escape(final_display)
    
    await status_message.edit_text(
        f"<b>✅ Task Complete</b>\n\n<b>Terminal Logs:</b>\n<pre>{escaped_final}</pre>", 
        parse_mode="HTML"
    )

def main():
    print("Starting Telegram Bot with Live Agent Logging...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
