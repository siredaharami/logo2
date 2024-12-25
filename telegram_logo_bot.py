from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image, ImageDraw, ImageFont
import io

# Replace these with your actual values
api_id = 25742938
api_hash = "b35b715fe8dc0a58e8048988286fc5b6"
bot_token = "7796646089:AAG3yoXJRSI-D2A5w1kPraju_qpL_Xt3JO8"

app = Client("logo_maker_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

users_data = {}

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Welcome to the Logo Maker Bot!\nPlease send me an image to start.")

@app.on_message(filters.photo)
async def handle_photo(client, message):
    photo = await message.download()
    with open(photo, "rb") as file:
        photo_bytes = file.read()

    users_data[message.chat.id] = {'photo': photo_bytes, 'position': (10, 10)}
    await message.reply_text("I got the image! Now send me the text you want to add to the image.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_text(client, message):
    chat_id = message.chat.id
    if chat_id in users_data and 'photo' in users_data[chat_id]:
        text = message.text
        users_data[chat_id]['text'] = text
        await send_edit_menu(client, chat_id)

async def send_edit_menu(client, chat_id):
    await client.send_message(chat_id, "Edit options:",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("♥️ Red", callback_data='color_red'), InlineKeyboardButton("💚 Green", callback_data='color_green')],
                [InlineKeyboardButton("💙 Blue", callback_data='color_blue'), InlineKeyboardButton("🖤 Black", callback_data='color_black')],
                [InlineKeyboardButton("Choose Font", callback_data='choose_font')],
                [InlineKeyboardButton("Add Shadow", callback_data='add_shadow')],
                [InlineKeyboardButton("Choose Stroke Color", callback_data='choose_stroke')],
                [
                    InlineKeyboardButton("⬆️", callback_data='move_up'),
                    InlineKeyboardButton("⬅️", callback_data='move_left'),
                    InlineKeyboardButton("➡️", callback_data='move_right'),
                    InlineKeyboardButton("⬇️", callback_data='move_down')
                ],
                [
                    InlineKeyboardButton("⬆️⬆️ Fast", callback_data='move_up_fast'),
                    InlineKeyboardButton("⬅️⬅️ Fast", callback_data='move_left_fast'),
                    InlineKeyboardButton("➡️➡️ Fast", callback_data='move_right_fast'),
                    InlineKeyboardButton("⬇️⬇️ Fast", callback_data='move_down_fast')
                ],
                [InlineKeyboardButton("Choose Language", callback_data='choose_language')],
                [InlineKeyboardButton("Download", callback_data='download_logo')],
                [InlineKeyboardButton("Back", callback_data='back')]
            ]
        )
    )

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if chat_id not in users_data or 'photo' not in users_data[chat_id] or 'text' not in users_data[chat_id]:
        await callback_query.answer("Please start by sending an image and text.")
        return

    photo_data = users_data[chat_id]['photo']
    text = users_data[chat_id]['text']
    position = users_data[chat_id].get('position', (10, 10))

    move_step = 10 
    fast_move_step = 40 
    color = users_data[chat_id].get('color', 'black')
    font_path = users_data[chat_id].get('font', "Southam Demo.ttf")
    shadow = users_data[chat_id].get('shadow', False)
    stroke_color = users_data[chat_id].get('stroke_color', 'black')
    stroke_width = 2

    if data.startswith("move_"):
        step = fast_move_step if "fast" in data else move_step
        if data in ["move_up", "move_up_fast"]:
            position = (position[0], max(0, position[1] - step))
        elif data in ["move_down", "move_down_fast"]:
            position = (position[0], position[1] + step)
        elif data in ["move_left", "move_left_fast"]:
            position = (max(0, position[0] - step), position[1])
        elif data in ["move_right", "move_right_fast"]:
            position = (position[0] + step, position[1])
        users_data[chat_id]['position'] = position

    if data.startswith("color_"):
        color = data.split("_")[1]
        users_data[chat_id]['color'] = color

    if data == "choose_font":
        current_font = users_data[chat_id].get('font', "Southam Demo.ttf")
        new_font = "Southam Demo.ttf" if current_font != "Southam Demo.ttf" else "crimes.ttf"
        users_data[chat_id]['font'] = new_font

    if data == "add_shadow":
        shadow = not users_data[chat_id].get('shadow', False)
        users_data[chat_id]['shadow'] = shadow

    if data == "choose_stroke":
        current_stroke = users_data[chat_id].get('stroke_color', "black")
        new_stroke = "black" if current_stroke != "black" else "red"
        users_data[chat_id]['stroke_color'] = new_stroke

    if data == 'choose_language':
        await callback_query.message.reply_text(
            "Choose your language:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("English", callback_data='lang_en'), InlineKeyboardButton("Hindi", callback_data='lang_hi')],
                    [InlineKeyboardButton("Spanish", callback_data='lang_es')],
                    [InlineKeyboardButton("Back", callback_data='back')]
                ]
            )
        )
        await callback_query.answer()
        return

    if data.startswith('lang_'):
        language = data.split('_')[1]
        users_data[chat_id]['language'] = language
        await callback_query.answer(f"Language set to {language}!", show_alert=True)
        await send_edit_menu(client, chat_id)
        return

    if data == 'download_logo':
        await send_edited_image(client, chat_id, photo_data, text, position, color, font_path, shadow, stroke_color, stroke_width, True)
        return

    if data == 'back':
        await send_edit_menu(client, chat_id)
        return

    await send_edited_image(client, chat_id, photo_data, text, position, color, font_path, shadow, stroke_color, stroke_width)

async def send_edited_image(client, chat_id, photo_data, text, position, color, font_path, shadow, stroke_color, stroke_width, final=False):
    image = Image.open(io.BytesIO(photo_data))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, 40)

    if shadow:
        shadow_offset = (2, 2)
        shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
        draw.text(shadow_position, text, fill="grey", font=font)

    draw.text(position, text, fill=color, font=font, stroke_width=stroke_width, stroke_fill=stroke_color)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    caption = "Here is your edited logo!" if not final else "Here is your final logo!"
    await client.send_photo(chat_id, img_byte_arr, caption=caption)

app.run()
