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
    users_data[message.chat.id] = {'photo': photo}
    await message.reply_text("I got the image! Now send me the text you want to add to the image.")

@app.on_message(filters.text & ~filters.command("start"))
async def handle_text(client, message):
    chat_id = message.chat.id
    if chat_id in users_data and 'photo' in users_data[chat_id]:
        text = message.text
        users_data[chat_id]['text'] = text

        # Send inline keyboard for color selection
        await message.reply_text(
            "Please choose a color for the text:",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Red", callback_data='red'), InlineKeyboardButton("Green", callback_data='green')],
                    [InlineKeyboardButton("Blue", callback_data='blue'), InlineKeyboardButton("Black", callback_data='black')],
                    [InlineKeyboardButton("White", callback_data='white')]
                ]
            )
        )

@app.on_callback_query()
async def handle_callback_query(client, callback_query):
    color = callback_query.data
    chat_id = callback_query.message.chat.id

    if chat_id in users_data and 'photo' in users_data[chat_id] and 'text' in users_data[chat_id]:
        # Retrieve photo and text
        photo_path = users_data[chat_id]['photo']
        text = users_data[chat_id]['text']

        # Open image and draw text
        image = Image.open(photo_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 40)

        # Draw the text on the image
        draw.text((10, 10), text, fill=color, font=font)

        # Save the edited image to a bytes buffer
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)

        # Send the image back
        await client.send_photo(chat_id, img_byte_arr, caption="Here is your logo!")
        await callback_query.answer("Logo created!", show_alert=True)

app.run()
