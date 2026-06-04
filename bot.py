import os
import asyncio
import time

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
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
# =========================================
# TOKEN DEL BOT
# =========================================

TOKEN ="7929600422:AAGKteeUmQOO3ckzGHWVuIEcVivirBmB0S8"

# =========================================
# GUARDAR USUARIOS
# =========================================

usuarios = {}

# usuario_id -> tarea de expulsión
temporizadores = {}

# =========================================
# TU ID DE TELEGRAM
# =========================================

ADMIN_ID = -1003888263128

# =========================================
# MENSAJES DE VERIFICACIÓN
# =========================================

TEXTOS = {

    "es": """
🚨 Bienvenido.

Por protección de los miembros y seguridad del grupo, debes verificarte.

✅ Envía tu EDAD y  una FOTO o VIDEO (preferiblemente desnudo o en boxer) donde aparezcas haciendo una o más de estas señas:

👌 🖖 🤞 🤘 🤙

Si no completas la verificación dentro del tiempo establecido serás expulsado automáticamente.

Usa los botones de abajo para continuar.
""",

    "en": """
🚨 Welcome.

For member protection and group safety, you must verify yourself.

✅ Send your AGE and a PHOTO or VIDEO showing yourself making one or more of these hand signs:

👌 🖖 🤞 🤘 🤙

Also include your age.

If verification is not completed within the allowed time, you will be automatically removed.

Use the buttons below to continue.
""",

    "pt": """
🚨 Bem-vindo.

Para proteção dos membros e segurança do grupo, você deve se verificar.

✅ Envie sua IDADE também uma FOTO ou VÍDEO mostrando você fazendo um ou mais destes sinais:

👌 🖖 🤞 🤘 🤙

Se a verificação não for concluída dentro do prazo, você será removido automaticamente.

Use os botões abaixo para continuar.
"""
}

# =========================================
# NUEVOS MIEMBROS
# =========================================

async def nuevo_miembro(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    for usuario in update.message.new_chat_members:

        usuarios[usuario.id] = {
            "chat_id": chat_id,
            "verificado": False
        }

        try:

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "✅ Sí, voy a verificarme",
                        callback_data=f"ok:{usuario.id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "❌ No quiero verificarme",
                        callback_data=f"no:{usuario.id}"
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
                parse_mode="HTML",
                text=(
                    f"{usuario.mention_html()}\n\n"
                    "👋 Bienvenido.\n\n"
                    "Por protección de los miembros y seguridad del grupo "
                    "debes verificarte.\n\n"
                    "📸 Enviá una FOTO o VIDEO mostrando tu rostro "
                    "haciendo una o más de estas señas:\n\n"
                    "👌 🖖 🤞 🤘 🤙\n\n"
                    "Además indicá tu edad.\n\n"
                    "⏳ Disponés de 10 minutos.\n\n"
                    "Si necesitás más tiempo avisá en el grupo."
                ),
                reply_markup=keyboard
            )

            asyncio.create_task(
                borrar_mensaje(
                    context,
                    chat_id,
                    msg.message_id,
                    1800
                )
            )

            asyncio.create_task(
                controlar_tiempo(
                    context,
                    chat_id,
                    usuario.id
                )
            )

            print(f"{usuario.full_name} registrado")

        except Exception as e:
            print("ERROR:", e)

# =========================================
# SOLICITUDES
# =========================================

async def solicitud(update: Update, context: ContextTypes.DEFAULT_TYPE):

    print("================================")
    print("SOLICITUD DETECTADA")
    print(update)
    print("================================")

# =========================================
# BOTONES
# =========================================

async def idioma(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    accion, user_id = query.data.split(":")
    user_id = int(user_id)

    if query.from_user.id != user_id:
        return

    if accion == "en":

        await query.edit_message_text(
            "Welcome.\n\n"
            "For safety reasons you must verify yourself.\n\n"
            "Send a photo or video showing your face while making:\n\n"
            "👌 🖖 🤞 🤘 🤙\n\n"
            "Include your age.\n\n"
            "You have 10 minutes."
        )

        return

    if accion == "pt":

        await query.edit_message_text(
            "Bem-vindo.\n\n"
            "Por segurança você deve se verificar.\n\n"
            "Envie uma foto ou vídeo mostrando o rosto fazendo:\n\n"
            "👌 🖖 🤞 🤘 🤙\n\n"
            "Informe também sua idade.\n\n"
            "Você tem 10 minutos."
        )

        return

    if accion == "no":

        datos = usuarios.get(user_id)

        if datos:

            await context.bot.ban_chat_member(
                datos["chat_id"],
                user_id
            )

            await context.bot.unban_chat_member(
                datos["chat_id"],
                user_id
            )

        return

    if accion == "ok":

        await query.answer(
            "Esperamos tu foto o video."
        )

# =========================================
# FOTO O VIDEO
# =========================================

async def recibir_verificacion(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    usuario = update.effective_user

    if usuario.id not in usuarios:
        return

    tiene_foto = update.message.photo
    tiene_video = update.message.video

    if not tiene_foto and not tiene_video:
        return

    usuarios[usuario.id]["verificado"] = True

    try:

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"📥 Nueva verificación\n\n"
                f"Usuario: {usuario.full_name}\n"
                f"ID: {usuario.id}"
            )
        )

    except Exception as e:
        print(e)

# =========================================
# APROBAR
# =========================================

async def aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        return

    try:

        user_id = int(context.args[0])

        if user_id not in usuarios:
            return

        usuarios[user_id]["verificado"] = True

        chat_id = usuarios[user_id]["chat_id"]

        msg = await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Verificación aprobada. Bienvenido."
        )

        asyncio.create_task(
            borrar_mensaje(
                context,
                chat_id,
                msg.message_id,
                120
            )
        )

        print(f"{user_id} aprobado")

    except Exception as e:
        print(e)

# =========================================
# RECHAZAR
# =========================================

async def rechazar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        return

    try:

        user_id = int(context.args[0])

        if user_id not in usuarios:
            return

        chat_id = usuarios[user_id]["chat_id"]

        await context.bot.ban_chat_member(
            chat_id,
            user_id
        )

        await context.bot.unban_chat_member(
            chat_id,
            user_id
        )

        print(f"{user_id} rechazado")

    except Exception as e:
        print(e)

# =========================================
# CONTROL TIEMPO
# =========================================

async def controlar_tiempo(
    context,
    chat_id,
    user_id
):

    await asyncio.sleep(600)

    datos = usuarios.get(user_id)

    if not datos:
        return

    if datos["verificado"]:
        return

    try:

        await context.bot.ban_chat_member(
            chat_id,
            user_id
        )

        await context.bot.unban_chat_member(
            chat_id,
            user_id
        )

        print(f"{user_id} expulsado")

    except Exception as e:
        print(e)

# =========================================
# BORRAR MENSAJES
# =========================================

async def borrar_mensaje(
    context,
    chat_id,
    message_id,
    segundos
):

    await asyncio.sleep(segundos)

    try:

        await context.bot.delete_message(
            chat_id,
            message_id
        )
    except:
        pass

from telegram.ext import CommandHandler

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
    CallbackQueryHandler(idioma)
)

app.add_handler(
    MessageHandler(
        filters.PHOTO | filters.VIDEO,
        recibir_verificacion
    )
)

app.add_handler(
    CommandHandler(
        "aprobar",
        aprobar
    )
)

app.add_handler(
    CommandHandler(
        "rechazar",
        rechazar
    )
)

print("BOT FUNCIONANDO")
print("HANDLERS CARGADOS")

app.run_polling()
