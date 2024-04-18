#!/usr/bin/env python
# pylint: disable=unused-argument, import-error
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to keep track of your study and study better
"""
import matplotlib.pyplot as plt
import numpy as np
import time
import logging
import ModuloScelte
import ModuloJson
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

from dotenv import load_dotenv
import os
from io import BytesIO


load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

global tempInfo
global colonne

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Stages
MATERIA, TEMPO_STUDIO, TEMPO_PAUSA, STUDIO, PAUSA, STOP_SAVE, END = range(7)
# Callback data
ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, ELEVEN, TWELVE = range(
    12)


async def start_focus_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    global tempInfo
    global colonne
    tempInfo = {'Materia': "?",
                'Tempo studiato': 0,
                'Tempo_studio': 0,
                'Tempo_pausa': 0,
                'nS': 0,
                'nP': 0,
                'Efficenza': 0,
                'Note': "?"
                }
    colonne = ['Materia', 'Tempo studiato', 'Tempo_studio',
               'Tempo_pausa', 'nS', 'nP', 'Efficenza', 'Note']

    df = ModuloJson.read_csv_table("tabella_studio", colonne)

    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("Telecomunicazioni", callback_data=str(ONE)),
            InlineKeyboardButton("Internet and Security",
                                 callback_data=str(TWO)),
        ],
        [
            InlineKeyboardButton(
                "Algoritmi per l'Ingegneria", callback_data=str(THREE)),
            InlineKeyboardButton("Automazione Industriale",
                                 callback_data=str(FOUR)),
        ],
        [
            InlineKeyboardButton("Esci", callback_data=str(FIVE)),
            # InlineKeyboardButton("6", callback_data=str(SIX)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("Ciao, che materia vuoi studiare?", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return MATERIA


async def salva_materia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    # print(query.data)
    materia = ModuloScelte.getSubject(int(query.data))
    # print(materia)
    global tempInfo
    tempInfo["Materia"] = materia
    # print(tempInfo)
    keyboard = [
        [
            InlineKeyboardButton("20m", callback_data=str(ONE)),
            InlineKeyboardButton("25m", callback_data=str(TWO)),
            InlineKeyboardButton("30m", callback_data=str(THREE)),
        ],
        [
            InlineKeyboardButton("35m", callback_data=str(FOUR)),
            InlineKeyboardButton("40m", callback_data=str(FIVE)),
            InlineKeyboardButton("45m", callback_data=str(SIX)),
        ],
        [
            InlineKeyboardButton("50m", callback_data=str(SEVEN)),
            InlineKeyboardButton("55m", callback_data=str(EIGHT)),
            InlineKeyboardButton("60m", callback_data=str(NINE)),
        ],
        [
            InlineKeyboardButton("Esci", callback_data=str(TEN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Bene, ora scegli quanto tempo far durare le tue sessioni di studio", reply_markup=reply_markup
    )
    return TEMPO_STUDIO


async def salva_t_studio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    # print(query.data)
    studio = ModuloScelte.getStudyTime(int(query.data))
    # print(materia)
    global tempInfo
    tempInfo["Tempo_studio"] = studio
    # print(tempInfo)
    keyboard = [
        [
            InlineKeyboardButton("5m", callback_data=str(ONE)),
            InlineKeyboardButton("7m", callback_data=str(TWO)),
            InlineKeyboardButton("9m", callback_data=str(THREE)),
        ],
        [
            InlineKeyboardButton("10m", callback_data=str(FOUR)),
            InlineKeyboardButton("12m", callback_data=str(FIVE)),
            InlineKeyboardButton("14m", callback_data=str(SIX)),
        ],
        [
            InlineKeyboardButton("15m", callback_data=str(SEVEN)),
            InlineKeyboardButton("17m", callback_data=str(EIGHT)),
            InlineKeyboardButton("20m", callback_data=str(NINE)),
        ],
        [
            InlineKeyboardButton("Esci", callback_data=str(TEN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Bene, ora scegli quanto tempo far durare le tue pause", reply_markup=reply_markup
    )
    return TEMPO_PAUSA


async def salva_t_pausa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    # print(query.data)
    pausa = ModuloScelte.getPauseTime(int(query.data))
    # print(materia)
    global tempInfo
    tempInfo["Tempo_pausa"] = pausa
    print(tempInfo)
    keyboard = [
        [
            InlineKeyboardButton("Cominciamo!", callback_data=str(ONE)),
        ],
        [
            InlineKeyboardButton("Ci ho ripensato", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Al tuo segnale!", reply_markup=reply_markup
    )
    return STUDIO


async def studio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global tempInfo

    query = update.callback_query
    chat_id = update.effective_message.chat_id
    query_id = query.message.message_id

    delete_id = query_id + tempInfo['nS'] + tempInfo['nP']
    if tempInfo['nS'] == 0:
        delete_id = query_id + 1
    await query.answer()
    ora_futura, minuti_futuri = ModuloScelte.calcola_tempo(tempInfo["Tempo_studio"])

    text=f"""Inizia il focus *numero {tempInfo['nS']+1}*, attento!💡📖
