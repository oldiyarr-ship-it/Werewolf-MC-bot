# https://github.com/eternnoir/pyTelegramBotAPI

import telebot
from telebot import types
import game
import time

token = ""
bot = telebot.TeleBot(token)

players = {} # id: username
votes = {} # voter id: voted id

status = ["wolf time","witch time","prophet time", "morning", "voting"]

@bot.message_handler(commands=['start'])
def handle_start(message):
	if message.chat.id in players.keys():
		bot.send_message(message.chat.id, "You have joined the game already")
	elif len(players) > game1.players_num:
		bot.send_message(message.chat.id, "The game is full")
	else:
		players[message.chat.id] =  message.chat.username
		for p in players.keys():
			bot.send_message(p, "{} has joined the game".format(message.chat.username))

		if len(players) == game1.players_num:
			game1.assign(list(players.keys()))

			ww = []
			for p in list(game1.players.keys()):
				if game1.players[p].name == "Werewolf" or game1.players[p].name == "Werewolf King":
					ww.append(p)
				bot.send_message(p, "The game begins...")
				bot.send_message(p, "You are a {}".format(game1.players[p].name))

			for p in ww:
				bot.send_message(p, "Your werewolf parters are {}".format([players[w] for w in ww]))

			# wolf 1st night
			bot.send_message(ww[0], "Please press --> /kill to kill someone after discussing with your werewolf partners.")

			game1.status = status[0]


@bot.message_handler(commands=['kill'])
def handle_kill(message):
	if (message.chat.id not in players.keys()) or game1.status != status[0] or (not game1.players[message.chat.id].alive) \
	 or (game1.players[message.chat.id].name != "Werewolf" and game1.players[message.chat.id].name != "Werewolf King"):
		bot.send_message(message.chat.id, "You are not allowed to kill.")
		return
	else:
		for p in players.keys():
			bot.send_message(p, "To all: Werewolf's turn.")

		markup = types.InlineKeyboardMarkup()
		for p in list(players.keys()):
			if game1.players[p].alive:
				itembtn1 = types.InlineKeyboardButton(players[p], callback_data = "kill " + str(p))
				markup.add(itembtn1)
		bot.send_message(message.chat.id, "Who do you want to kill:", reply_markup = markup)


@bot.callback_query_handler(lambda query: "kill" in query.data)
def process_callback_kill(query):
	if (query.message.chat.id not in players.keys()) or game1.status != status[0] or (not game1.players[query.message.chat.id].alive) \
	 or (game1.players[query.message.chat.id].name != "Werewolf" and game1.players[query.message.chat.id].name != "Werewolf King"):
		bot.send_message(query.message.chat.id, "You are not allowed to kill.")
		return
	else:
		killed_id = int(query.data[5:])
		game1.newly_killed.append(killed_id)
		bot.send_message(query.message.chat.id, "U killed: " + players[killed_id])

	 	# witch

		game1.status = status[1]

		for p in players.keys():
			bot.send_message(p, "To all: Witch's turn.")

		found = False
		for p in list(game1.players.keys()):
			if game1.players[p].name == "Witch" and game1.players[p].alive:
				found = True
				break

		if found:
			if game1.players[p].save_potion and game1.players[p].kill_potion:
				witch_action(0,p,killed_id)

			elif not game1.players[p].save_potion and game1.players[p].kill_potion:
				witch_action(1,p)

			elif game1.players[p].save_potion and not game1.players[p].kill_potion:
				witch_action(2,p,killed_id)

		else:
			prophet_action()

		return


