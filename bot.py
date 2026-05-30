import os
import asyncio

from telegram import (
    Update,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    ChatMemberHandler,
    ChatJoinRequestHandler,
    PollAnswerHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
# =========================================
# TOKEN DEL BOT
# =========================================

TOKEN ="7929600422:AAGKteeUmQOO3ckzGHWVuIEcVivirBmB0S8"

# =========================================
# ID DE LA ENCUESTA
# PEGAR EL ID REAL
# =========================================

POLL_ID = "4958646825356624164"

# =========================================
# GUARDAR USUARIOS
# user_id -> chat_id
# =========================================

usuarios = {}

# =========================================
# MENSAJES
# =========================================

TEXTOS = {

    "es": """
🚨 Bienvenido.

Para poder hablar en el grupo:

1. Respondé la encuesta de edades fijada arriba.
2. Luego quedarás habilitado automáticamente.
""",

    "en": """
🚨 Welcome.

To speak in the group:

1. Answer the pinned age poll above.
2. You will then be automatically unmuted.
""",

    "pt": """
🚨 Bem-vindo.

Para falar no grupo:

1. Responda à enquete de idade fixada acima.
2. Depois você será desbloqueado automaticamente.
"""
}

# =========================================
# NUEVOS MIEMBROS
# =========================================

async def nuevo_miembro(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("================================")
    print("NUEVO MIEMBRO")
    print(update)
    print("================================")

    chat_id = update.effective_chat.id

    for usuario in update.message.new_chat_members:

        usuarios[usuario.id] = chat_id

        try:

            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=usuario.id,
                permissions=ChatPermissions(
                    can_send_messages=False
                )
            )

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🇪🇸 Español",
                        callback_data=f"es:{usuario.id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🇺🇸 English",
                        callback_data=f"en:{usuario.id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🇧🇷 Português",
                        callback_data=f"pt:{usuario.id}"
                    )
                ]
            ])

           msg = await context.bot.send_message(
    chat_id=chat_id,
    text=(
        f"{usuario.mention_html()}\n\n"
        "🌎 Seleccioná tu idioma / Select your language / Selecione seu idioma"
    ),
    parse_mode="HTML",
    reply_markup=keyboard
)

context.application.create_task(
    borrar_mensaje(
        context,
        chat_id,
        msg.message_id,
        150
    )
)

            print(f"{usuario.full_name} silenciado")

        except Exception as e:
            print("ERROR:", e)

# =========================================
# SOLICITUDES DE INGRESO
# =========================================

async def solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("================================")
    print("SOLICITUD DETECTADA")
    print(update)
    print("================================")


# =========================================
# SELECCIONAR IDIOMA
# =========================================

async def idioma(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data.split(":")

    lang = data[0]
    user_id = int(data[1])

    if query.from_user.id != user_id:
        return

    texto = TEXTOS[lang]

    await query.edit_message_text(
        text=texto
    )


# =========================================
# DETECTAR ENCUESTA
# =========================================

async def detectar_encuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):

    poll = update.message.poll

    print("\n======================")
    print("ID DE LA ENCUESTA:")
    print(poll.id)
    print("======================")
    print(poll)
    print("======================\n")


# =========================================
# CUANDO ALGUIEN VOTA
# =========================================

async def voto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    respuesta = update.poll_answer

    print("==============")
    print("VOTO DETECTADO")
    print("Usuario:", respuesta.user.id)
    print("Encuesta:", respuesta.poll_id)
    print("Opciones:", respuesta.option_ids)
    print("==============")

    user_id = respuesta.user.id
    poll_id = respuesta.poll_id

    if poll_id != POLL_ID:
        return

    if user_id not in usuarios:
        print("Usuario no encontrado en memoria.")
        return

    chat_id = usuarios[user_id]

    try:

        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )

       msg = await context.bot.send_message(
    chat_id=chat_id,
    text=f"✅ {respuesta.user.mention_html()} habilitado automáticamente.",
    parse_mode="HTML"
)

context.application.create_task(
    borrar_mensaje(
        context,
        chat_id,
        msg.message_id,
        60
    )
)

        print(f"Usuario {user_id} habilitado.")

    except Exception as e:
        print("ERROR voto:", e)

async def borrar_mensaje(context, chat_id, message_id, segundos):

    await asyncio.sleep(segundos)

    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
    except:
        pass
# =========================================
# DEBUG
# =========================================

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("================================")
    print(update)
    print("================================")


# =========================================
# APP
# =========================================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        nuevo_miembro
    )
)

app.add_handler(
    ChatJoinRequestHandler(solicitud)
)

app.add_handler(
    CallbackQueryHandler(idioma)
)

app.add_handler(
    MessageHandler(
        filters.POLL,
        detectar_encuesta
    )
)

app.add_handler(
    PollAnswerHandler(voto)
)

app.add_handler(
    MessageHandler(
        filters.ALL,
        debug
    ),
    group=999
)

print("BOT FUNCIONANDO")
print(awaiting := "HANDLERS CARGADOS")

app.run_polling()
