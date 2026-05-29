from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    ChatMemberHandler,
    PollAnswerHandler,
    MessageHandler,
    filters,
)

TOKEN = -1003888263128

# SE COMPLETA AUTOMÁTICAMENTE AL VER LA ENCUESTA
POLL_ID = "PONER_ID_ENCUESTA"

MENSAJE = """
🚨 Bienvenido.

Para poder hablar en el grupo:

1. Respondé la encuesta de edades fijada arriba.
2. Una vez respondida serás habilitado automáticamente.
"""

# -----------------------------------
# NUEVOS MIEMBROS
# -----------------------------------
async def nuevo_miembro(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_member = update.chat_member

    if (
        chat_member.old_chat_member.status in ["left", "kicked"]
        and chat_member.new_chat_member.status in ["member", "restricted"]
    ):

        usuario = chat_member.new_chat_member.user
        chat_id = update.effective_chat.id

        try:

            # SILENCIAR
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=usuario.id,
                permissions=ChatPermissions(
                    can_send_messages=False
                )
            )

            # MENSAJE
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"{usuario.mention_html()} {MENSAJE}",
                parse_mode="HTML"
            )

            print(f"{usuario.full_name} silenciado.")

        except Exception as e:
            print(e)

# -----------------------------------
# DETECTAR ENCUESTA
# -----------------------------------
async def detectar_encuesta(update: Update, context: ContextTypes.DEFAULT_TYPE):

    poll = update.message.poll

    print("\n======================")
    print("ID DE LA ENCUESTA:")
    print(poll.id)
    print("======================\n")

# -----------------------------------
# CUANDO ALGUIEN VOTA
# -----------------------------------
async def voto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    respuesta = update.poll_answer

    user_id = respuesta.user.id
    poll_id = respuesta.poll_id

    # SOLO NUESTRA ENCUESTA
    if poll_id != POLL_ID:
        return

    try:

        # OBTENER CHAT
        chats = await context.bot.get_updates()

        # DESMUTEAR EN TODOS LOS GRUPOS DONDE ESTÉ
        # (simplificación práctica)
        for upd in chats:

            if upd.effective_chat:

                chat_id = upd.effective_chat.id

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

                    print(f"Usuario {user_id} habilitado.")

                except:
                    pass

    except Exception as e:
        print(e)

# -----------------------------------
# APP
# -----------------------------------
app = ApplicationBuilder().token(TOKEN).build()

# NUEVOS USUARIOS
app.add_handler(
    ChatMemberHandler(
        nuevo_miembro,
        ChatMemberHandler.CHAT_MEMBER
    )
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
```
