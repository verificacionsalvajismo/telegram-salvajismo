import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
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

# =========================================
# TU ID DE TELEGRAM
# =========================================

ADMIN_ID = 8011642705

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
                    "Por protección de los miembros y seguridad del grupo debes verificarte.\n\n"
                    "📸𝐄𝐧𝐯í𝐚 𝐭𝐮 𝐄𝐃𝐀𝐃 𝐲  𝐮𝐧𝐚 𝐅𝐎𝐓𝐎 𝐨 𝐕𝐈𝐃𝐄𝐎 (𝐨𝐛𝐥𝐢𝐠𝐚𝐭𝐨𝐫𝐢𝐚𝐦𝐞𝐧𝐭𝐞 𝐝𝐞𝐬𝐧𝐮𝐝𝐨 𝐨 𝐞𝐧 𝐛𝐨𝐱𝐞𝐫) 𝐡𝐚𝐜𝐢𝐞𝐧𝐝𝐨 𝐮𝐧𝐚 𝐨 𝐦á𝐬 𝐝𝐞 𝐞𝐬𝐭𝐚𝐬 𝐬𝐞ñ𝐚𝐬:\n\n"
                    "👌 🖖 🤞 🤘 🤙\n\n"
                    "⏳ Disponés de 10 minutos o escribe en el chat que necesitas más tiempo.\n\n"
                    "Si no completás la verificación serás expulsado automáticamente."
                ),
                reply_markup=keyboard
            )

            asyncio.create_task(
                borrar_mensaje(
                    context,
                    chat_id,
                    msg.message_id,
                    600
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
            "𝐒𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐀𝐆𝐄 𝐚𝐧𝐝 𝐚 𝐏𝐇𝐎𝐓𝐎 𝐨𝐫 𝐕𝐈𝐃𝐄𝐎 (𝐦𝐮𝐬𝐭 𝐛𝐞 𝐧𝐮𝐝𝐞 𝐨𝐫 𝐢𝐧 𝐮𝐧𝐝𝐞𝐫𝐰𝐞𝐚𝐫) 𝐦𝐚𝐤𝐢𝐧𝐠 𝐨𝐧𝐞 𝐨𝐫 𝐦𝐨𝐫𝐞 𝐨𝐟 𝐭𝐡𝐞 𝐟𝐨𝐥𝐥𝐨𝐰𝐢𝐧𝐠 𝐬𝐢𝐠𝐧𝐬:\n\n"
            "👌 🖖 🤞 🤘 🤙\n\n"
            "You have 10 minutes or request more time by writing it in the chat.\n\n"
        )

        asyncio.create_task(
            borrar_mensaje(
                context,
                query.message.chat.id,
                query.message.message_id,
                600
            )
        )

        return

    if accion == "pt":

        await query.edit_message_text(
            "Bem-vindo.\n\n"
            "Por segurança você deve se verificar.\n\n"
            "𝗘𝗻𝘃𝗶𝗲 𝘀𝘂𝗮 𝗜𝗗𝗔𝗗𝗘 𝗲 𝘂𝗺𝗮 𝗙𝗢𝗧𝗢 𝗼𝘂 𝗩𝗜𝗗𝗘𝗢 (𝗱𝗲𝘃𝗲 𝘀𝗲𝗿 𝘃𝗼𝗰ê 𝗻𝘂 𝗼𝘂 𝗱𝗲 𝗿𝗼𝘂𝗽𝗮 í𝗻𝘁𝗶𝗺𝗮) 𝗳𝗮𝘇𝗲𝗻𝗱𝗼 𝘂𝗺 𝗼𝘂 𝗺𝗮𝗶𝘀 𝗱𝗼𝘀 𝘀𝗲𝗴𝘂𝗶𝗻𝘁𝗲𝘀 𝘀𝗶𝗻𝗮𝗶𝘀:\n\n"
            "👌 🖖 🤞 🤘 🤙\n\n"
            "Você tem 10 minutosou solicite mais tempo escrevendo no chat.\n\n"
        )

        asyncio.create_task(
            borrar_mensaje(
                context,
                query.message.chat.id,
                query.message.message_id,
                600
            )
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

        return

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

    edad = ""

    if update.message.caption:
        edad = update.message.caption
    else:
        edad = "Sin edad indicada"

    try:

        if tiene_foto:

            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=update.message.photo[-1].file_id,
                caption=(
                    f"📥 Nueva verificación\n\n"
                    f"Usuario: {usuario.full_name}\n"
                    f"ID: {usuario.id}\n\n"
                    f"Edad / texto:\n{edad}"
                )
            )

        elif tiene_video:

            await context.bot.send_video(
                chat_id=ADMIN_ID,
                video=update.message.video.file_id,
                caption=(
                    f"📥 Nueva verificación\n\n"
                    f"Usuario: {usuario.full_name}\n"
                    f"ID: {usuario.id}\n\n"
                    f"Edad / texto:\n{edad}"
                )
            )

        print(f"{usuario.full_name} verificado")

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

print("BOT FUNCIONANDO")
print("HANDLERS CARGADOS")

async def error_handler(update, context):
    print("ERROR:")
    print(context.error)

app.add_error_handler(error_handler)

app.run_polling()
