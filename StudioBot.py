#!/usr/bin/env python
# pylint: disable=unused-argument, import-error
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to keep track of your study and study better
"""

import logging, time, ModuloJson, ModuloScelte

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update ,ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler,ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv
import os

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
MATERIA, TEMPO_STUDIO, TEMPO_PAUSA, CICLO_FOCUS, STOP , END = range(6)
# Callback data
ONE, TWO, THREE, FOUR , FIVE, SIX, SEVEN, EIGHT, NINE, TEN, ELEVEN, TWELVE = range(12)

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
                'Efficenza': 0, 
                'Note': "?"
                }
    colonne = ['Materia', 'Tempo studiato','Tempo_studio','Tempo_pausa', 'Efficenza', 'Note']

    df = ModuloJson.read_csv_table("tabella_studio", colonne)
    materie_unique = df['Materia'].unique()  # Ottieni tutti i valori unici dalla colonna 'Materia'
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton("Telecomunicazioni", callback_data=str(ONE)),
            InlineKeyboardButton("Internet and Security", callback_data=str(TWO)),
        ],
        [
            InlineKeyboardButton("Algoritmi per l'Ingegneria", callback_data=str(THREE)),
            InlineKeyboardButton("Automazione Industriale", callback_data=str(FOUR)),
        ],
        [
            InlineKeyboardButton("Esci", callback_data=str(FIVE)),
            #InlineKeyboardButton("6", callback_data=str(SIX)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("Start handler, Choose a route", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return MATERIA

async def salva_materia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    #print(query.data)
    materia = ModuloScelte.getSubject(int(query.data))
    #print(materia)
    global tempInfo
    tempInfo["Materia"] = materia
    #print(tempInfo)
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
    #print(query.data)
    studio = ModuloScelte.getStudyTime(int(query.data))
    #print(materia)
    global tempInfo
    tempInfo["Tempo_studio"] = studio
    #print(tempInfo)
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
    #print(query.data)
    pausa = ModuloScelte.getPauseTime(int(query.data))
    #print(materia)
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
    return CICLO_FOCUS

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END

# Define a few command handlers. These usually take the two arguments update and context.
async def inizializza(update: Update, context: ContextTypes.DEFAULT_TYPE)  -> int:
    """Send a message when the command /start is issued."""
    try:

        if update.message.from_user.id == 527634720:
            await update.message.reply_text("*controllo chat superato, ciao Sequoia* ✅\n\n usa /help per scoprire i comandi", parse_mode='MarkdownV2')
        else:
            await update.message.reply_text(f"controllo chat non superato ❌, questo bot puo' essere usato *solo in gruppi autorizzati\.*\nIl tuo id e' `{update.effective_user.id}`\.`", parse_mode='MarkdownV2')
            return
        
        colonne = ['Materia', 'Tempo studiato', 'Efficenza', 'Note']
        df = ModuloJson.read_csv_table("tabella_studio", colonne)
        ModuloJson.save_user_data("tabella_studio", df)
        if not df.empty and df.shape[0] > 0:
            await update.message.reply_text("Il DataFrame ha almeno una riga di dati, comincia ad usarlo con i comandi🎈🎉")
        else:
            await update.message.reply_text("Il *DataFrame è vuoto* \n\n🕴️", parse_mode='MarkdownV2')
    except Exception as e:
        await update.message.reply_text(e)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE)  -> int:
    """Send a message when the command /help is issued."""
    help_message = '''
Possibili comandi:
/reps \- _visualizza tutte le reputazioni_
/newtrade \- _inserisci un nuovo scambio_
/help \- _questo messaggio_'''
    await update.message.reply_text(help_message, parse_mode="MarkdownV2")

async def stampa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    colonne = ['username', 'reputazione', 'volume']  # Rimuovi 'id' dalle colonne
    df = ModuloJson.read_csv_table("reputazioni", colonne)
    
    if not df.empty and df.shape[0] > 0:
        # Formatta manualmente i dati come una tabella        
        # Intestazione della tabella
        message = "*Username \| Reputazione \| Volume*\n"
        # Aggiungi righe
        for index, row in df.iterrows():
            message += f"@{ModuloJson.escape_special_chars(row['username'])} \| {int(row['reputazione'])} \| {row['volume']}\n"

        await update.message.reply_text(message, parse_mode="MarkdownV2")
    else:
        await update.message.reply_text("Il *DataFrame è vuoto* o contiene solo i titoli delle colonne\n\n*Chiedi ad un admin di assegnare le prime reputazioni a persone fidate*", parse_mode="MarkdownV2")
        return



def main()  -> int:
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
                CallbackQueryHandler(salva_materia, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salva_materia, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(salva_materia, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(salva_materia, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(FIVE) + "$"),
                #CallbackQueryHandler(four, pattern="^" + str(SIX) + "$"),
                ],
            TEMPO_STUDIO: [
                CallbackQueryHandler(salva_t_studio, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salva_t_studio, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(salva_t_studio, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(salva_t_studio, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(salva_t_studio, pattern="^" + str(FIVE) + "$"),
                CallbackQueryHandler(salva_t_studio, pattern="^" + str(SIX) + "$"),
                CallbackQueryHandler(salva_t_studio, pattern="^" + str(SEVEN) + "$"),
                CallbackQueryHandler(salva_t_studio, pattern="^" + str(EIGHT) + "$"),
                CallbackQueryHandler(salva_t_studio, pattern="^" + str(NINE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TEN) + "$"),
                ],
            TEMPO_PAUSA: [
                CallbackQueryHandler(salva_t_pausa, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(salva_t_pausa, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(salva_t_pausa, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(salva_t_pausa, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(salva_t_pausa, pattern="^" + str(FIVE) + "$"),
                CallbackQueryHandler(salva_t_pausa, pattern="^" + str(SIX) + "$"),
                CallbackQueryHandler(salva_t_pausa, pattern="^" + str(SEVEN) + "$"),
                CallbackQueryHandler(salva_t_pausa, pattern="^" + str(EIGHT) + "$"),
                CallbackQueryHandler(salva_t_pausa, pattern="^" + str(NINE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TEN) + "$"),
                ],
            CICLO_FOCUS: [
                #CallbackQueryHandler(one, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TWO) + "$"),
                ],
            STOP: [
                #CallbackQueryHandler(one, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TWO) + "$"),
                ],
            END: [
                CallbackQueryHandler(end, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(start_focus_mode, pattern="^" + str(TWO) + "$"),
                ],

        },
        fallbacks=[CommandHandler("start", start_focus_mode)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # application.add_handler(CommandHandler("manualRep", manualRep))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("print", stampa))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    


if __name__ == "__main__":
    main()