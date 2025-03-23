import telebot
from shazamio import Shazam
import asyncio
import os
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
import requests
from bs4 import BeautifulSoup


load_dotenv()

SHAZAM_API_KEY = os.getenv("SHAZAM_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

AUDIO_FILE_PATH = 'audio.ogg'


async def identify_song(file_path):
    shazam = Shazam()
    response = await shazam.recognize_song(file_path)
    song = response['track']['title']
    artist = response['track']['subtitle']
    song_url = response['track'].get('url', 'No URL available')
    return song, artist, song_url

def get_lyrics_azlyrics(song, artist):
    try:
      
        url = f"https://www.azlyrics.com/lyrics/{artist.lower().replace(' ', '')}/{song.lower().replace(' ', '')}.html"
  
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return "Lyrics not found."

    
        soup = BeautifulSoup(response.text, "html.parser")
        lyrics_div = soup.find("div", class_="col-xs-12 col-lg-8 text-center")
        if lyrics_div:
            lyrics = lyrics_div.find_all("div")[5].get_text(separator="\n")
            return lyrics
        else:
            return "Lyrics not found."
    except Exception as e:
        print(f"Error fetching lyrics from AZLyrics: {e}")
        return "Unable to fetch lyrics. Please try again later."

# Start
@bot.message_handler(commands=['start'])
def send_welcome(message):
   
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Identify Song 🎵", "Help ❓", "Features 🌟")

    bot.reply_to(message, "🎶 **Welcome to Flow!** 🎶\n\n"
                          "I'm your personal music assistant. Here's what I can do:\n"
                          "- Identify songs from voice messages.\n"
                          "- Fetch lyrics for your favorite tracks.\n"
                          "- Help you discover more about music.\n\n",
                 reply_markup=keyboard, parse_mode="Markdown")

# Help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "🆘 **Help Menu** 🆘\n\n"
        "Here are the commands you can use:\n"
        "- /start: Start the bot and see the welcome message.\n"
        "- /help: Display this help menu.\n"
        "- /features: See what this bot can do.\n"
        "- Send a voice message: I will identify the song for you.\n\n"
        "Feel free to send me a voice message anytime!"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

# Features
@bot.message_handler(commands=['features'])
def send_features(message):
    features_text = (
        "🌟 **What Flow Can Do** 🌟\n\n"
        "1. **Identify Songs**: Send me a voice message, and I will identify the song for you.\n"
        "2. **Get Song Details**: I will provide the song title, artist, and a link to listen to the song.\n"
        "3. **Get Lyrics**: I can fetch the lyrics of the identified song.\n"
        "4.   After identifying a song, I will provide buttons to:\n"
        "   - Get lyrics.\n"
        "   - Search for the song on YouTube.\n"
        "   - Search for the song on Spotify.\n"
        
        "🎶 **How to Use** 🎶\n"
        "- Send a voice message with a song, and I will do the rest!\n"
        "- Use /help to see all available commands.\n\n"
        "Enjoy using Flow! 🎵"
    )
    bot.reply_to(message, features_text, parse_mode="Markdown")

# Handle voice messages
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    file_id = message.voice.file_id
    file_info = bot.get_file(file_id)

    
    bot.send_message(message.chat.id, "🔍 Processing your voice message... Please wait!")

   
    downloaded_file = bot.download_file(file_info.file_path)
    with open(AUDIO_FILE_PATH, 'wb') as new_file:
        new_file.write(downloaded_file)

    async def process_voice():
        try:
           
            song, artist, song_url = await identify_song(AUDIO_FILE_PATH)
            reply_message = f"🎶 **Song Identified!** 🎶\n\n" \
                           f"**Title:** {song}\n" \
                           f"**Artist:** {artist}\n" \
                           f"**Listen here:** {song_url}\n\n" \
                           f"Would you like to know more about this song?"

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Get Lyrics", callback_data=f"lyrics_{song}_{artist}"))
            keyboard.add(InlineKeyboardButton("Search on YouTube", url=f"https://www.youtube.com/results?search_query={song} {artist}"))
            keyboard.add(InlineKeyboardButton("Search on Spotify", url=f"https://open.spotify.com/search/{song} {artist}"))

            
            bot.send_message(message.chat.id, reply_message, reply_markup=keyboard, parse_mode="Markdown")

        except Exception as e:
            bot.reply_to(message, f"❌ **Error:** Unable to identify the song. Please try again later.\n\nError: {e}")

        finally:
           
            if os.path.exists(AUDIO_FILE_PATH):
                os.remove(AUDIO_FILE_PATH)

   
    asyncio.run(process_voice())


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("lyrics_"):

        _, song, artist = call.data.split("_")
        bot.send_message(call.message.chat.id, f"🔍 Searching for lyrics of **{song}** by **{artist}**...", parse_mode="Markdown")

        #web scraping
        lyrics = get_lyrics_azlyrics(song, artist)
        if "not found" in lyrics.lower() or "unable" in lyrics.lower():
            lyrics = "Sorry, I couldn't find the lyrics for this song. Please try another song."
        bot.send_message(call.message.chat.id, f"🎤 **Lyrics for {song} by {artist}:**\n\n{lyrics}", parse_mode="Markdown")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == "Identify Song 🎵":
        bot.reply_to(message, "🎤 Send me a voice message, and I'll identify the song for you!")
    elif message.text == "Help ❓":
        send_help(message)
    elif message.text == "Features 🌟":
        send_features(message)
    else:
        bot.reply_to(message, "🤔 I didn't understand that. Please use the buttons or type /help for assistance.")


bot.polling()