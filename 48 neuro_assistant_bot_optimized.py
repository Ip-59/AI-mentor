
import json
import os
import logging
from threading import Lock
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler

# Path to the JSON file
JSON_FILE_PATH = "neuro_assistant_data.json"
LOCK = Lock()

# Logging setup
logging.basicConfig(filename="bot_logs.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

# Load or initialize JSON data
def load_data():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, "r") as file:
            return json.load(file)
    return {"users": []}

def save_data(data):
    with LOCK:  # Ensuring thread-safe writes
        with open(JSON_FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)

data = load_data()

# Conversation states
REGISTER, MAIN_MENU = range(2)

# Helper function to check if user is registered
def is_registered(username):
    return any(user["username"] == username for user in data["users"])

# Helper function to get user data
def get_user(username):
    return next((user for user in data["users"] if user["username"] == username), None)

# Commands
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    context.user_data["username"] = user.username
    logger.info(f"User {user.username} started interaction.")
    update.message.reply_text("Welcome! Use /register to create your profile.")
    return REGISTER

def register(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    if not is_registered(user.username):
        new_user = {
            "username": user.username,
            "name": user.first_name,
            "registration_date": "2024-01-01T12:00:00Z",
            "level": 1,
            "total_points": 0,
            "active": True,
            "progress": {"lectures_completed": [], "quizzes_completed": []},
            "achievements": []
        }
        data["users"].append(new_user)
        save_data(data)
        logger.info(f"User {user.username} registered successfully.")
        update.message.reply_text("Registration complete! Use /menu to see options.")
    else:
        update.message.reply_text("You are already registered. Use /menu to continue.")
    return MAIN_MENU

def menu(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Main Menu:\n"
        "1. /lecture - Start a lecture\n"
        "2. /quiz - Take a quiz\n"
        "3. /progress - View your progress"
    )
    return MAIN_MENU

def lecture(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    user = get_user(username)
    if not user:
        update.message.reply_text("You need to register first with /register.")
        return
    user["progress"]["lectures_completed"].append("Lecture 1")
    save_data(data)
    logger.info(f"User {username} completed a lecture.")
    update.message.reply_text("Lecture completed!")

def quiz(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    user = get_user(username)
    if not user:
        update.message.reply_text("You need to register first with /register.")
        return
    user["progress"]["quizzes_completed"].append("Quiz 1")
    save_data(data)
    logger.info(f"User {username} completed a quiz.")
    update.message.reply_text("Quiz completed!")

def progress(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    user = get_user(username)
    if not user:
        update.message.reply_text("You need to register first with /register.")
        return
    update.message.reply_text(
        f"Progress:\n"
        f"Lectures completed: {len(user['progress']['lectures_completed'])}\n"
        f"Quizzes completed: {len(user['progress']['quizzes_completed'])}\n"
        f"Level: {user['level']}\n"
        f"Achievements: {', '.join(user['achievements']) if user['achievements'] else 'None'}"
    )

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
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
