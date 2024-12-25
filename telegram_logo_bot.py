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

    users_data[message.chat.id] = {'photo': photo_bytes, 'position': (10, 10)}
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
                    [InlineKeyboardButton("Choose Font", callback_data='choose_font')],
                    [InlineKeyboardButton("Add Shadow", callback_data='add_shadow')],
                    [InlineKeyboardButton("Stroke Options", callback_data='stroke_options')],
                    [
                        InlineKeyboardButton("⬆️", callback_data='move_up'),
                        InlineKeyboardButton("⬅️", callback_data='move_left'),
                        InlineKeyboardButton("➡️", callback_data='move_right'),
                        InlineKeyboardButton("⬇️", callback_data='move_down'),
                        InlineKeyboardButton("⬅⯈", callback_data='move_left_fast'),
                        InlineKeyboardButton("⬆︎︎⬇︎︎", callback_data='move_up_fast'),
                        InlineKeyboardButton("➡⯇", callback_data='move_right_fast'),
                        InlineKeyboardButton("⬇︎⬆︎", callback_data='move_down_fast'),
                        InlineKeyboardButton("Back", callback_data='move_back')
                    ],
                    [InlineKeyboardButton("Choose Language", callback_data='choose_language')],
                    [InlineKeyboardButton("Download", callback_data='download')]
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

    if chat_id in users_data:
        if data == 'stroke_options':
            await callback_query.message.reply_text(
                "Stroke Options:",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Enable/Disable Stroke", callback_data='toggle_stroke')],
                        [
                            InlineKeyboardButton("Increase Size", callback_data='increase_stroke'),
                            InlineKeyboardButton("Decrease Size", callback_data='decrease_stroke')
                        ],
                        [InlineKeyboardButton("Change Stroke Color", callback_data='stroke_colors')]
                    ]
                )
            )
            await callback_query.answer()
            return

        if data == 'toggle_stroke':
            users_data[chat_id]['stroke_enabled'] = not users_data[chat_id].get('stroke_enabled', False)
            status = "enabled" if users_data[chat_id]['stroke_enabled'] else "disabled"
            await callback_query.answer(f"Stroke {status}!", show_alert=True)
            return

        if data == 'increase_stroke':
            users_data[chat_id]['stroke_width'] = users_data[chat_id].get('stroke_width', 2) + 1
            await callback_query.answer(f"Stroke size increased to {users_data[chat_id]['stroke_width']}!", show_alert=True)
            return

        if data == 'decrease_stroke':
            current_size = users_data[chat_id].get('stroke_width', 1)
            if current_size > 1:
                users_data[chat_id]['stroke_width'] = current_size - 1
                await callback_query.answer(f"Stroke size decreased to {users_data[chat_id]['stroke_width']}!", show_alert=True)
            else:
                await callback_query.answer("Stroke size cannot be less than 1!", show_alert=True)
            return

        if data == 'stroke_colors':
            await callback_query.message.reply_text(
                "Select Stroke Color:",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Black", callback_data='stroke_color_black')],
                        [InlineKeyboardButton("Red", callback_data='stroke_color_red')],
                        [InlineKeyboardButton("Green", callback_data='stroke_color_green')]
                    ]
                )
            )
            await callback_query.answer()
            return

        if data.startswith('stroke_color_'):
            users_data[chat_id]['stroke_color'] = data.split('_')[2]
            await callback_query.answer(f"Stroke color set to {users_data[chat_id]['stroke_color']}!", show_alert=True)
            return

    # Movement functionality
    step_size = 10
    fast_step_size = 40
    if data == 'move_up':
        users_data[chat_id]['position'] = (users_data[chat_id]['position'][0], users_data[chat_id]['position'][1] - step_size)
    elif data == 'move_down':
        users_data[chat_id]['position'] = (users_data[chat_id]['position'][0], users_data[chat_id]['position'][1] + step_size)
    elif data == 'move_left':
        users_data[chat_id]['position'] = (users_data[chat_id]['position'][0] - step_size, users_data[chat_id]['position'][1])
    elif data == 'move_right':
        users_data[chat_id]['position'] = (users_data[chat_id]['position'][0] + step_size, users_data[chat_id]['position'][1])
    elif data == 'move_up_fast':
        users_data[chat_id]['position'] = (users_data[chat_id]['position'][0], users_data[chat_id]['position'][1] - fast_step_size)
    elif data == 'move_down_fast':
        users_data[chat_id]['position'] = (users_data[chat_id]['position'][0], users_data[chat_id]['position'][1] + fast_step_size)
    elif data == 'move_left_fast':
        users_data[chat_id]['position'] = (users_data[chat_id]['position'][0] - fast_step_size, users_data[chat_id]['position'][1])
    elif data == 'move_right_fast':
        users_data[chat_id]['position'] = (users_data[chat_id]['position'][0] + fast_step_size, users_data[chat_id]['position'][1])
    elif data == 'move_back':
        users_data[chat_id].setdefault('history', []).append(users_data[chat_id]['position'])
        if len(users_data[chat_id]['history']) > 1:
            users_data[chat_id]['position'] = users_data[chat_id]['history'][-2]
            users_data[chat_id]['history'].pop(-1)

    # Download functionality
    if data == 'download':
        await process_and_send_image(chat_id, "Here is your downloaded logo!", client)
        return

# Function to process and send image
async def process_and_send_image(chat_id, caption, client):
    if 'photo' in users_data[chat_id] and 'text' in users_data[chat_id]:
        photo_data = users_data[chat_id]['photo']
        text = users_data[chat_id]['text']
        position = users_data[chat_id].get('position', (10, 10))
        color = users_data[chat_id].get('color', 'black')
        font_path = users_data[chat_id].get('font', "Southam Demo.ttf")
        shadow = users_data[chat_id].get('shadow', False)
        stroke_color = users_data[chat_id].get('stroke_color', 'black')
        stroke_width = users_data[chat_id].get('stroke_width', 2)
        stroke_enabled = users_data[chat_id].get('stroke_enabled', False)

        image = Image.open(io.BytesIO(photo_data))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, 40)

        if shadow:
            shadow_offset = (2, 2)
            shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
            draw.text(shadow_position, text, fill="grey", font=font)

        if stroke_enabled:
            draw.text(position, text, fill=color, font=font, stroke_width=stroke_width, stroke_fill=stroke_color)
        else:
            draw.text(position, text, fill=color, font=font)

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        await client.send_photo(chat_id, img_byte_arr, caption=caption)

app.run()