def witch_action(status, ids=None, killed_id=None):
	if status == 0:
		markup2 = types.InlineKeyboardMarkup()
		itembtn1 = types.InlineKeyboardButton("Save " + players[killed_id], callback_data = "potion save " + str(killed_id))
		markup2.add(itembtn1)
		for p in list(players.keys()):
			if game1.players[p].alive and p != killed_id:
				itembtn = types.InlineKeyboardButton("kill " + players[p], callback_data = "potion kkkk " + str(p))
				markup2.add(itembtn)
		itembtn2 = types.InlineKeyboardButton("Skip", callback_data = "potion none")
		markup2.add(itembtn2)
		bot.send_message(ids, players[killed_id] + " is killed tonight. Do you want to save him/her or kill others or skip?", reply_markup = markup2)

	elif status == 1:
		markup3 = types.InlineKeyboardMarkup()
		for p in list(players.keys()):
			if game1.players[p].alive:
				itembtn = types.InlineKeyboardButton("kill " + players[p], callback_data = "potion kkkk " + str(p))
				markup3.add(itembtn)
		itembtn2 = types.InlineKeyboardButton("Skip", callback_data = "potion none")
		markup3.add(itembtn2)
		bot.send_message(ids, "Do you want to kill someone or skip?", reply_markup = markup3)

	elif status == 2:
		markup4 = types.InlineKeyboardMarkup()
		itembtn1 = types.InlineKeyboardButton("Yes", callback_data = "potion save " + str(killed_id))
		itembtn2 = types.InlineKeyboardButton("No", callback_data = "potion none")
		markup4.add(itembtn1, itembtn2)
		bot.send_message(ids, players[killed_id] + " is killed tonight. Do you want to save him/her?", reply_markup = markup4)


@bot.callback_query_handler(lambda query: "potion" in query.data)
def process_callback_potion(query):
	if (query.message.chat.id not in players.keys()) or game1.status != status[1] \
	or (not game1.players[query.message.chat.id].alive) or (game1.players[query.message.chat.id].name != "Witch"):
		bot.send_message(query.message.chat.id, "You are not allowed to use potion.")
		return
	else:
		if "save" in query.data:
			saved_id = int(query.data[12:])
			if saved_id in game1.newly_killed:
				game1.newly_killed.remove(saved_id)
				bot.send_message(query.message.chat.id, "U saved: " + players[saved_id])
				game1.players[query.message.chat.id].save_potion = False
			else:
				raise Exception("Saving people not killed!")

		elif "kkkk" in query.data:
			killed_id = int(query.data[12:])
			if game1.players[killed_id].alive:
				game1.newly_killed.append(killed_id)
				bot.send_message(query.message.chat.id, "U killed: " + players[killed_id])
				game1.players[query.message.chat.id].kill_potion = False
			else:
				raise Exception("Killing dead people!")

		elif "none" in query.data:
			pass
	
	prophet_action()
	return


def prophet_action():
	game1.status = status[2]

	for p in players.keys():
		bot.send_message(p, "To all: Prophet's turn.")
	
	found = False
	for p in list(game1.players.keys()):
		if game1.players[p].name == "Prophet" and game1.players[p].alive:
			found = True
			pro = p
			break

	if not found:
		morning_announce()
		return
		
	markup5 = types.InlineKeyboardMarkup()
	for p in list(players.keys()):
		if game1.players[p].alive:
			itembtn = types.InlineKeyboardButton(players[p], callback_data = "check " + str(p))
			markup5.add(itembtn)
	bot.send_message(pro, "Who do you want to check?", reply_markup = markup5)


@bot.callback_query_handler(lambda query: "check" in query.data)
def process_callback_check(query):
	if (query.message.chat.id not in players.keys()) or game1.status != status[2] \
	or (not game1.players[query.message.chat.id].alive) or (game1.players[query.message.chat.id].name != "Prophet"):
		bot.send_message(query.message.chat.id, "You are not allowed to check.")
		return
	else:
		check_id = int(query.data[6:])
		if game1.players[check_id].name == "Werewolf" or game1.players[check_id].name == "Werewolf King":
			bot.send_message(query.message.chat.id, "{} is a bad person.".format(players[check_id]))
		else:
			bot.send_message(query.message.chat.id, "{} is a good person.".format(players[check_id]))

		morning_announce()
		return


def checkwnin():
	if game1.bad_count == 0:
		for p in players.keys():
			bot.send_message(p, "Gameover. The good team wins.")
		return True 
	elif game1.god_count == 0 or game1.civil_count == 0 or (game1.god_count + game1.civil_count) < game1.bad_count:
		for p in players.keys():
			bot.send_message(p, "Gameover. The bad team wins.")
		return True
	else:
		return False

