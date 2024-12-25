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

    users_data[message.chat.id] = {
        'photo': photo_bytes,
        'position': (10, 10),
        'font_size': 40,
        'color': 'black',
        'stroke_enabled': False,
        'stroke_width': 2,
        'stroke_color': 'black',
        'font_path': "Southam Demo.ttf"
    }
    await message.reply_text("I got the image! Now send me the text you want to add to the image.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_text(client, message):
    chat_id = message.chat.id
    if chat_id in users_data and 'photo' in users_data[chat_id]:
        users_data[chat_id]['text'] = message.text

        await message.reply_text(
            "Please choose a color for the text or adjust the position:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("♥️ Red", callback_data='color_red'), InlineKeyboardButton("💚 Green", callback_data='color_green')],
                    [InlineKeyboardButton("💙 Blue", callback_data='color_blue'), InlineKeyboardButton("🖤 Black", callback_data='color_black')],
                    [InlineKeyboardButton("Stroke Options", callback_data='stroke_options')],
                    [InlineKeyboardButton("Shadow Options", callback_data='shadow_options')],
                    [InlineKeyboardButton("Inner Shadow Options", callback_data='inner_shadow_options')],
                    [
                        InlineKeyboardButton("⬆️", callback_data='move_up'),
                        InlineKeyboardButton("⬅️", callback_data='move_left'),
                        InlineKeyboardButton("➡️", callback_data='move_right'),
                        InlineKeyboardButton("⬇️", callback_data='move_down')
                    ],
                    [
                        InlineKeyboardButton("⬆️ Fast Up", callback_data='fast_up'),
                        InlineKeyboardButton("⬅️ Fast Left", callback_data='fast_left'),
                        InlineKeyboardButton("➡️ Fast Right", callback_data='fast_right'),
                        InlineKeyboardButton("⬇️ Fast Down", callback_data='fast_down')
                    ],
                    [
                        InlineKeyboardButton("Increase Size 2×", callback_data='increase_font_2x'), 
                        InlineKeyboardButton("Decrease Size 2×", callback_data='decrease_font_2x')
                    ],
                    [
                        InlineKeyboardButton("Increase Size 4×", callback_data='increase_font_4x'), 
                        InlineKeyboardButton("Decrease Size 4×", callback_data='decrease_font_4x')
                    ]
                ]
            )
        )
        await send_edited_image(client, chat_id)

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if chat_id in users_data:
        if data.startswith('color_'):
            users_data[chat_id]['color'] = data.split('_')[1]
            await callback_query.answer(f"Text color set to {users_data[chat_id]['color']}!", show_alert=True)
        
        elif data == 'toggle_shadow':
            users_data[chat_id]['shadow_enabled'] = not users_data[chat_id].get('shadow_enabled', False)
            status = "enabled" if users_data[chat_id]['shadow_enabled'] else "disabled"
            await callback_query.answer(f"Shadow {status}!", show_alert=True)

        elif data == 'toggle_inner_shadow':
            users_data[chat_id]['inner_shadow_enabled'] = not users_data[chat_id].get('inner_shadow_enabled', False)
            status = "enabled" if users_data[chat_id]['inner_shadow_enabled'] else "disabled"
            await callback_query.answer(f"Inner Shadow {status}!", show_alert=True)

        elif data.startswith('shadow_color_'):
            users_data[chat_id]['shadow_color'] = data.split('_')[2]
            await callback_query.answer(f"Shadow color set to {users_data[chat_id]['shadow_color']}!", show_alert=True)

        elif data.startswith('shadow_offset_'):
            offset = int(data.split('_')[2])
            users_data[chat_id]['shadow_offset'] = (offset, offset)
            await callback_query.answer(f"Shadow offset set to {offset}!", show_alert=True)

        elif data.startswith('shadow_size_'):
            size = int(data.split('_')[2])
            users_data[chat_id]['shadow_size'] = size
            await callback_query.answer(f"Shadow size set to {size}!", show_alert=True)
    
        elif data == 'stroke_options':
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

        elif data == 'shadow_options':
            await callback_query.message.reply_text(
                "Shadow Options:",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Enable/Disable Shadow", callback_data='toggle_shadow')],
                        [
                            InlineKeyboardButton("Increase Shadow Size", callback_data='increase_shadow_size'),
                            InlineKeyboardButton("Decrease Shadow Size", callback_data='decrease_shadow_size')
                        ],
                        [InlineKeyboardButton("Change Shadow Color", callback_data='shadow_colors')],
                        [
                            InlineKeyboardButton("Increase Shadow Offset", callback_data='increase_shadow_offset'),
                            InlineKeyboardButton("Decrease Shadow Offset", callback_data='decrease_shadow_offset')
                        ]
                    ]
                )
            )
            await callback_query.answer()

        elif data == 'inner_shadow_options':
            await callback_query.message.reply_text(
                "Inner Shadow Options:",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Enable/Disable Inner Shadow", callback_data='toggle_inner_shadow')],
                        [
                            InlineKeyboardButton("Increase Inner Shadow Size", callback_data='increase_inner_shadow_size'),
                            InlineKeyboardButton("Decrease Inner Shadow Size", callback_data='decrease_inner_shadow_size')
                        ],
                        [InlineKeyboardButton("Change Inner Shadow Color", callback_data='inner_shadow_colors')],
                        [
                            InlineKeyboardButton("Increase Inner Shadow Offset", callback_data='increase_inner_shadow_offset'),
                            InlineKeyboardButton("Decrease Inner Shadow Offset", callback_data='decrease_inner_shadow_offset')
                        ]
                    ]
                )
            )
            await callback_query.answer()

        elif data == 'toggle_stroke':
            users_data[chat_id]['stroke_enabled'] = not users_data[chat_id].get('stroke_enabled', False)
            status = "enabled" if users_data[chat_id]['stroke_enabled'] else "disabled"
            await callback_query.answer(f"Stroke {status}!", show_alert=True)

        elif data == 'increase_stroke':
            users_data[chat_id]['stroke_width'] += 1
            await callback_query.answer(f"Stroke size increased to {users_data[chat_id]['stroke_width']}!", show_alert=True)

        elif data == 'decrease_stroke':
            current_size = users_data[chat_id].get('stroke_width', 1)
            if current_size > 1:
                users_data[chat_id]['stroke_width'] -= 1
                await callback_query.answer(f"Stroke size decreased to {users_data[chat_id]['stroke_width']}!", show_alert=True)
            else:
                await callback_query.answer("Stroke size cannot be less than 1!", show_alert=True)

        elif data == 'stroke_colors':
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

        elif data == 'increase_shadow_size':
            users_data[chat_id]['shadow_size'] += 1
            await callback_query.answer(f"Shadow size increased to {users_data[chat_id]['shadow_size']}!", show_alert=True)

        elif data == 'decrease_shadow_size':
            current_size = users_data[chat_id].get('shadow_size', 1)
            if current_size > 1:
                users_data[chat_id]['shadow_size'] -= 1
                await callback_query.answer(f"Shadow size decreased to {users_data[chat_id]['shadow_size']}!", show_alert=True)
            else:
                await callback_query.answer("Shadow size cannot be less than 1!", show_alert=True)
        
        elif data == 'shadow_colors':
            await callback_query.message.reply_text(
                "Select Shadow Color:",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Black", callback_data='shadow_color_black')],
                        [InlineKeyboardButton("Gray", callback_data='shadow_color_gray')],
                        [InlineKeyboardButton("Red", callback_data='shadow_color_red')],
                        [InlineKeyboardButton("Green", callback_data='shadow_color_green')]
                    ]
                )
            )
            await callback_query.answer()

        elif data == 'increase_shadow_offset':
            current_offset = users_data[chat_id].get('shadow_offset', (5, 5))
            new_offset = (current_offset[0] + 1, current_offset[1] + 1)
            users_data[chat_id]['shadow_offset'] = new_offset
            await callback_query.answer(f"Shadow offset increased to {new_offset}!", show_alert=True)

        elif data == 'decrease_shadow_offset':
            current_offset = users_data[chat_id].get('shadow_offset', (5, 5))
            new_offset = (max(0, current_offset[0] - 1), max(0, current_offset[1] - 1))
            users_data[chat_id]['shadow_offset'] = new_offset
            await callback_query.answer(f"Shadow offset decreased to {new_offset}!", show_alert=True)

        elif data == 'increase_inner_shadow_size':
            users_data[chat_id]['inner_shadow_size'] += 1
            await callback_query.answer(f"Inner shadow size increased to {users_data[chat_id]['inner_shadow_size']}!", show_alert=True)

        elif data == 'decrease_inner_shadow_size':
            current_size = users_data[chat_id].get('inner_shadow_size', 1)
            if current_size > 1:
                users_data[chat_id]['inner_shadow_size'] -= 1
                await callback_query.answer(f"Inner shadow size decreased to {users_data[chat_id]['inner_shadow_size']}!", show_alert=True)
            else:
                await callback_query.answer("Inner shadow size cannot be less than 1!", show_alert=True)
        
        elif data == 'inner_shadow_colors':
            await callback_query.message.reply_text(
                "Select Inner Shadow Color:",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Black", callback_data='inner_shadow_color_black')],
                        [InlineKeyboardButton("Gray", callback_data='inner_shadow_color_gray')],
                        [InlineKeyboardButton("Red", callback_data='inner_shadow_color_red')],
                        [InlineKeyboardButton("Green", callback_data='inner_shadow_color_green')]
                    ]
                )
            )
            await callback_query.answer()

        elif data == 'increase_inner_shadow_offset':
            current_offset = users_data[chat_id].get('inner_shadow_offset', (5, 5))
            new_offset = (current_offset[0] + 1, current_offset[1] + 1)
            users_data[chat_id]['inner_shadow_offset'] = new_offset
            await callback_query.answer(f"Inner shadow offset increased to {new_offset}!", show_alert=True)

        elif data == 'decrease_inner_shadow_offset':
            current_offset = users_data[chat_id].get('inner_shadow_offset', (5, 5))
            new_offset = (max(0, current_offset[0] - 1), max(0, current_offset[1] - 1))
            users_data[chat_id]['inner_shadow_offset'] = new_offset
            await callback_query.answer(f"Inner shadow offset decreased to {new_offset}!", show_alert=True)

        position = users_data[chat_id].get('position', (10, 10))
        normal_step = 5
        fast_step = 20

        if data.startswith("move_") or data.startswith("fast_"):
            step = fast_step if data.startswith("fast_") else normal_step
            if data.endswith("up"):
                position = (position[0], max(0, position[1] - step))
            elif data.endswith("down"):
                position = (position[0], position[1] + step)
            elif data.endswith("left"):
                position = (max(0, position[0] - step), position[1])
            elif data.endswith("right"):
                position = (position[0] + step, position[1])
            users_data[chat_id]['position'] = position
            await callback_query.answer("Position updated!")

        if data.startswith('stroke_color_'):
            users_data[chat_id]['stroke_color'] = data.split('_')[2]
            await callback_query.answer(f"Stroke color set to {users_data[chat_id]['stroke_color']}!", show_alert=True)

        if data.startswith('increase_font_'):
            factor = int(data.split('_')[2][:-1])
            current_size = users_data[chat_id].get('font_size', 40)
            users_data[chat_id]['font_size'] = current_size * factor
            await callback_query.answer(f"Font size increased to {users_data[chat_id]['font_size']}!", show_alert=True)

        elif data.startswith('decrease_font_'):
            factor = int(data.split('_')[2][:-1])
            current_size = users_data[chat_id].get('font_size', 40)
            if current_size // factor >= 10:
                users_data[chat_id]['font_size'] = current_size // factor
                await callback_query.answer(f"Font size decreased to {users_data[chat_id]['font_size']}!", show_alert=True)
            else:
                await callback_query.answer("Font size cannot be too small!", show_alert=True)

        await send_edited_image(client, chat_id)

