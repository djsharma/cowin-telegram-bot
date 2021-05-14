
from telegram.ext import PicklePersistence
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.updater import Updater
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.callbackquery import CallbackQuery
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from telegram.message import Message
from telegram.ext.dispatcher import run_async
from telegram.ext import MessageHandler, Filters
from telegram.ext import ConversationHandler
import copy



##mongodb imports
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Book"]
collection = mydb["customers"]


district_codes = {
	'indore' : '314',
	'khandwa' : '339',
	'jhabua' : '340',
	'dhar' : '341'
}





def start(update, context):
	chat_id = update.message.chat_id
	first_name = update.message.chat.first_name
	last_name = update.message.chat.last_name
	context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, {}".format(first_name) )
	context.bot.send_message(chat_id=update.effective_chat.id, text="This bot will help you to get notification for vaccine slot availability in your interested districts. \n \n ~ developer Dhananjay Sharma")
	context.bot.send_message(chat_id=update.effective_chat.id, text="Type /start anytime to start again, /help for help menu")
    

	# collection.update({"chatId": update.effective_chat.id}, { '$set' : {"firstName": first_name, "lastName" : last_name} }, upsert=True)
	# collection.update({"chatId": update.effective_chat.id}, { '$set' : {"firstName": first_name, "lastName" : last_name} }, multi=True, upsert=True)


	keyboard = [[
		InlineKeyboardButton("Indore", callback_data='indore'),
		InlineKeyboardButton("Khandwa", callback_data='khandwa'),
		InlineKeyboardButton("Jhabua", callback_data='jhabua'),
		InlineKeyboardButton("Dhar", callback_data='dhar')
	]]

	reply_markup = InlineKeyboardMarkup(keyboard)
	update.message.reply_text('please select your district', reply_markup=reply_markup)




def button(update, context):
	query: CallbackQuery = update.callback_query
	query.answer()
	
	firstName = query.message.chat.first_name
	lastName = query.message.chat.last_name
	
	if query['message']['text'] == 'please select your age group':
		query.edit_message_text(text="Selected ageGroup: {}".format(query.data))
		collection.update({"chatId": update.effective_chat.id}, { '$set' : {"ageGroup": query.data} }, multi=True)
		context.bot.send_message(chat_id=update.effective_chat.id, text="successfully updated your age group, please wait for notifications")	
	
	else :
		query.edit_message_text(text="Selected district: {}".format(query.data))

		query_doc = {"chatId" : update.effective_chat.id, "district" : query.data, "districtCode" : district_codes[query.data] }
		##TODO: if exists then extract data
		update_doc = {"chatId" : update.effective_chat.id, "district" : query.data, "districtCode" : district_codes[query.data] , "firstName" : firstName, "lastName": lastName, "required" : True}
		collection.update(query_doc, update_doc, upsert=True)
		context.bot.send_message(chat_id=update.effective_chat.id, text="district added in your watchlist, please press /age to update your age group")
		# context.bot.send_message(chat_id=update.effective_chat.id, text="district added successfully to your watchlist, please press /age to update your age group")	
		# collection.insert({"chatId" : update.effective_chat.id, "district" : query.data, "districtCode" : district_codes[query.data]})
		# context.bot.send_message(chat_id=update.effective_chat.id, text="district already in your watchlist, please press /age to update your age group")



		# query_doc = {"chatId" : update.effective_chat.id, "district" : query.data, "districtCode" : district_codes[query.data] }
		# update_doc = {"chatId" : update.effective_chat.id, "district" : query.data, "districtCode" : district_codes[query.data] }
		# collection.update(query_doc, update_doc, upsert=True)
		

		# collection.update({"chatId": update.effective_chat.id}, { '$set' : {"district" : query.data, "districtCode" : district_codes[query.data], "required" : True} }, multi=True, upsert=True)

		




def deregister(update, context):
	query_doc = {"chatId" : update.effective_chat.id}
	collection.remove(query_doc)
	context.bot.send_message(chat_id=update.effective_chat.id, text="You are de-registered from all watchlists")



def more(update, context):
	query_doc = {"chatId" : update.effective_chat.id}
	collection.update({"chatId": update.effective_chat.id}, { '$set' : {"required": True} }, multi=True)
	context.bot.send_message(chat_id=update.effective_chat.id, text="You are again listening to notifications")






def ageGroup(update, context):
	chat_id = update.message.chat_id
	keyboard = [[
		InlineKeyboardButton("Above 45", callback_data='above45'),
		InlineKeyboardButton("Below 45", callback_data='below45'),
	]]

	reply_markup_age = InlineKeyboardMarkup(keyboard)
	update.message.reply_text('please select your age group', reply_markup=reply_markup_age)





def help_menu(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text=" 1.) Want to add anymore district in your watchlist, press /start and register new \n 2) To deregister yourself from all watchlist press /deregister \n 3) Upon getting notification for slot you, for further receiving notifications, press /more")







persistence = PicklePersistence(filename='/Users/test/MiscData/BotDataBase')

updater = Updater(token='TOKEN', persistence=persistence, use_context=True)
dispatcher = updater.dispatcher


start_handler = CommandHandler('start', start)
button_handler = CallbackQueryHandler(button)
help_handler = CommandHandler('help', help_menu)
deregister_handler = CommandHandler('deregister', deregister)
ageGroup_handler = CommandHandler('age',ageGroup)
more_handler = CommandHandler('more',more)


dispatcher.add_handler(start_handler)
dispatcher.add_handler(button_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(deregister_handler)
dispatcher.add_handler(ageGroup_handler)
dispatcher.add_handler(more_handler)



updater.start_polling()


#updater.stop()




