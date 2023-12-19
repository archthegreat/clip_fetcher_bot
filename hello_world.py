# Standard library modules
import asyncio
import subprocess
import os
import time

# Third-party modules
from telegram import Update
from telegram.ext import (ApplicationBuilder, 
                          ContextTypes, 
                          CommandHandler, 
                          MessageHandler,
                          filters
                        )
from telegram.constants import ParseMode

with open('api_key.txt') as api_key:
    api_key = api_key.read()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.from_user.first_name

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Hello, {first_name}! This bot can download videos from all'
        ' popular sites like YouTube, Instagram, Reddit, Twitch etc. To learn'
        ' how to use the bot, type /help.',
        reply_to_message_id=update.message.message_id
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('help.txt') as help_text:
        help_text = help_text.read()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=help_text,
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.message_id,
    )



async def url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.args[0]

    output = subprocess.getstatusoutput(
        f'yt-dlp --no-warnings -f best/bestvideo+bestaudio --get-url {url}')
    if output[0] != 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Invalid URL. No media source found at target.'
            ' Please try again.',
            reply_to_message_id=update.message.message_id,
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Click <a href="{output[1]}">here</a>' 
            ' to download the video.',
            parse_mode=ParseMode.HTML,
            reply_to_message_id=update.message.message_id,)


async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    url = context.args[0]
    chat_id = update.effective_chat.id
    timestamp = int(time.time())
    file_path = f'test/video_{chat_id}_{timestamp}.mp4'

    temp_message = await context.bot.send_message(
            chat_id=chat_id,
            text='Downloading video and sending. Please wait.',
            reply_to_message_id=update.message.message_id)
    try:    
        subprocess.run(
            ['yt-dlp', '--format', 'bestvideo+bestaudio/best', 
            '--merge-output-format', 'mp4', '--concurrent-fragments', '4', 
            '--no-playlist', f'{url}', '-o',f'{file_path}'],
            check = True
            )
    except subprocess.CalledProcessError:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message.message_id,
            text='Invalid URL. No media source found at target.'
            ' Please try again.'
        )
    # subprocess.call(['ffmpeg', '-i', file_path, '-vf', 'scale=1:360', 
    #                compressed_file_path])
    
    with open(file_path, 'rb+') as video:
        await context.bot.send_video(
            chat_id=update.effective_chat.id,
            video=video,
            reply_to_message_id=update.message.message_id,
            write_timeout=300,
        )
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=temp_message.message_id,
    )

    if os.path.isfile(file_path):
        os.remove(file_path)


async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = context.args[0]
    chat_id = update.effective_chat.id
    timestamp = int(time.time())
    file_path = f'test/audio_{chat_id}_{timestamp}.mp3'

    temp_message = await context.bot.send_message(
        chat_id=chat_id,
        text='Downloading the audio, please wait.',
        reply_to_message_id=update.message.message_id
    )

    try:
        subprocess.run(
            ['yt-dlp', '-x', '--audio-format', 'mp3',
             '-o', file_path, url],
             check=True
        )
    except subprocess.CalledProcessError:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=temp_message.message_id,
            text='Invalid URL. No media source found at target.'
            ' Please try again.'
        )
    with open(file_path, 'rb+') as audio:
        await context.bot.send_audio(
            chat_id=update.effective_chat.id,
            audio=audio,
            reply_to_message_id=update.message.message_id,
            write_timeout=1000,
        )
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=temp_message.message_id,
    )

    if os.path.isfile(file_path):
        os.remove(file_path
    

)
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I didn't understand that! 😕 It seems like you've"
        " sent an invalid command."
        " See /help if you'd like to have a look at the available commands.",
        reply_to_message_id=update.message.message_id,
    )


if __name__ == '__main__':
    application = ApplicationBuilder().token(api_key).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('url', url))
    application.add_handler(CommandHandler('download', download))
    application.add_handler(CommandHandler('dl', download))
    application.add_handler(CommandHandler('audio', audio))
    application.add_handler(CommandHandler('help', help_command))
    
    # handler for unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    
    application.run_polling()