async def send_edited_image(client, chat_id):
    user_data = users_data[chat_id]
    photo_data = user_data['photo']
    text = user_data.get('text', '')
    position = user_data.get('position', (10, 10))
    color = user_data.get('color', 'black')
    font_path = user_data.get('font_path', "Southam Demo.ttf")
    stroke_color = user_data.get('stroke_color', 'black')
    stroke_width = user_data.get('stroke_width', 2)
    stroke_enabled = user_data.get('stroke_enabled', False)
    font_size = user_data.get('font_size', 40)
    shadow_enabled = user_data.get('shadow_enabled', False)
    inner_shadow_enabled = user_data.get('inner_shadow_enabled', False)
    shadow_color = user_data.get('shadow_color', 'gray')
    shadow_offset = user_data.get('shadow_offset', (5, 5))
    shadow_size = user_data.get('shadow_size', 3)

    image = Image.open(io.BytesIO(photo_data))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)

    # Apply shadow
    if shadow_enabled:
        shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
        for x in range(-shadow_size, shadow_size + 1):
            for y in range(-shadow_size, shadow_size + 1):
                draw.text((shadow_position[0] + x, shadow_position[1] + y), text, fill=shadow_color, font=font)

    # Apply inner shadow
    if inner_shadow_enabled:
        for x in range(-shadow_size, shadow_size + 1):
            for y in range(-shadow_size, shadow_size + 1):
                draw.text((position[0] - x, position[1] - y), text, fill=shadow_color, font=font)

    # Apply text with stroke or normal text
    if stroke_enabled:
        draw.text(position, text, fill=color, font=font, stroke_width=stroke_width, stroke_fill=stroke_color)
    else:
        draw.text(position, text, fill=color, font=font)

    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    await client.send_photo(chat_id, img_byte_arr, caption="Here is your edited logo!")

app.run()
