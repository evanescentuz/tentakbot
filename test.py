from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import requests

# Constants
BOT_TOKEN = '7438054039:AAENzT11GywtdmRs4hB_GKv9vkAa2fR9CQ8'
IMGBB_API_KEY = '9b4ea7191130c0e88a6b43c3f45dde6c'

# States
PHOTO, CHARACTER_NAME, ANIME_NAME, RARITY, EVENT = range(5)

# Function to upload file to ImgBB
def upload_to_imgbb(file_path):
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                data={'key': IMGBB_API_KEY},
                files={'image': f}
            )
        response_data = response.json()
        if response_data['success']:
            return response_data['data']['url']
        return None
    except Exception as e:
        print(f"Error uploading to ImgBB: {str(e)}")
        return None

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please send a photo.")
    return PHOTO

# Handle photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        file_path = await file.download_as_bytearray()

        # Save the downloaded file temporarily
        with open("temp_image.jpg", "wb") as f:
            f.write(file_path)

        context.user_data['image_path'] = "temp_image.jpg"
        await update.message.reply_text("Please enter the character's name.")
        return CHARACTER_NAME
    else:
        await update.message.reply_text("Send only photo.")
        return PHOTO

# Handle character name
# Handle character name
async def handle_character_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if name:
        # Convert to title case and replace spaces with hyphens
        formatted_name = name.title().replace(" ", "-")
        context.user_data['character_name'] = formatted_name
        await update.message.reply_text("Please enter the anime name.")
        return ANIME_NAME
    else:
        await update.message.reply_text("Send name, not other things.")
        return CHARACTER_NAME

# Handle anime name
async def handle_anime_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    anime_name = update.message.text.strip()
    if anime_name:
        # Convert to title case and replace spaces with hyphens
        formatted_anime_name = anime_name.title().replace(" ", "-")
        context.user_data['anime_name'] = formatted_anime_name
        await update.message.reply_text(
            "Choose rarity:\n1 (⚪️ Common)\n2 (🟣 Rare)\n3 (🟢 Medium)\n4 (🟡 Legendary)\n5 (🔮 Limited)\n6 (💮 Special)\n7 (🎐 Celestial)"
        )
        return RARITY
    else:
        await update.message.reply_text("Send name, not other things.")
        return ANIME_NAME

# Handle rarity
async def handle_rarity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    rarity = update.message.text.strip()
    if rarity.isdigit() and 1 <= int(rarity) <= 7:
        context.user_data['rarity'] = rarity
        await update.message.reply_text(
            "Choose event:\n1: 𝑺𝒖𝒎𝒎𝒆𝒓 🏖\n2: 𝑲𝒊𝒎𝒐𝒏𝒐 👘\n3: 𝑾𝒊𝒏𝒕𝒆𝒓 ❄️\n4: 𝑽𝒂𝒍𝒆𝒏𝒕𝒊𝒏𝒆 💞\n5: 𝑺𝒄𝒉𝒐𝒐𝒍 🎒\n6: 𝑯𝒂𝒍𝒍𝒐𝒘𝒆𝒆𝒏 🎃\n7: 𝑮𝒂𝒎𝒆 🎮\n8: 𝑴𝒂𝒓𝒊𝒏𝒆 🪼\n9: 𝑩𝒂𝒔𝒌𝒆𝒕𝒃𝒂𝒍𝒍 🏀\n10: 𝑴𝒂𝒊𝒅 🧹\n11: 𝑹𝒂𝒊𝒏 ☔\n12: 𝑩𝒖𝒏𝒏𝒚 🐰\n13: 𝑩𝒍𝒐𝒔𝒔𝒐𝒎 🌸\n14: 𝑹𝒐𝒄𝒌 🎸\n15: 𝑪𝒉𝒓𝒊𝒔𝒕𝒎𝒂𝒔 🎄\n16: 𝑵𝒆𝒓𝒅 🤓\n17: 𝑾𝒆𝒅𝒅𝒊𝒏𝒈 💍\n18: 𝑪𝒉𝒆𝒆𝒓𝒍𝒆𝒂𝒅𝒆𝒓𝒔 🎊\n19: 𝑨𝒓𝒕𝒊𝒔𝒕 🎨\n20: 𝑵𝒖𝒓𝒔𝒆 🏨\n21: None"
        )
        return EVENT
    else:
        await update.message.reply_text("Please send a number, not other things.")
        return RARITY

# Handle event
async def handle_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    event = update.message.text.strip()
    if event.isdigit() and 1 <= int(event) <= 21:
        context.user_data['event'] = event
        imgbb_url = upload_to_imgbb(context.user_data['image_path'])
        if imgbb_url:
            character_name = context.user_data['character_name']
            anime_name = context.user_data['anime_name']
            rarity = context.user_data['rarity']
            event = context.user_data['event']
            
            # Prepare the message with MarkdownV2 formatting
            message = (
                f"Here's your order: `/upload {imgbb_url} "
                f"{character_name} {anime_name} {rarity} {event}`"
            )
            
            await update.message.reply_text(
                message,
                parse_mode='MarkdownV2'
            )
        else:
            await update.message.reply_text("Failed to upload image to ImgBB.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please send a number, not other things.")
        return EVENT

def main():
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler with the states PHOTO, CHARACTER_NAME, ANIME_NAME, RARITY, EVENT
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
            CHARACTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_character_name)],
            ANIME_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_anime_name)],
            RARITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rarity)],
            EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event)],
        },
        fallbacks=[],
    )

    # Add the handler to the application
    application.add_handler(conv_handler)

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
