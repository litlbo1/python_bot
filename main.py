import os
import mysql.connector
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

try:
  db_connection = mysql.connector.connect(
      host=os.getenv('DB_HOST'),
      user=os.getenv('DB_USER'),
      password=os.getenv('DB_PASSWORD'),
      database=os.getenv('DB_NAME')
  )
  db_cursor = db_connection.cursor()
except mysql.connector.Error as err:
  print(f"Error: {err}")
  exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  chat_id = update.message.chat_id

  db_cursor.execute("INSERT IGNORE INTO users (chat_id) VALUES (%s)", (chat_id,))
  db_connection.commit()
  web_app_button = InlineKeyboardButton(
      text="Открыть приложение",
      web_app=WebAppInfo(url="https://kamekadzefilm.ru/")
  )
  reply_markup = InlineKeyboardMarkup([[web_app_button]])
  await update.message.reply_text(
      'Привет друг!\nТут находиться ссылка на приложение где ты сможешь смотреть фильмы абсолютно бесплатно в хорошем качестве)',
      reply_markup=reply_markup
  )

async def set_start_menu(application: Application) -> None:
  bot = application.bot
  commands = [
      ("start", "Начать")
  ]
  bot.set_my_commands(commands)
  start_button = KeyboardButton('/start')
  reply_markup = ReplyKeyboardMarkup([[start_button]], resize_keyboard=True)
  db_cursor.execute("SELECT chat_id FROM users")
  rows = db_cursor.fetchall()
  for row in rows:
      chat_id = row[0]
      bot.send_message(chat_id=chat_id, text="Нажмите 'Начать' для продолжения", reply_markup=reply_markup)

def main() -> None:
  application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
  application.add_handler(CommandHandler('start', start))
  application.run_polling(poll_interval=0.5)
  application.post(set_start_menu(application))

if __name__ == '__main__':
  main()
