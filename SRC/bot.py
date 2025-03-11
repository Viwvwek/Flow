import os
import requests
import logging
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

SHAZAM_API_KEY = os.getenv("SHAZAM_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Function to identify songs using Shazam API
def identify_song(audio_file):
    url = "https://shazam.p.rapidapi.com/songs/v2/detect"
    headers = {
        "X-RapidAPI-Key": SHAZAM_API_KEY,
        "X-RapidAPI-Host": "shazam.p.rapidapi.com"
    }
    try:
        with open(audio_file, "rb") as file:
            files = {"file": file}
            response = requests.post(url, headers=headers, files=files)
            if response.status_code == 200:
                data = response.json()
                track = data.get("track", {})
                return {
                    "title": track.get("title", "Unknown"),
                    "artist": track.get("subtitle", "Unknown"),
                    "url": track.get("url", "#")
                }
            else:
                logger.error(f"Shazam API request failed with status code {response.status_code}")
    except Exception as e:
        logger.error(f"Error identifying song: {e}")
    return None

# Function to fetch lyrics from azlyrics.com
def fetch_lyrics(song_title, artist_name):
    query = f"{song_title} {artist_name}".replace(" ", "+")
    url = f"https://search.azlyrics.com/search.php?q={query}"
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        # Find the first result link
        result = soup.find("td", class_="text-left visitedlyr")
        if result and result.a:
            lyrics_url = result.a["href"]
            lyrics_page = requests.get(lyrics_url)
            lyrics_soup = BeautifulSoup(lyrics_page.text, "html.parser")
            lyrics_div = lyrics_soup.find("div", class_="col-xs-12 col-lg-8 text-center")
            if lyrics_div:
                return lyrics_div.get_text(separator="\n")
            else:
                logger.warning("Lyrics div not found on the lyrics page.")
        else:
            logger.warning("No results found on azlyrics search page.")
    except Exception as e:
        logger.error(f"Error fetching lyrics: {e}")
    return "Lyrics not found."

# Handle voice messages
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info(f"Received voice message from user {user.id}")
    voice_file = await update.message.voice.get_file()
    file_path = f"voice_{user.id}.ogg"
    await voice_file.download_to_drive(file_path)
    logger.info(f"Voice message downloaded to {file_path}")
    # Identify the song
    song_info = identify_song(file_path)
    if song_info:
        title = song_info["title"]
        artist = song_info["artist"]
        url = song_info["url"]
        logger.info(f"Song identified: {title} by {artist}")
        # Fetch lyrics
        lyrics = fetch_lyrics(title, artist)
        # Send the result to the user
        message = (
            f"🎵 **Song Identified** 🎵\n\n"
            f"**Title:** {title}\n"
            f"**Artist:** {artist}\n\n"
            f"🔗 [Listen on Shazam]({url})\n\n"
            f"📜 **Lyrics:**\n{lyrics}"
        )
        await update.message.reply_text(message, parse_mode="Markdown")
    else:
        logger.warning("Song could not be identified.")
        await update.message.reply_text("Sorry, I couldn't identify the song.")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /start command")
    await update.message.reply_text(
        "🎶 **Welcome to the Song Identifier Bot!** 🎶\n\n"
        "Send me a voice message, and I'll identify the song for you.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Get help\n"
        "/about - Learn more about the bot"
    )

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /help command")
    await update.message.reply_text(
        "🆘 **Help** 🆘\n\n"
        "To identify a song, simply send me a voice message containing the song.\n\n"
        "I'll analyze the audio and provide you with the song's title, artist, and lyrics (if available)."
    )

# About command
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /about command")
    await update.message.reply_text(
        "🤖 **About This Bot** 🤖\n\n"
        "This bot uses the Shazam API to identify songs from voice messages.\n\n"
        "It also fetches lyrics from azlyrics.com.\n\n"
        "Developed with ❤️ using Python and python-telegram-bot."
    )

# Main function to run the bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    # Start the bot
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()