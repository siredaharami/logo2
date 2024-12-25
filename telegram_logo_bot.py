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
    # Download the image
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

        # Send inline keyboard for color, text movement, and additional features
        await message.reply_text(
            "Please choose a color for the text or adjust the position:",
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
                    ]
                ]
            )
        )

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id

    if chat_id in users_data and 'photo' in users_data[chat_id] and 'text' in users_data[chat_id]:
        # Retrieve photo, text, and current position
        photo_data = users_data[chat_id]['photo']
        text = users_data[chat_id]['text']
        position = users_data[chat_id].get('position', (10, 10))

        # Define the move step in pixels
        move_step = 10

        # Define some default values
        color = users_data[chat_id].get('color', 'black')
        font_path = users_data[chat_id].get('font', "Southam Demo.ttf")
        shadow = users_data[chat_id].get('shadow', False)
        stroke_color = users_data[chat_id].get('stroke_color', 'black')
        stroke_width = 2  # Example stroke width

        if data.startswith("move_"):
            # Handle text position adjustments
            if data == "move_up":
                position = (position[0], max(0, position[1] - move_step))
            elif data == "move_down":
                position = (position[0], position[1] + move_step)
            elif data == "move_left":
                position = (max(0, position[0] - move_step), position[1])
            elif data == "move_right":
                position = (position[0] + move_step, position[1])

            # Update position
            users_data[chat_id]['position'] = position
            await callback_query.answer("Position updated!")
            return

        if data.startswith("color_"):
            # Update color
            color = data.split("_")[1]
            users_data[chat_id]['color'] = color
            await callback_query.answer(f"Text color set to {color}!")
            return

        if data == "choose_font":
            # Example implementation: This should show UI to pick fonts
            # For now, we'll switch between some example fonts
            current_font = users_data[chat_id].get('font', "Southam Demo.ttf")
            new_font = "Southam Demo.ttf" if current_font != "Southam Demo.ttf" else "crimes.ttf"  # Example logic
            users_data[chat_id]['font'] = new_font
            await callback_query.answer(f"Font set to {new_font}!")
            return

        if data == "add_shadow":
            # Toggle shadow
            shadow = not users_data[chat_id].get('shadow', False)
            users_data[chat_id]['shadow'] = shadow
            await callback_query.answer(f"Shadow {'enabled' if shadow else 'disabled'}!")
            return

        if data == "choose_stroke":
            # Example implementation: This should show UI to pick stroke colors
            # For now, we'll cycle through some example stroke colors
            current_stroke = users_data[chat_id].get('stroke_color', "black")
            new_stroke = "black" if current_stroke != "black" else "red"  # Example logic
            users_data[chat_id]['stroke_color'] = new_stroke
            await callback_query.answer(f"Stroke color set to {new_stroke}!")
            return

        # Open image and draw text
        image = Image.open(io.BytesIO(photo_data))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, 40)

        # Draw the shadow first if enabled
        if shadow:
            shadow_offset = (2, 2)
            shadow_position = (position[0] + shadow_offset[0], position[1] + shadow_offset[1])
            draw.text(shadow_position, text, fill="grey", font=font)

        # Draw the text with stroke
        draw.text(position, text, fill=color, font=font, stroke_width=stroke_width, stroke_fill=stroke_color)

        # Save the edited image to a bytes buffer
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Send the image back
        await client.send_photo(chat_id, img_byte_arr, caption="Here is your logo!")
        await callback_query.answer("Logo created!", show_alert=True)

app.run()