La prossima pausa sarà alle *{ora_futura:02d}:{minuti_futuri:02d}🔏*
"""
    e_text = ModuloJson.escape_special_chars(text)
    await query.edit_message_text(e_text,parse_mode="MarkdownV2")

    print("query id: ", query_id, "\n message to delite id: ", delete_id)
    if tempInfo['nS'] != 0:
        await context.bot.deleteMessage(update.effective_chat.id, delete_id)
        print("eliminato messaggio con id: ", delete_id)

    print("tempInfo nS: ", tempInfo["nS"])

    due = tempInfo["Tempo_studio"]*60
    context.job_queue.run_once(
        alarm, due, chat_id=chat_id, name=str(chat_id), data=due,)
    time.sleep(due)

    tempInfo['nS'] = tempInfo['nS'] + 1
    if tempInfo['nS'] > 3:
        keyboard = [
            [
                InlineKeyboardButton("Continua", callback_data=str(ONE)),
            ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"Hai completato tutte le {tempInfo['nS']} sesh da {tempInfo['Tempo_studio']} minuti!", reply_markup=reply_markup
        )
        return STOP_SAVE

    keyboard = [
        [
            InlineKeyboardButton("Comincia la pausa", callback_data=str(ONE)),
        ],
        [
            InlineKeyboardButton("Smetti di studiare", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Hai completato {tempInfo['nS']} sesh da {tempInfo['Tempo_studio']} minuti!", reply_markup=reply_markup
    )
    return PAUSA


async def pausa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global tempInfo
    chat_id = update.effective_message.chat_id
    query = update.callback_query
    query_id = query.message.message_id
    delete_id = query_id + tempInfo['nS'] + tempInfo["nP"]

    if tempInfo['nP'] == 0:
        delete_id = query_id + 1

    await query.answer()
    ora_futura, minuti_futuri = ModuloScelte.calcola_tempo(tempInfo["Tempo_pausa"])

    text=f"""Inizia la pausa *numero {tempInfo['nP']+1}*, che chill...🍃☀️
Si torna a studiare alle *{ora_futura:02d}:{minuti_futuri:02d}🔓*
"""
    e_text = ModuloJson.escape_special_chars(text)
    await query.edit_message_text(e_text,parse_mode="MarkdownV2")

    print("query id: ", query_id, "\n message to delite id: ", delete_id)
    await context.bot.deleteMessage(update.effective_chat.id, delete_id)
    print("eliminato messaggio con id: ", delete_id)

    print("tempInfo nP: ", tempInfo["nP"])

    due = tempInfo['Tempo_pausa'] * 60
    context.job_queue.run_once(
        alarm, due, chat_id=chat_id, name=str(chat_id), data=due,)
    time.sleep(due)

    tempInfo["nP"] = tempInfo["nP"] + 1

    keyboard = [
        [
            InlineKeyboardButton("Studia", callback_data=str(ONE)),
        ],
        [
            InlineKeyboardButton("Basta, ho finito", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Pausa finita, pronto per studiare?", reply_markup=reply_markup
    )
    return STUDIO


async def salva(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global colonne
    global tempInfo

    query = update.callback_query
    query_id = query.message.message_id
    delete_id = query_id + tempInfo['nS'] + tempInfo["nP"]

    print("query id: ", query_id, "\n message to delite id: ", delete_id)
    await context.bot.deleteMessage(update.effective_chat.id, delete_id)
    print("eliminato messaggio con id: ", delete_id)

    await query.answer()
    if tempInfo["nS"] == 0:
        await query.edit_message_text(text=f"Ah, trolli? 🗿")
        return ConversationHandler.END

    tempInfo['Tempo studiato'] = tempInfo["nS"] * tempInfo["Tempo_studio"]

    # Salva il DataFrame aggiornato nel file CSV
    ModuloJson.add_new_line(name="tabella_studio",
                            columns=colonne, newline=tempInfo)

    ore_studiate = tempInfo['Tempo studiato']//60
    minuti_restanti = tempInfo['Tempo studiato'] - 60 * ore_studiate
    await query.edit_message_text(
        text=f"salvato, hai studiato {tempInfo['Materia']} per {ore_studiate} ore e {minuti_restanti} minuti, 🆒\npausetta? ☕"
    )
    return ConversationHandler.END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Scrivimi quando vuoi studiare 👋")
    return ConversationHandler.END

###


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job

    await context.bot.send_message(job.chat_id, text=f"Beep!⏰ \n\nSono passati {job.data//60} minuti!")


async def inizializza(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:

        if update.message.from_user.id == 527634720:
            await update.message.reply_text("*controllo chat superato, ciao Sequoia* ✅\n\n usa /help per scoprire i comandi", parse_mode='MarkdownV2')
        else:
            await update.message.reply_text(f"controllo chat non superato ❌, questo bot puo' essere usato *solo in gruppi autorizzati\.*\nIl tuo id e' `{update.effective_user.id}`\.`", parse_mode='MarkdownV2')
            return

        colonne = ['Materia', 'Tempo studiato', 'Tempo_studio',
                   'Tempo_pausa', 'nS', 'nP', 'Efficenza', 'Note']
        df = ModuloJson.read_csv_table("tabella_studio", colonne)
        ModuloJson.save_user_data("tabella_studio", df)

        if not df.empty and df.shape[0] > 0:
            await update.message.reply_text("Il DataFrame ha almeno una riga di dati, comincia ad usarlo con i comandi🎈🎉")
        else:
            await update.message.reply_text("Il *DataFrame è vuoto* \n\n🕴️", parse_mode='MarkdownV2')
    except Exception as e:
        await update.message.reply_text(e)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /help is issued."""
    help_message = '''
'''
    await update.message.reply_text(help_message, parse_mode="MarkdownV2")


