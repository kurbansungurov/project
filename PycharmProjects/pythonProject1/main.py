from typing import Dict, Any
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import random
import json
import requests
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, \
    ConversationHandler, filters, MessageHandler

TOKEN = '7689860193:AAGnExMzB-bYQfKRVaRya6X0KGlQnQLu1FM'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

GENRE_CODE = {
    1: "комедия",
    2: "ужасы",
    3: "мелодрама",
    4: "драма"}

HEADERS = {
    "accept": "application/json",
    "X-API-KEY": "MRKSZ70-GSAMN68-HK62F95-37K90FA"}

GENRE, MOVIES = range(2)


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     keyboard = [
#         [
#             InlineKeyboardButton("комедия", callback_data="1"),
#             InlineKeyboardButton("ужасы", callback_data="2"),
#             InlineKeyboardButton("мелодрамы", callback_data="3"),
#             InlineKeyboardButton("драма", callback_data="4")
#         ]
#     ]

#     reply_markup = InlineKeyboardMarkup(keyboard)

#     await update.message.reply_text("Привет,я бот с рекомендательной системой по поиску фильмов на вечер.Давай что-нибудь подберем:Фильм, какого жанра вы бы хотели посмотреть?", reply_markup=reply_markup)


async def genre_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"Выбран жанр: {GENRE_CODE[int(query.data)]}")

    url = f"https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&selectFields=&genres.name={GENRE_CODE[int(query.data)]}"
    response = requests.get(url, headers=HEADERS)
    print(response.text)

    parsed_data = json.loads(response.text)
    ids = [doc['id'] for doc in parsed_data['docs']]
    print(ids)

    random_ids = random.sample(ids, 5)
    print(random_ids)

    payload_ids = {
        update.effective_chat.id: {"genre_data": query.data, "ids": random_ids}
    }
    context.bot_data.update(payload_ids)
    print(context.bot_data)
    # await update.message.reply_text("Готовы ли выбрать интересущие вас фильмы?")
    return MOVIES


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END


async def movies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("xaxa")
    return ConversationHandler.END
    # keyboard = [
    #     [
    #         InlineKeyboardButton("да", callback_data="1"),
    #         InlineKeyboardButton("нет", callback_data="2")
    #     ]
    # ]

    # reply_markup = InlineKeyboardMarkup(keyboard)


# ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["комедия", "ужасы", "боевики"]]

    await update.message.reply_text(
        "Привет! Я бот-рекомендатель! "
        "Отправьте /cancel чтобы перестать разговаривать.\n\n"
        "Фильм какого жанра, вы бы хотели посмотреть??",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Выберите жанр"
        ),
    )

    return GENRE


async def movie_genre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    choosen_genre = update.message.text

    print(user, choosen_genre)

    # сохранение в payload

    await update.message.reply_text(
        "Напишите, пожалуйста, несколько фильмов в этом жарне, которые вы посмотрели, они вам понравились и оставили классные впечатления.",
        reply_markup= ReplyKeyboardRemove()
    )

    return MOVIES


async def choose_movies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # получить фильмы
    movie_title = update.message.text

    print(movie_title)

    # ищем фильм по названию
    # берем похожие
    # сохраняем в бд

    await update.message.reply_text(
        "Вот что я тебе хочу посоветовать!."
    )
    return ConversationHandler.END

async def skip_choose_movies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    # application.add_handler(CallbackQueryHandler(genre_button_click))

    # conv_handler = ConversationHandler(
    #     entry_points=[CommandHandler("start", start)],
    #     states={
    #         GENRE: [CallbackQueryHandler(genre_button_click)],
    #         MOVIES: [MessageHandler(filters.TEXT, movies)],
    #     },
    #     fallbacks=[CommandHandler("cancel", cancel)],
    # )
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENRE: [MessageHandler(filters.Regex("^(комедия|ужасы|боевики)$"), movie_genre)],
            MOVIES: [MessageHandler(filters.Regex(filters.TEXT), choose_movies)
                     ],
            # LOCATION: [
            #     MessageHandler(filters.LOCATION, location),
            #     CommandHandler("skip", skip_location),
            # ],
            # BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()

    # async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     await context.bot.send_message(chat_id=update.effective_chat.id,text="Привет,я бот с рекомендательной системой по поиску фильмов на вечер.Давай что-нибудь подберем")