import telebot
from telebot import types
import os
import time
import game

# TOKEN (HEROKU ENV)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise Exception("TELEGRAM_BOT_TOKEN bulunamadı!")

bot = telebot.TeleBot(TOKEN)

players = {}   # id: username
votes = {}     # voter id: voted id

status = ["wolf time", "witch time", "prophet time", "morning", "voting"]

# GAME OBJESİ (SENİN game.py İÇİN)
game1 = game.Game()


# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def handle_start(message):

    user_id = message.chat.id

    if user_id in players:
        bot.send_message(user_id, "Zaten oyuna katıldın.")
        return

    if len(players) >= game1.players_num:
        bot.send_message(user_id, "Oyun dolu.")
        return

    players[user_id] = message.chat.username or "unknown"

    for p in players:
        bot.send_message(p, f"{players[user_id]} oyuna katıldı.")

    if len(players) == game1.players_num:
        game1.assign(list(players.keys()))

        ww = []

        for p in game1.players:
            role = game1.players[p].name

            if role in ["Werewolf", "Werewolf King"]:
                ww.append(p)

            bot.send_message(p, f"Oyun başladı!\nRolün: {role}")

        for p in ww:
            bot.send_message(p, f"Diğer kurt adamlar: {[players[x] for x in ww]}")

        bot.send_message(ww[0], " /kill komutu ile öldürme yapabilirsin.")

        game1.status = status[0]


# ---------------- BOT START ----------------
if __name__ == "__main__":
    print("Bot çalışıyor...")
    bot.infinity_polling(skip_pending=True)