async def stampa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Rimuovi 'id' dalle colonne
    colonne = ['Materia', 'Tempo studiato', 'Tempo_studio',
               'Tempo_pausa', 'nS', 'nP', 'Efficenza', 'Note']
    df = ModuloJson.read_csv_table("tabella_studio", colonne)
    print(df)
    # Ottieni tutti i valori unici dalla colonna 'Materia'
    materie_unique = df['Materia'].unique()

    tempo_studiato_per_materia = df.groupby('Materia')['Tempo studiato'].sum()

    # Creazione del grafico a torta
    plt.figure(figsize=(8, 6))
    plt.pie(tempo_studiato_per_materia, labels=tempo_studiato_per_materia.index,
            autopct='%1.1f%%', startangle=140, wedgeprops={"linewidth": 1, "edgecolor": "white"})
    plt.title('Distribuzione del tempo di studio per materia')
    plt.axis('equal')  # Assicura che il grafico sia circolare
    # Salva il grafico come byte
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Converti i dati in una stringa formattata per la caption
    caption = "Distribuzione del tempo di studio per materia\n\n"
    for materia, minuti in tempo_studiato_per_materia.items():
        ore = minuti / 60
        caption += f"*{materia}*: {ore:.2f} ore\n"
    esc_caption = ModuloJson.escape_special_chars(caption)
    # Invia l'immagine e la caption tramite Telegram
    photo = buffer.getvalue()
    # print(caption)
    # print(esc_caption)
    await update.message.reply_photo(photo, caption=esc_caption, parse_mode="MarkdownV2")


def main() -> int:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("focus", start_focus_mode)],
        states={
            MATERIA: [
                CallbackQueryHandler(
                    salva_materia, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(
                    salva_materia, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(
                    salva_materia, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(
                    salva_materia, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(FIVE) + "$"),
            ],
            TEMPO_STUDIO: [
                CallbackQueryHandler(
                    salva_t_studio, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(
                    salva_t_studio, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(
                    salva_t_studio, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(
                    salva_t_studio, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(
                    salva_t_studio, pattern="^" + str(FIVE) + "$"),
                CallbackQueryHandler(
                    salva_t_studio, pattern="^" + str(SIX) + "$"),
                CallbackQueryHandler(
                    salva_t_studio, pattern="^" + str(SEVEN) + "$"),
                CallbackQueryHandler(
                    salva_t_studio, pattern="^" + str(EIGHT) + "$"),
                CallbackQueryHandler(
                    salva_t_studio, pattern="^" + str(NINE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TEN) + "$"),
            ],
            TEMPO_PAUSA: [
                CallbackQueryHandler(
                    salva_t_pausa, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(
                    salva_t_pausa, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(
                    salva_t_pausa, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(
                    salva_t_pausa, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(
                    salva_t_pausa, pattern="^" + str(FIVE) + "$"),
                CallbackQueryHandler(
                    salva_t_pausa, pattern="^" + str(SIX) + "$"),
                CallbackQueryHandler(
                    salva_t_pausa, pattern="^" + str(SEVEN) + "$"),
                CallbackQueryHandler(
                    salva_t_pausa, pattern="^" + str(EIGHT) + "$"),
                CallbackQueryHandler(
                    salva_t_pausa, pattern="^" + str(NINE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TEN) + "$"),
            ],
            STUDIO: [
                CallbackQueryHandler(studio, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salva, pattern="^" + str(TWO) + "$"),
            ],
            PAUSA: [
                CallbackQueryHandler(pausa, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salva, pattern="^" + str(TWO) + "$"),
            ],
            STOP_SAVE: [
                CallbackQueryHandler(salva, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salva, pattern="^" + str(TWO) + "$"),
            ],
            END: [
                CallbackQueryHandler(salva, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(
                    start_focus_mode, pattern="^" + str(TWO) + "$"),
            ],

        },
        fallbacks=[CommandHandler("start", start_focus_mode)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    application.add_handler(CommandHandler("start", inizializza))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("print", stampa))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
