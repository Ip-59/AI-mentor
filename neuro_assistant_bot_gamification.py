
import json
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler
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

# Achievement system
ACHIEVEMENTS = [
    {"name": "First Lecture", "description": "Complete your first lecture", "points": 10},
    {"name": "Quiz Master", "description": "Score 100% on a quiz", "points": 50},
    {"name": "ML Enthusiast", "description": "Complete 5 lectures", "points": 100},
]

# Helper functions
def award_achievement(username, achievement_name):
    if username not in data["achievements"]:
        data["achievements"][username] = []
    if achievement_name not in [ach["name"] for ach in data["achievements"][username]]:
        achievement = next((a for a in ACHIEVEMENTS if a["name"] == achievement_name), None)
        if achievement:
            data["achievements"][username].append(achievement)
            return f"Achievement unlocked: {achievement_name} - {achievement['description']}"
    return None

def update_user_points(username, points):
    for user in data["users"]:
        if user["username"] == username:
            user["total_points"] += points
            if user["total_points"] >= 100:
                user["level"] += 1
                user["total_points"] = 0
                return f"Congratulations! You advanced to level {user['level']}."
    return None

# Handlers
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    context.user_data["username"] = user.username
    update.message.reply_text(f"Welcome, {user.first_name}! Use /register to create your profile.")
    return REGISTER

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
    if username not in data["progress"]:
        update.message.reply_text("You need to register first with /register.")
        return
    data["progress"][username]["lectures_completed"].append("Lecture 1")
    achievement_msg = award_achievement(username, "First Lecture")
    save_data(data)
    msg = "Lecture completed!"
    if achievement_msg:
        msg += f"\n{achievement_msg}"
    update.message.reply_text(msg)

def quiz(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    if username not in data["progress"]:
        update.message.reply_text("You need to register first with /register.")
        return
    data["progress"][username]["quizzes_completed"].append("Quiz 1")
    achievement_msg = award_achievement(username, "Quiz Master")
    save_data(data)
    msg = "Quiz completed with a perfect score!"
    if achievement_msg:
        msg += f"\n{achievement_msg}"
    update.message.reply_text(msg)

def progress(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    user_progress = data["progress"].get(username, {"lectures_completed": [], "quizzes_completed": []})
    user = next((u for u in data["users"] if u["username"] == username), None)
    achievements = data["achievements"].get(username, [])
    update.message.reply_text(
        f"Progress:\n"
        f"Lectures completed: {len(user_progress['lectures_completed'])}\n"
        f"Quizzes completed: {len(user_progress['quizzes_completed'])}\n"
        f"Level: {user['level']}\n"
        f"Achievements: {', '.join([a['name'] for a in achievements]) if achievements else 'None'}"
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
