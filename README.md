# Flow - Your Personal Music Assistant Bot 🎶

Flow is a Telegram bot that helps you identify songs from voice messages, fetch lyrics, and provide links to listen to your favorite tracks. 

## Features 🌟
- **Identify Songs:** Send a voice message, and Flow will recognize the song for you.
- **Get Song Details:** Retrieve the song title, artist name, and a link to listen to the song.
- **Fetch Lyrics:** Get lyrics for the identified song.
- **Search Online:** Provides quick buttons to search for the song on YouTube and Spotify.

## How to Use 🚀
1. **Start the Bot**: Click [here](https://t.me/Flow_Songbot) to open Flow on Telegram.
2. **Send a Voice Message**: Flow will analyze and identify the song for you.
3. **Get More Info**: After identification, you can request lyrics or search the song online.
4. **Use Commands:**
   - `/start` - Start the bot and see the welcome message.
   - `/help` - Display the help menu.
   - `/features` - View the bot's capabilities.

## Installation & Setup 🛠️
To run this bot locally, follow these steps:

### Prerequisites:
- Python 3.7+
- Telegram Bot Token (from @BotFather)
- Shazam API Key

### Installation:
1. Clone this repository:
   ```sh
   git clone https://github.com/yourrepo/flow-bot.git
   cd flow-bot
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your API keys:
   ```sh
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   SHAZAM_API_KEY=your_shazam_api_key
   ```
4. Run the bot:
   ```sh
   python bot.py
   ```

## Dependencies 📦
The bot requires the following dependencies:
```sh
telebot
shazamio
asyncio
requests
beautifulsoup4
dotenv
```

## Contributing 🤝
Feel free to fork this repository and contribute by submitting pull requests.

## License 📜
This project is licensed under the MIT License.

---
Enjoy using **Flow** and enhance your music experience! 🎵