def morning_announce():
	game1.status = status[3]

	for p in players.keys():
		bot.send_message(p, "Good morning! Yesterday night, {} died.".format([players[w] for w in game1.newly_killed]))

	for c in game1.newly_killed:
		game1.players[c].alive = False

		if game1.players[c].name == "Werewolf King" or game1.players[c].name == "Werewolf":
			game1.bad_count -= 1
		elif game1.players[c].name == "Civilian":
			game1.civil_count -= 1
		else:
			game1.god_count -= 1

	if checkwnin():
		return

	no_special = []
	for c in game1.newly_killed:
		if game1.players[c].name == "Werewolf King" or game1.players[c].name == "Hunter":
			pass
		else:
			no_special.append(c)

	for i in no_special:
		game1.newly_killed.remove(i)

	if not found_king_hunter(game1.newly_killed):
		morning_vote()

	return


def found_king_hunter(ids):
	found = False
	ids = list(ids)
	for c in ids:
		if game1.players[c].name == "Werewolf King" or game1.players[c].name == "Hunter":
			found = True
			for p in players.keys():
				bot.send_message(p, players[c] + ", please kill someone.")

			markup6 = types.InlineKeyboardMarkup()
			for p in list(players.keys()):
				if game1.players[p].alive:
					itembtn = types.InlineKeyboardButton("kill " + players[p], callback_data = "special " + str(p))
					markup6.add(itembtn)
			itembtn2 = types.InlineKeyboardButton("Skip", callback_data = "special 0")
			markup6.add(itembtn2)
			bot.send_message(c, "Please kill someone or skip?", reply_markup = markup6)

	if not found:
		return False


@bot.callback_query_handler(lambda query: "special" in query.data)
def process_callback_special_kill(query):
	killed_id = int(query.data[8:])
	if killed_id == 0:
		for p in players.keys():
			bot.send_message(p, players[query.message.chat.id] + " chose not to kill.")
	else:
		if game1.players[killed_id].alive:
			game1.players[killed_id].alive = False
			bot.send_message(query.message.chat.id, "U killed: " + players[killed_id])
		else:
			raise Exception("Killing dead people!")

		for p in players.keys():
			bot.send_message(p, players[killed_id] + "is killed by " + players[query.message.chat.id])

	game1.newly_killed.remove(query.message.chat.id)

	if not found_king_hunter(killed_id):
		if game1.status == status[3]:
			morning_vote()
		elif game1.status == status[4]:
			night()

	return

def morning_vote(again=False):

	if not again:
		if checkwnin():
			return
		else:
			for p in players.keys():
				bot.send_message(p, "The game cotinues... Please vote to kill after discussion.")

	game1.status = status[4]

	# vote
	global votes
	votes = {} # voter id: voted id

	markup7 = types.InlineKeyboardMarkup()
	for p in list(players.keys()):
		if game1.players[p].alive:
			itembtn1 = types.InlineKeyboardButton(players[p], callback_data = "vote " + str(p))
			markup7.add(itembtn1)
	itembtn2 = types.InlineKeyboardButton("Skip", callback_data = "vote 0")
	markup7.add(itembtn2)

	for p in list(players.keys()):
		if game1.players[p].alive:
			bot.send_message(p, "Who do you want to kill:", reply_markup = markup7)


