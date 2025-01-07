from openai import OpenAI
import telebot
import sqlite3



key = "sk-KVD8VYoze5Ivy8BFwfV9KnCzdMvhnnyp"

client = OpenAI(
    api_key=key,
    base_url="https://api.proxyapi.ru/openai/v1"
)


token = ''
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['clear'])
def clear(message):
    with sqlite3.connect('db.db') as db:
        cursor = db.cursor()
        query_for_user_messages = '''SELECT text FROM mes WHERE role='user' '''
        cursor.execute(query_for_user_messages)
        str_of_user_messages = '. '.join(list(map(lambda x: x[0], cursor.fetchall())))

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=
            [
                {
                    "role": "system",
                    "content": "Вы проверяете предложения, в конце выдавая аналитику допущенных ошибок по пунктам"
                },
                {
                    "role": "system",
                    "content": "аналитика должна быть на русском языке, но про предложения вашего ученика, сохраняя английские слова"
                },
                {
                    "role": "user",
                    "content": str_of_user_messages
                },
            ]
        )
        bot.send_message(message.chat.id, completion.choices[0].message.content)

        query = f'''DELETE FROM mes'''
        cursor.execute(query)
        db.commit()


@bot.message_handler()
def main(message):
    with sqlite3.connect('db.db') as db:

        cursor = db.cursor()


        query_add_user_message = f'''INSERT INTO mes (text, role) VALUES ('{message.text}', 'user')'''
        cursor.execute(query_add_user_message)

        query_for_gpt_context = '''SELECT * FROM mes'''
        cursor.execute(query_for_gpt_context)

        list_of_past_messages_for_gpt_context = [{'role': i[2], 'content': i[1]} for i in cursor.fetchall()]

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=
            [
                {
                    "role": "system",
                    "content": "Вы англичанин, который поддерживает диалог на английском со своим другом"
                },

            ]+list_of_past_messages_for_gpt_context
        )

        query_add_sistem_message = f'''INSERT INTO mes (text, role) VALUES (?, ?)'''
        cursor.execute(query_add_sistem_message, (completion.choices[0].message.content, 'system'))

        bot.send_message(message.chat.id, completion.choices[0].message.content)
        db.commit()

bot.polling(none_stop=True)