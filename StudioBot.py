#!/usr/bin/env python
# pylint: disable=unused-argument, import-error
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to keep track of your study and study better
"""

import logging, time, ModuloJson

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update ,ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler,ConversationHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv
import os

load_dotenv()
bot_token = os.getenv("BOT_TOKEN")
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

SCEGLI_TEMPO , SALVA_VOLUME, CHECK_REP= range(3)

global tempInfo

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


async def inizioStudio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = '''
*Diamo inizio al focus
            🔇🤫
*'''
    await update.message.reply_text(message, parse_mode="MarkdownV2")
    global tempInfo

    colonne = ['Materia', 'Tempo studiato', 'Efficenza', 'Note']
    df = ModuloJson.read_csv_table("tabella_studio", colonne)

    materie_unique = df['Materia'].unique()  # Ottieni tutti i valori unici dalla colonna 'Materia'

    tempInfo = {'Materia': "?", 'Tempo studiato': "?", 'Efficenza': "?", 'Note': "?"}
    keyboard = []

    for materia in materie_unique:
        keyboard.append([InlineKeyboardButton(materia, callback_data=materia)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)
    return SCEGLI_TEMPO

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")

async def scegliTempo(update: Update, context: ContextTypes.DEFAULT_TYPE)  -> int:
    text = update.message.text
    try:
        global tempInfo

    except:
        await update.message.reply_text(f"hai cappato duro hermano, riprova", parse_mode="MarkdownV2")
        return SCEGLI_TEMPO

    return SALVA_VOLUME


async def salvaVolume(update: Update, context: ContextTypes.DEFAULT_TYPE)  -> int:
    try:
        text = update.message.text
        amount = int(text)
        global infoTrade
        infoTrade["volume"]=amount
        await update.message.reply_text(f"@{ModuloJson.escape_special_chars(infoTrade['user1'])}, @{ModuloJson.escape_special_chars(infoTrade['user2'])}\nper favore cliccate il seguente comando\n/conferma oppure annullate con /cancel", parse_mode="MarkdownV2")
    except: 
        await update.message.reply_text("Inserisci l'importo *in dollari \(us$\)* _\(solo numeri interi\)_ oppure annullate con /cancel", parse_mode="MarkdownV2")
        return SALVA_VOLUME
    return CHECK_REP

async def controllaReputazione(update: Update, context: ContextTypes.DEFAULT_TYPE)  -> int:
    text = update.message.text
    if text == "/caneclla":
        await update.message.reply_text("Ciao anon💭", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    global infoTrade
    username = update.message.from_user.username
    if (username == infoTrade['user1']):
        infoTrade['user1Up']= True
    if (username == infoTrade['user2']):
        infoTrade['user2Up']= True
    if (infoTrade['user1Up']==False or infoTrade['user2Up']==False):
        return CHECK_REP
    # cerco rep dei due user
    colonne = ['id', 'username', 'reputazione', 'volume']
    df = ModuloJson.read_csv_table("reputazioni", colonne)
    try: 
        # Seleziona la riga corrispondente al primo utente
        user1_row = df.loc[df['username'] == infoTrade['user1']]
        # Se l'utente esiste nel DataFrame
        if not user1_row.empty:
            # Ottieni la reputazione dell'utente
            rep1 = user1_row['reputazione'].values[0]
            vol1 = user1_row['volume'].values[0]
        else:
            await update.message.reply_text(f"Utente 1 {infoTrade['user1']} non trovato, richiedi a @eddichan di essere aggiunto")
            return ConversationHandler.END
        # Seleziona la riga corrispondente al primo utente
        user2_row = df.loc[df['username'] == infoTrade['user2']]
        # Se l'utente esiste nel DataFrame
        if not user2_row.empty:
            # Ottieni la reputazione dell'utente
            rep2 = user2_row['reputazione'].values[0]
            vol2 = user2_row['volume'].values[0]
        else:
            await update.message.reply_text(f"Utente 2 {infoTrade['user2']} non trovato, richiedi a @eddichan di essere aggiunto")
            return ConversationHandler.END
    except Exception as e:
        # Gestione delle eccezioni
        await update.message.reply_text(f"Annullo tutto, mi hai rotto il bot!")
        return ConversationHandler.END
    
    if rep1>0 and rep2>0:
        print("scambio possibile")
        rep1New = float(rep1+rep2/5)
        rep2New = float(rep2+rep1/5)
        df.loc[df['username'] == infoTrade['user1'], 'reputazione'] = rep1New
        df.loc[df['username'] == infoTrade['user2'], 'reputazione'] = rep2New

        df.loc[df['username'] == infoTrade['user1'], 'volume'] = vol1 + infoTrade['volume']
        df.loc[df['username'] == infoTrade['user2'], 'volume'] = vol2 + infoTrade['volume']
        ModuloJson.save_user_data("reputazioni", df)
        risposta=""
        risposta=risposta + f"✅La reputazione dell'utente *@{infoTrade['user1']}* è ora *\{int(rep1New)}*\n"
        risposta=risposta + f"✅La reputazione dell'utente *@{infoTrade['user2']}* è ora *\{int(rep2New)}*\n"
        await update.message.reply_text(risposta, parse_mode="MarkdownV2")


    else:
        await update.message.reply_text(f"non potete inserire nuove transazioni _senza una reputazione_, contattate @eddichan", parse_mode="MarkdownV2")
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE)  -> int:
    """Send a message when the command /help is issued."""
    help_message = '''
Possibili comandi:
/reps \- _visualizza tutte le reputazioni_
/newtrade \- _inserisci un nuovo scambio_
/help \- _questo messaggio_'''
    await update.message.reply_text(help_message, parse_mode="MarkdownV2")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Ciao anon💭", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

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
    
    tx= ConversationHandler(
        entry_points=[CommandHandler("s",inizioStudio)],
        states={
            SCEGLI_TEMPO: [CommandHandler("cancel", cancel),MessageHandler(filters.ALL, scegliTempo)],
            SALVA_VOLUME: [CommandHandler("cancel", cancel),MessageHandler(filters.ALL, salvaVolume),],
            CHECK_REP: [CommandHandler("cancel", cancel),CommandHandler(["conferma","cancella"], controllaReputazione),],
        },
        fallbacks=[CommandHandler("cancel", cancel),],
        per_user=False
    )
    # Add the conversation handler to the application
    application.add_handler(tx)    
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", inizializza))
    application.add_handler(CallbackQueryHandler(button))

    # application.add_handler(CommandHandler("manualRep", manualRep))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reps", stampa))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    


if __name__ == "__main__":
    main()