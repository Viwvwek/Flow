import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Replace with your Shazam API key and Telegram bot token
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
    except Exception as e:
        print(f"Error identifying song: {e}")
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
    except Exception as e:
        print(f"Error fetching lyrics: {e}")
    return "Lyrics not found."

# Handle voice messages
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    voice_file = await update.message.voice.get_file()
    file_path = f"voice_{user.id}.ogg"
    await voice_file.download_to_drive(file_path)
    # Identify the song
    song_info = identify_song(file_path)
    if song_info:
        title = song_info["title"]
        artist = song_info["artist"]
        url = song_info["url"]
        # Fetch lyrics
        lyrics = fetch_lyrics(title, artist)
        # Send the result to the user
        message = f"🎵 **Song Identified** 🎵\n\nTitle: {title}\nArtist: {artist}\n\n🔗 Listen: {url}\n\n📜 Lyrics:\n{lyrics}"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Sorry, I couldn't identify the song.")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Send me a voice message, and I'll identify the song for you.")

# Main function to run the bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    # Start the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()