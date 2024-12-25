from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image, ImageDraw, ImageFont
import io

# Replace with your own values
api_id = 25742938
api_hash = "b35b715fe8dc0a58e8048988286fc5b6"
bot_token = "7796646089:AAG3yoXJRSI-D2A5w1kPraju_qpL_Xt3JO8"

app = Client("logo_maker_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

users_data = {}

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Welcome to the Logo Maker Bot!\nPlease send me an image.")

@app.on_message(filters.photo)
async def handle_photo(client, message):
    photo = await message.download()
    with open(photo, "rb") as file:
        photo_bytes = file.read()

    users_data[message.chat.id] = {'photo': photo_bytes, 'position': (10, 10), 'font_size': 40}  # Set default font size
    await message.reply_text("I got the image! Now send me the text you want to add to the image.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_text(client, message):
    chat_id = message.chat.id
    if chat_id in users_data and 'photo' in users_data[chat_id]:
        text = message.text
        users_data[chat_id]['text'] = text

        await message.reply_text(
            "Please choose a color for the text or adjust the position:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("♥️ Red", callback_data='color_red'), InlineKeyboardButton("💚 Green", callback_data='color_green')],
                    [InlineKeyboardButton("💙 Blue", callback_data='color_blue'), InlineKeyboardButton("🖤 Black", callback_data='color_black')],
                    [InlineKeyboardButton("Increase Text Size", callback_data='increase_font_size')],
                    [InlineKeyboardButton("Decrease Text Size", callback_data='decrease_font_size')],
                    [InlineKeyboardButton("Choose Font", callback_data='choose_font')],
                    [InlineKeyboardButton("Add Shadow", callback_data='add_shadow')],
                    [InlineKeyboardButton("Choose Stroke Color", callback_data='choose_stroke')],
                    [
                        InlineKeyboardButton("⬆️", callback_data='move_up'),
                        InlineKeyboardButton("⬅️", callback_data='move_left'),
                        InlineKeyboardButton("➡️", callback_data='move_right'),
                        InlineKeyboardButton("⬇️", callback_data='move_down')
                    ],
                    [InlineKeyboardButton("Choose Language", callback_data='choose_language')]
                ]
            )
        )

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if data == 'choose_language':
        await callback_query.message.reply_text(
            "Choose your language:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("English", callback_data='lang_en'), InlineKeyboardButton("Hindi", callback_data='lang_hi')],
                    [InlineKeyboardButton("Spanish", callback_data='lang_es')]
                ]
            )
        )
        await callback_query.answer()
        return

    if data.startswith('lang_'):
        language = data.split('_')[1]
        users_data[chat_id]['language'] = language
        await callback_query.answer(f"Language set to {language}!", show_alert=True)
        return

    if chat_id in users_data and 'photo' in users_data[chat_id] and 'text' in users_data[chat_id]:
        photo_data = users_data[chat_id]['photo']
        text = users_data[chat_id]['text']
        position = users_data[chat_id].get('position', (10, 10))

        move_step = 10

        color = users_data[chat_id].get('color', 'black')
        font_path = users_data[chat_id].get('font', "Southam Demo.ttf")
        shadow = users_data[chat_id].get('shadow', False)
        stroke_color = users_data[chat_id].get('stroke_color', 'black')
        stroke_width = 2

        font_size = users_data[chat_id].get('font_size', 40)

        if data == "increase_font_size":
            font_size += 5
            users_data[chat_id]['font_size'] = font_size
            await callback_query.answer(f"Font size increased to {font_size}!")

        if data == "decrease_font_size":
            font_size = max(5, font_size - 5)  # Prevent size below 5
            users_data[chat_id]['font_size'] = font_size
            await callback_query.answer(f"Font size decreased to {font_size}!")

        if data.startswith("move_"):
            if data == "move_up":
                position = (position[0], max(0, position[1] - move_step))
            elif data == "move_down":
                position = (position[0], position[1] + move_step)
            elif data == "move_left":
                position = (max(0, position[0] - move_step), position[1])
            elif data == "move_right":
                position = (position[0] + move_step, position[1])
            users_data[chat_id]['position'] = position
            await callback_query.answer("Position updated!")

        if data.startswith("color_"):
            color = data.split("_")[1]
            users_data[chat_id]['color'] = color
            await callback_query.answer(f"Text color set to {color}!")

        if data == "choose_font":
            current_font = users_data[chat_id].get('font', "Southam Demo.ttf")
            new_font = "Southam Demo.ttf" if current_font != "Southam Demo.ttf" else "crimes.ttf"
            users_data[chat_id]['font'] = new_font
            await callback_query.answer(f"Font set to {new_font}!")

        if data == "add_shadow":
            shadow = not users_data[chat_id].get('shadow', False)
            users_data[chat_id]['shadow'] = shadow
            await callback_query.answer(f"Shadow {'enabled' if shadow else 'disabled'}!")

        if data == "choose_stroke":
            current_stroke = users_data[chat_id].get('stroke_color', "black")
            new_stroke = "black" if current_stroke != "black" else "red"
            users_data[chat_id]['stroke_color'] = new_stroke
            await callback_query.answer(f"Stroke color set to {new_stroke}!")

        image = Image.open(io.BytesIO(photo_data))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, font_size)

        if shadow:
            shadow_offset = (2, 2)
            shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
            draw.text(shadow_position, text, fill="grey", font=font)

        draw.text(position, text, fill=color, font=font, stroke_width=stroke_width, stroke_fill=stroke_color)

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        await client.send_photo(chat_id, img_byte_arr, caption="Here is your edited logo!")
        await callback_query.answer("Edit applied!")

app.run()