@bot.callback_query_handler(lambda query: "vote" in query.data)
def process_callback_vote(query):
	if (query.message.chat.id not in players.keys()) or game1.status != status[4] \
	or (not game1.players[query.message.chat.id].alive):
		bot.send_message(query.message.chat.id, "You are not allowed to vote.")
		return

	global votes
	voter_id = query.message.chat.id
	voted_id = int(query.data[5:])

	for p in list(votes.keys()):
		if (p == voter_id):
			bot.send_message(voter_id, "You have voted already!")
			return

	votes[voter_id] = voted_id

	if len(votes) != (game1.bad_count + game1.god_count + game1.civil_count):
		if voted_id != 0:
			bot.send_message(voter_id, "You have voted to kill {}. Please wait for others.".format(players[voted_id]))
		else:
			bot.send_message(voter_id, "You have voted to kill {}. Please wait for others.".format("NONE"))
		return

	else:
		result = {}
		for v in list(votes.values()):
			if v == '0':
				continue
			elif v in list(result.keys()):
				result[v] += 1
			else:
				result[v] = 1

		text = ""
		for v in list(votes.keys()):
			if votes[v] != 0:
				text += "{} vote to kill {}\n".format(players[v], players[votes[v]])
			else:
				text += "{} vote to kill {}\n".format(players[v], "None")

		text += "\nTotal:\n"

		votes = {}
		sorted_result = sorted(result.items(), key=lambda x: x[1], reverse=True) # [(id, 3), (id, 1), (id, 1)]

		for r in sorted_result:
			if r[0] != 0:
				text += "{}: {}\n".format(players[r[0]], r[1])
			else:
				text += "{}: {}\n".format("None", r[1])

		if (sorted_result[0][0] == 0):
			sorted_result.pop(0)

		if (len(sorted_result) == 0):
			text += "\n Everyone choose to skip."
			for p in list(players.keys()):
				bot.send_message(p, text)
			night()
			return

		if (len(sorted_result) > 1 and sorted_result[0][1] == sorted_result[1][1]):
			text += "\n It's a tie. Please vote again."
			for p in list(players.keys()):
				bot.send_message(p, text)
			morning_vote(again=True)

		else:
			killed_id = sorted_result[0][0]
			text += "\n {} is killed.".format(players[killed_id])

			for p in list(players.keys()):
				bot.send_message(p, text)

			game1.players[killed_id].alive = False

			if game1.players[killed_id].name == "Werewolf King" or game1.players[killed_id].name == "Werewolf":
				game1.bad_count -= 1
			elif game1.players[killed_id].name == "Civilian":
				game1.civil_count -= 1
			else:
				game1.god_count -= 1

			if checkwnin():
				return

			if not found_king_hunter(killed_id):
				night()


def night():
	game1.status = status[0]

	for p in list(players.keys()):
		bot.send_message(p, "Night again. Werewolves, please kill.")

		if (game1.players[p].name == "Werewolf" or game1.players[p].name == "Werewolf King") and game1.players[p].alive == True:
			ww = p
	
	bot.send_message(ww, "Please press --> /kill to kill someone after discussing with your werewolf partners.")


@bot.message_handler(commands=['help'])
def help(message):
	bot.send_message(message.chat.id, "Hi. To join the game, press --> /start.\nTo check the status of the game, press --> /status.\nTo check the rules, press --> /rules.\nFor other enquiries, please contact the host.")


@bot.message_handler(commands=['status'])
def check_status(message):
	if message.chat.id not in players.keys():
		bot.send_message(message.chat.id, "You are not in the game.")

	elif message.chat.id in players.keys() and game1.status == "":
		text = "status: not enough players\n\n"
		for p in list(players.keys()):
			text += players[p]
			text += "\n"
		text += "\nNeed {} more players.".format(game1.players_num - len(players))
		bot.send_message(message.chat.id, text)

	else:
		text = "status: "
		text += game1.status

		text += "\n\n"

		for p in list(players.keys()):
			text += players[p]
			text += ": "
			if game1.players[p].alive:
				text += "alive"
			else:
				text += "dead"
			text += "\n"
		bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['rules'])
def rules(message):
	text = "Werewolf bot acts as the MC/moderator of a simplified verison of the game: The Werewolves of Millers Hollow.\n\n"
	text += "English rules: https://en.wikipedia.org/wiki/The_Werewolves_of_Millers_Hollow\n\n"
	text += "Chinese rules: https://zh.wikipedia.org/wiki/%E7%8B%BC%E4%BA%BA%E6%AE%BA"
	bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
	bot.send_message(message.chat.id, "Hi. Press --> /help for help.")


# main
print("Welcome to werewolf game.\nSet up: ")
n = int(input("Number of participants: "))
w = int(input("Number of werewolves: "))
k = int(input("Number of werewolf kings: "))
p = int(input("Number of prophets: "))
wi = int(input("Number of witches: "))
h = int(input("Number of hunters: "))
c = int(input("Number of civilians: "))

if (w + k + p + wi + h + c != n):
	raise Exception("Wrong number of characters.")
elif (w + k) < 1:
	raise Exception("No werewolf! Cannot start the game.")
else:
	game1 = game.Game(n, [w, k, p, wi, h, c])
	print("The game begins...")
	bot.polling()

if __name__ == "__main__":
    bot.infinity_polling()