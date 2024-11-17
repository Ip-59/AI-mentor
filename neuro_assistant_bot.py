
from telegram import Update, Bot, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging

# Token placeholder (To run the bot, replace 'YOUR_TOKEN' with the actual token)
TELEGRAM_BOT_TOKEN = "YOUR_TOKEN"

# Enabling logging for better tracking of bot activity
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Stages of conversation
REGISTER, MAIN_MENU = range(2)

# Dictionary to store user data temporarily
user_data = {}

# Start command handler to initiate conversation
def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    context.user_data["username"] = user.username
    update.message.reply_text(
        f"Hello, {user.first_name}! Welcome to the ML Neuro Assistant. "
        "Please type /register to begin your learning journey."
    )
    return REGISTER

# Registration handler
def register(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    user_data[user.username] = {
        "name": user.first_name,
        "progress": [],  # Tracking user's completed lessons, quizzes, etc.
    }
    update.message.reply_text(
        "Thank you for registering! Type /menu to access the learning options."
    )
    return MAIN_MENU

# Menu handler - Main options for the user after registration
def menu(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Main Menu:\n"
        "1. Type /lecture to begin a lecture.\n"
        "2. Type /quiz to test your knowledge.\n"
        "3. Type /progress to check your progress."
    )
    return MAIN_MENU

# Placeholder lecture handler
def lecture(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Starting lecture 1: Introduction to Machine Learning. [Content Placeholder]"
    )

# Placeholder quiz handler
def quiz(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Quiz 1: What is Machine Learning? [Question Placeholder]"
    )

# Progress handler
def progress(update: Update, context: CallbackContext) -> None:
    username = update.effective_user.username
    progress_info = user_data.get(username, {}).get("progress", [])
    update.message.reply_text(
        f"Your progress: {progress_info}"
    )

# Error handler for better debugging
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f"Update {update} caused error {context.error}")

# Main function to start the bot
def main():
    # Creating the bot
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Setting up ConversationHandler with the states
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

    # Add ConversationHandler to dispatcher
    dispatcher.add_handler(conv_handler)

    # Log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
