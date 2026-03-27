import os
import subprocess
import asyncio
import html
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Pull API keys from Koyeb Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("Missing TELEGRAM_TOKEN environment variable.")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello Max! OpenClaw is connected via terminal. Send me a command.")

def run_openclaw_sync(user_text, log_list):
    """
    Runs the OpenClaw system via a terminal command and captures the live output.
    This acts exactly like a human typing into the server console.
    """
    try:
        log_list.append(f"--- Executing Command: {user_text} ---\n")
        log_list.append("Firing up Node.js OpenClaw environment...\n")
        
        # THE MAGIC CLI TRIGGER
        # This calls the exact file specified in your package.json's "bin"
        command = ["node", "scripts/run-node.mjs", user_text]
        
        # Start the terminal process inside your cloned repo folder
        process = subprocess.Popen(
            command,
            cwd="/app/Missminute1",  
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge errors into standard output
            text=True,
            bufsize=1  # Line buffered so we get updates instantly
        )
        
        # Read the terminal output line-by-line in real-time
        for line in process.stdout:
            log_list.append(line)
            
        process.wait() # Wait for the agent to finish its job

        if process.returncode == 0:
            log_list.append("\n✅ Process finished naturally.")
        else:
            log_list.append(f"\n❌ Process exited with error code {process.returncode}")
            
    except Exception as e:
        log_list.append(f"\n[CRITICAL ERROR] Failed to run terminal command: {str(e)}\n")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Send the initial dashboard message
    status_message = await update.message.reply_text("⚙️ Interfacing with server terminal...")
    
    # We use a list instead of StringIO for better thread-safety when appending logs
    log_list = []
    loop = asyncio.get_running_loop()
    
    # Start the heavy terminal execution in a background thread
    task = loop.run_in_executor(None, run_openclaw_sync, user_text, log_list)
    
    last_text = ""
    
    # The Heartbeat Loop: Update Telegram with the live logs every 2.5 seconds
    while not task.done():
        await asyncio.sleep(2.5) 
        
        current_log = "".join(log_list)
        if not current_log:
            continue
            
        # Telegram has a 4096 character limit. Keep only the most recent logs.
        if len(current_log) > 3500:
            display_text = "...\n" + current_log[-3500:]
        else:
            display_text = current_log
            
        if display_text != last_text:
            try:
                # Use HTML to safely format the logs without breaking Telegram's markdown
                escaped_text = html.escape(display_text)
                await status_message.edit_text(
                    f"<b>🖥️ Live Terminal...</b>\n<pre>{escaped_text}</pre>", 
                    parse_mode="HTML"
                )
                last_text = display_text
            except Exception:
                # Ignore minor update errors
                pass
                
    # Task is finished. Grab the final output.
    await task 
    final_log = "".join(log_list)
    final_display = final_log[-3500:] if len(final_log) > 3500 else final_log
    escaped_final = html.escape(final_display)
    
    await status_message.edit_text(
        f"<b>✅ Task Complete</b>\n\n<b>Final Terminal Logs:</b>\n<pre>{escaped_final}</pre>", 
        parse_mode="HTML"
    )

def main():
    print("Starting Telegram Bot (Subprocess Mode)...")
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
