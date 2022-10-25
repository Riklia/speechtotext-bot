import logging
from aiogram import Bot, Dispatcher, executor, types
from config import API_TOKEN, admin
import keyboard as kb
import functions as func
import sqlite3
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import Throttled
import speech_to_text


storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
connection = sqlite3.connect('data.db')
q = connection.cursor()
q.execute("create table if not exists users (id integer primary key, "
		  "user_id integer, block integer, language text )")


class Admin(StatesGroup):
	ban = State()
	unban = State()
	bulk = State()


@dp.message_handler(commands=['start'])
@dp.throttled(func.antiflood, rate=3)
async def start(message: types.Message):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer('Hi, admin!', reply_markup=kb.menu)
		else:
			await message.answer('Send me a voice message!', reply_markup=kb.menu)
	else:
		await message.answer('Sorry, you are banned.')


@dp.message_handler(content_types=['text'], text="Help")
@dp.throttled(func.antiflood, rate=3)
async def command_help(message: types.Message):
	await message.answer("I can covert voice messages to text "
						 "messages.\nNOTE: Duration of voice message must be "
						 "up to 5 minutes.")


@dp.message_handler(commands=['admin'])
async def com_admin(message: types.Message):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users where user_id={message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer("Hi, admin!", reply_markup=kb.adm)


@dp.message_handler(content_types=['text'], text="Back to main menu")
async def back_to_menu(message: types.Message):
	await message.answer("Send me a voice message!", reply_markup=kb.menu)


@dp.message_handler(content_types=['text'], text="Blacklist")
async def blacklist(message: types.Message):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users where user_id={message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			q.execute(f"SELECT * FROM users WHERE block == 1")
			result = q.fetchall()
			sl = []
			for index in result:
				i = index[0]
				sl.append(i)
			ids = "\n".join(map(str, sl))
			await message.answer(f"ID users in blacklist:\n{ids}",
								reply_markup=kb.adm)


@dp.message_handler(content_types=['text'], text="Add to blacklist")
async def add_to_black(message: types.Message):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users where user_id={message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer("Enter ID of user you want to ban.\nIf "
								 "you want to cancel this action, press the "
								 "button below.", reply_markup=kb.back)
			await Admin.ban.set()


@dp.message_handler(content_types=['text'], text="Remove from blacklist")
async def remove_from_black(message: types.Message):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users where user_id={message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer("Enter ID of user you want to remove from "
								 "blacklist. \nIf you want to cancel this action, press the "
								 "button below.", reply_markup=kb.back)
			await Admin.unban.set()


@dp.message_handler(content_types=['text'], text="Bulk messaging")
async def bulk_messaging(message: types.Message):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users where user_id={message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		if message.chat.id == admin:
			await message.answer("Enter a text from bulk messaging",
								 reply_markup=kb.back)
			await Admin.bulk.set()


@dp.message_handler(content_types=['text'], text="Language")
@dp.throttled(func.antiflood, rate=3)
async def language(message: types.Message):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users where user_id={message.chat.id}")
	result = q.fetchone()
	if result[0] == 0:
		await message.answer('Choose the language of your voice messages.',
							 reply_markup=kb.lang)


@dp.callback_query_handler(text=['set_lang_Ukrainian', 'set_lang_English'])
async def set_language(call: types.CallbackQuery):
	if call.data == "set_lang_Ukrainian":
		await func.set_language(call.message.chat.id, "Ukrainian")
	elif call.data == "set_lang_English":
		await func.set_language(call.message.chat.id, "English")
	await bot.edit_message_text(chat_id=call.message.chat.id,
								message_id=call.message.message_id,
								text=f'Language: {call.data.split("_")[2]}')
	await call.answer()


@dp.message_handler(state=Admin.ban)
async def proc_add_to_black(message: types.Message, state: FSMContext):
	if message.text == "Cancel":
		await message.answer("Canceled.", reply_markup=kb.adm)
		await state.finish()
	else:
		if message.text.isdigit():
			q.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
			result = q.fetchall()
			connection.commit()
			if len(result) == 0:
				await message.answer("This user is not in the database.")
			else:
				a = result[0]
				id = a[0]
				if id == 0:
					q.execute(f"UPDATE users SET block=1 WHERE user_id = "
							  f"{message.text}")
					connection.commit()
					await message.answer("User has been banned.",
										 reply_markup=kb.adm)
					await state.finish()
					await bot.send_message(message.text, "You have been "
														 "banned by admin.")
				else:
					await message.answer("This user already had been banned.")
		else:
			await message.answer("Sorry, ID must be a number.")


@dp.message_handler(state=Admin.unban)
async def proc_remove_from_black(message: types.Message, state: FSMContext):
	if message.text == "Cancel":
		await message.answer("Canceled.", reply_markup=kb.adm)
		await state.finish()
	else:
		if message.text.isdigit():
			q.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
			result = q.fetchall()
			connection.commit()
			if len(result) == 0:
				await message.answer("This user is not in the database.")
			else:
				a = result[0]
				id = a[0]
				if id == 1:
					q.execute(f"UPDATE users SET block=0 WHERE user_id = "
							  f"{message.text}")
					connection.commit()
					await message.answer("User has been removed from "
										 "blacklist.", reply_markup=kb.adm)
					await state.finish()
					await bot.send_message(message.text, "You have been "
														 "unbanned.")
				else:
					await message.answer("This user does not in blacklist.")
		else:
			await message.answer("Sorry, ID must be a number.")


@dp.message_handler(state=Admin.bulk)
async def proc_bulk_messaging(message: types.Message, state: FSMContext):
	q.execute(f'SELECT user_id FROM users')
	row = q.fetchall()
	connection.commit()
	text = message.text
	if message.text == 'Cancel':
		await message.answer('Canceled.', reply_markup=kb.adm)
		await state.finish()
	else:
		info = row
		await message.answer('Bulk messaging has been started!',
							 reply_markup=kb.adm)
		for i in range(len(info)):
			try:
				await bot.send_message(info[i][0], str(text))
			except:
				pass
		await message.answer('Bulk messaging has been completed!',
							 reply_markup=kb.adm)
		await state.finish()


async def return_text(file, lang, message):
	await message.answer(speech_to_text.to_text(file, lang), reply=message)


@dp.message_handler(content_types=[types.ContentType.VOICE])
async def get_voice(message: types.Message):
	func.join(chat_id=message.chat.id)
	q.execute(f"SELECT block FROM users where user_id={message.chat.id}")
	result = q.fetchone()[0]
	if result == 0:
		q.execute(f"SELECT language FROM users WHERE user_id = {message.chat.id}")
		lang = q.fetchone()[0]
		voice = await message.voice.get_file()
		await bot.download_file(file_path=voice.file_path, destination=f"{voice.file_id}.ogg")
		await return_text(f"{voice.file_id}.ogg", lang, message)
	else:
		await message.answer("Sorry, you are banned.")

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)
