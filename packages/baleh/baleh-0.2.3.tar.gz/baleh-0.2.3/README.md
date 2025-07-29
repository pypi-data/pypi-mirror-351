# Baleh

An advanced Python library for Bale messenger bots, inspired by the Telegram Bot API.

## Installation

Install the library using pip:

```bash
pip install baleh
Prerequisites
This library requires ffmpeg for converting animated stickers (.tgs to .webm). Install it on your system:

Ubuntu/Debian:
bash


sudo apt-get install ffmpeg
MacOS:
bash


brew install ffmpeg
Windows: Download from ffmpeg.org, extract, and add to your PATH.
The library also uses the following Python packages (automatically installed via pip):

aiohttp>=3.8.0
Pillow>=9.0.0
Features
Send text messages, photos, videos, audio, stickers (static and animated), and documents
Manage chats (get chat info, ban/unban members)
Handle incoming messages with decorators
Asynchronous API with aiohttp
Webhook support
Type hints for better IDE support
Retry mechanism for handling API errors
Support for animated stickers (converts .tgs to .webm)
Usage
Send a Message
python


from baleh import BaleClient
import asyncio

async def main():
    client = BaleClient("your_bot_token")
    await client.connect()
    message = await client.send_message(chat_id=123456789, text="Hello, Bale!")
    print(message.text)
    await client.disconnect()

asyncio.run(main())
Send a Photo
python


async def send_photo():
    client = BaleClient("your_bot_token")
    await client.connect()
    message = await client.send_photo(chat_id=123456789, photo="path/to/photo.jpg", caption="My photo")
    await client.disconnect()

asyncio.run(send_photo())
Send an Animated Sticker
The library automatically converts .tgs files to .webm for animated stickers:

python


async def send_animated_sticker():
    client = BaleClient("your_bot_token")
    await client.connect()
    message = await client.send_animation(chat_id=123456789, animation="path/to/sticker.tgs")
    await client.disconnect()

asyncio.run(send_animated_sticker())
Handle Incoming Messages
python


async def handle_messages():
    client = BaleClient("your_bot_token")
    
    @client.on_message()
    async def on_message(message):
        await client.send_message(message.chat.id, f"Received: {message.text}")
    
    await client.connect()
    await client.start_polling()

asyncio.run(handle_messages())
Contributing
Fork the repository at github.com/hamidrashidi98/baleh and submit pull requests. Feel free to open issues for bugs or feature requests.

Development
To contribute to the development of this library:

Clone the repository:
bash


git clone https://github.com/hamidrashidi98/baleh.git
cd baleh
Install dependencies:
bash


pip install -r requirements.txt
Make your changes and test them.
Submit a pull request.
License
This project is licensed under the MIT License - see the LICENSE file for details.