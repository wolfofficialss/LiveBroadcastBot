import logging
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from decouple import config
from telethon.tl.functions.users import GetFullUserRequest

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

destination_channels_str = config("DESTNATION_CHANNELS")
destination_channels = [int(channel_id.strip()) for channel_id in destination_channels_str.split(',')]

replacement_link = config("MY_LINK", default=None)
replacement_web_link = config("WEB_LINK", default=None)
replacement_username = config("MY_USERNAME", default=None)

logger.info("Starting...")

try:
    api_id = config("APP_ID", cast=int)
    api_hash = config("HASH")
    string_session = config("STRING_SESSION")
    user_client = TelegramClient(StringSession(string_session), api_id, api_hash)
    user_client.start()
    bot_token = config("TOKEN")
    source_channel = config("SOURCE_CHANNELS", cast=int)
    admin_user_id = config("ADMIN_USER_ID", cast=int)
    datgbot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)
except Exception as e:
    logger.error(f"Error initializing the bot: {str(e)}")
    logger.error("Bot is quitting...")
    exit()

@datgbot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user_id = event.sender_id
    if user_id == admin_user_id:
        try:
            ok = await datgbot(GetFullUserRequest(user_id))
            await event.reply(f"**Hi!**\n\n**I am a channel auto-forward bot!! Read /help to know more!\n\n[Contact Owner](https://t.me/WolfOfficials)..", link_preview=False)
        except Exception as e:
            logger.error(f"Error processing /start command: {str(e)}")
    else:
        await event.reply("You are not authorized to use the bot.")

@datgbot.on(events.NewMessage(pattern="/help"))
async def help(event):
    user_id = event.sender_id
    if user_id == admin_user_id:
        try:
            await event.reply("**Help**\n\n**❄About this bot:\n➡This bot will send all new posts from the source channel to one or more channels (without the forwarded tag)!**\n\n**❄How to use me?\n🏮Add the account to the channels.\n🏮Make me an admin in destination channels.\n🏮Now all new messages would be autoposted on the linked channels!!**\n\n**Liked the bot?** [Get Code](https://t.me/WolfOfficials)", link_preview=False)
        except Exception as e:
            logger.error(f"Error processing /help command: {str(e)}")
    else:
        await event.reply("You are not authorized to use the bot.")

async def replace_links_in_message(message):
    if replacement_web_link:
        message = re.sub(r'https?://tcvvip5\.com/#/register\?r_code=44YWW823408', replacement_web_link, message)
    if replacement_link:
        message = re.sub(r'https?://t\.me\S*|t\.me\S*', replacement_link, message)
    if replacement_username:
        message = re.sub(r'@[\w]+', replacement_username, message)
    return message

async def replace_links_in_caption(caption):
    if replacement_web_link:
        caption = re.sub(r'https?://tcvvip5\.com/#/register\?r_code=44YWW823408', replacement_web_link, caption)
    if replacement_link:
        caption = re.sub(r'https?://t\.me\S*|t\.me\S*', replacement_link, caption)
    if replacement_username:
        caption = re.sub(r'@[\w]+', replacement_username, caption)
    return caption


@user_client.on(events.NewMessage(chats=source_channel))
async def forward_message(event):
    user_id = event.sender_id
    if not event.is_private:
        try:
            if event.message.media:
                if getattr(event.message, 'text', None):
                    replaced_message = await replace_links_in_message(event.message.text)
                    event.message.text = replaced_message
                for destination_channel_id in destination_channels:
                    await event.client.send_message(destination_channel_id, event.message)
            else:
                replaced_message = await replace_links_in_message(event.message.text)
                for destination_channel_id in destination_channels:
                    await event.client.send_message(destination_channel_id, replaced_message)
        except Exception as e:
            logger.error(f"Failed to forward the message: {str(e)}")


logger.info("Bot has started.")
datgbot.run_until_disconnected()
