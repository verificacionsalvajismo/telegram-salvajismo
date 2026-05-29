import os

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

POLL_ID = "PONER_ID_REAL"

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

    chat_member = update.chat_member

    if (
        chat_member.old_chat_member.status in ["left", "kicked"]
        and chat_member.new_chat_member.status in ["member", "restricted"]
    ):

        usuario = chat_member.new_chat_member.user
        chat_id = update.effective_chat.id

        usuarios[usuario.id] = chat_id

        try:

            # =========================================
            # SILENCIAR
            # =========================================

            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=usuario.id,
                permissions=ChatPermissions(
                    can_send_messages=False
                )
            )

            # =========================================
            # BOTONES IDIOMA
            # =========================================

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🇪🇸 Español", callback_data=f"es:{usuario.id}")
                ],
                [
                    InlineKeyboardButton("🇺🇸 English", callback_data=f"en:{usuario.id}")
                ],
                [
                    InlineKeyboardButton("🇧🇷 Português", callback_data=f"pt:{usuario.id}")
                ]
            ])

            # =========================================
            # MENSAJE
            # =========================================

            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"{usuario.mention_html()}\n\n"
                    "🌎 Seleccioná tu idioma / Select your language / Selecione seu idioma"
                ),
                parse_mode="HTML",
                reply_markup=keyboard
            )

            print(f"{usuario.full_name} silenciado.")

        except Exception as e:
            print(e)

# =========================================
# SELECCIONAR IDIOMA
# =========================================

async def idioma(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data.split(":")

    lang = data[0]
    user_id = int(data[1])

    # SOLO EL USUARIO PUEDE TOCAR SUS BOTONES
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
    print("======================\n")
    print(poll)

# =========================================
# CUANDO ALGUIEN VOTA
# =========================================

async def voto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    respuesta = update.poll_answer

    user_id = respuesta.user.id
    poll_id = respuesta.poll_id

    # SOLO NUESTRA ENCUESTA
    if poll_id != POLL_ID:
        return

    # SI NO EXISTE
    if user_id not in usuarios:
        return

    chat_id = usuarios[user_id]

    try:

        # =========================================
        # DESMUTEAR
        # =========================================

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

        # =========================================
        # MENSAJE
        # =========================================

        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Usuario habilitado automáticamente."
        )

        print(f"Usuario {user_id} habilitado.")

    except Exception as e:
        print(e)

# =========================================
# APP
# =========================================

app = ApplicationBuilder().token(TOKEN).build()

# NUEVOS USUARIOS
app.add_handler(
    ChatMemberHandler(
        nuevo_miembro,
        ChatMemberHandler.CHAT_MEMBER
    )
)

# BOTONES IDIOMA
app.add_handler(
    CallbackQueryHandler(idioma)
)

# DETECTAR ENCUESTA
app.add_handler(
    MessageHandler(
        filters.POLL,
        detectar_encuesta
    )
)

# DETECTAR VOTOS
app.add_handler(
    PollAnswerHandler(voto)
)

print("BOT FUNCIONANDO")

app.run_polling()
