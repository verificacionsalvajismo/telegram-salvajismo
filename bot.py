import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions
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

TOKEN = "7929600422:AAGKteeUmQOO3ckzGHWVuIEcVivirBmB0S8"

# =========================================
# GUARDAR USUARIOS
# =========================================

usuarios = {}

EDADES_SILENCIAR = [
    "12-14",
    "15-17"
]

EDADES_PERMITIDAS = [
    "18-19",
    "20-22",
    "23-25",
    "26-28",
    "29-30"
]

EDADES_EXPULSAR = [
    "+30",
    "+35",
    "+40",
    "+45",
    "+50"
]

# =========================================
# NUEVOS MIEMBROS
# =========================================

async def nuevo_miembro(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    for usuario in update.message.new_chat_members:

        if usuario.is_bot:
            continue

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "12-14",
                    callback_data=f"edad:12-14:{usuario.id}"
                ),
                InlineKeyboardButton(
                    "15-17",
                    callback_data=f"edad:15-17:{usuario.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "18-19",
                    callback_data=f"edad:18-19:{usuario.id}"
                ),
                InlineKeyboardButton(
                    "20-22",
                    callback_data=f"edad:20-22:{usuario.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "23-25",
                    callback_data=f"edad:23-25:{usuario.id}"
                ),
                InlineKeyboardButton(
                    "26-28",
                    callback_data=f"edad:26-28:{usuario.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "29-30",
                    callback_data=f"edad:29-30:{usuario.id}"
                ),
                InlineKeyboardButton(
                    "+30",
                    callback_data=f"edad:+30:{usuario.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "+35",
                    callback_data=f"edad:+35:{usuario.id}"
                ),
                InlineKeyboardButton(
                    "+40",
                    callback_data=f"edad:+40:{usuario.id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "+45",
                    callback_data=f"edad:+45:{usuario.id}"
                ),
                InlineKeyboardButton(
                    "+50",
                    callback_data=f"edad:+50:{usuario.id}"
                )
            ]
        ])

        if usuario.username:
            nombre = f"@{usuario.username}"
            parse_mode = None
        else:
            nombre = usuario.mention_html()
            parse_mode = "HTML"

        mensaje = await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"👋 Bienvenido/Welcome {nombre}\n\n"

                "🇪🇸 Selecciona tu edad usando los botones de abajo. Ignora este mensaje y serás expulsado por el bot en unos minutos.\n\n"

                "🇺🇸 Select your age using the buttons below. Ignore this message and you will be removed by the bot in a few minutes.\n\n"

                "🇧🇷Selecione sua idade usando os botões abaixo. Ignore esta mensagem e você será removido pelo bot em alguns minutos .\n\n"
                
            ),
            parse_mode=parse_mode,
            reply_markup=keyboard
        )

        usuarios[usuario.id] = {
            "chat_id": chat_id,
            "respondio": False,
            "mensaje_id": mensaje.message_id
        }

        asyncio.create_task(
            controlar_tiempo(
                context,
                chat_id,
                usuario.id
            )
        )

# =========================================
# CALLBACK DE EDAD
# =========================================

async def edad_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    datos = query.data.split(":")

    edad = datos[1]
    user_id = int(datos[2])

    if query.from_user.id != user_id:
        return

    if user_id not in usuarios:
        return

    usuarios[user_id]["respondio"] = True

    chat_id = usuarios[user_id]["chat_id"]

    try:
        await query.message.delete()
    except:
        pass

    if edad in EDADES_SILENCIAR:

        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False
            )
        )

        usuarios.pop(user_id, None)
        return

    if edad in EDADES_PERMITIDAS:

        usuarios.pop(user_id, None)
        return

    if edad in EDADES_EXPULSAR:

        await context.bot.ban_chat_member(
            chat_id,
            user_id
        )

        usuarios.pop(user_id, None)
        return

# =========================================
# CONTROL TIEMPO
# =========================================

async def controlar_tiempo(
    context,
    chat_id,
    user_id
):

    await asyncio.sleep(300)

    datos = usuarios.get(user_id)

    if not datos:
        return

    if datos["respondio"]:
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

        try:
            await context.bot.delete_message(
                chat_id,
                datos["mensaje_id"]
            )
        except:
            pass

        usuarios.pop(user_id, None)

    except Exception as e:
        print(e)

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
    CallbackQueryHandler(
        edad_callback
    )
)

print("BOT FUNCIONANDO")
print("HANDLERS CARGADOS")

async def error_handler(update, context):
    print("ERROR:")
    print(context.error)

app.add_error_handler(error_handler)

app.run_polling(
    drop_pending_updates=True
)
