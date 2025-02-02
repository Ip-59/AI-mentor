
import json
import os
from telegram import Update, Bot, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging

# Path to the JSON file
JSON_FILE_PATH = "neuro_assistant_data.json"

# Load or initialize JSON data
def load_data():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, "r") as file:
            return json.load(file)
    return {"users": [], "progress": {}, "achievements": {}}

def save_data(data):
    with open(JSON_FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

data = load_data()

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
REGISTER, MAIN_MENU = range(2)

# Start handler
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    context.user_data["username"] = user.username
    update.message.reply_text(f"Welcome, {user.first_name}! Use /register to create your profile.")
    return REGISTER

# Registration handler
def register(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    if not any(u["username"] == user.username for u in data["users"]):
        new_user = {
            "username": user.username,
            "name": user.first_name,
            "registration_date": "2024-01-01T12:00:00Z",
            "level": 1,
            "total_points": 0
        }
        data["users"].append(new_user)
        data["progress"][user.username] = {"lectures_completed": [], "quizzes_completed": []}
        data["achievements"][user.username] = []
        save_data(data)
        update.message.reply_text("Registration successful! Use /menu to see options.")
    else:
        update.message.reply_text("You are already registered. Use /menu to continue.")
    return MAIN_MENU

# Menu handler
def menu(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Main Menu:\n"
        "1. /lecture - Start a lecture\n"
        "2. /quiz - Take a quiz\n"
        "3. /progress - View your progress"
    )
    return MAIN_MENU

# Placeholder handlers for lecture and quiz
def lecture(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Lecture content placeholder.")

def quiz(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Quiz placeholder.")

def progress(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    user_progress = data["progress"].get(username, {"lectures_completed": [], "quizzes_completed": []})
    update.message.reply_text(
        f"Progress:\n"
        f"Lectures completed: {len(user_progress['lectures_completed'])}\n"
        f"Quizzes completed: {len(user_progress['quizzes_completed'])}"
    )

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

# Main function
def main():
    TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REGISTER: [CommandHandler("register", register)],
            MAIN_MENU: [
                CommandHandler("menu", menu),
                CommandHandler("lecture", lecture),
                CommandHandler("quiz", quiz),
                CommandHandler("progress", progress),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
