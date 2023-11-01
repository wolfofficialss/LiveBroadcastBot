import logging
from telethon import TelegramClient, events, Button
from decouple import config
from telethon.tl.functions.users import GetFullUserRequest

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.INFO)

destination_channels = [
    config("dest1", cast=int),
    config("dest2", cast=int),
    config("dest3", cast=int),
    config("dest4", cast=int),
    # Add more channel IDs as needed
]

print("Starting...")
try:
    apiid = config("APP_ID", cast=int)
    apihash = config("HASH")
    bottoken = config("TOKEN")
    frm = config("source", cast=int)
    datgbot = TelegramClient('bot', apiid, apihash).start(bot_token=bottoken)
except:
    print("Environment vars are missing! Kindly recheck.")
    print("Bot is quitting...")
    exit()

@datgbot.on(events.NewMessage(pattern="/start"))
async def start(event):
    ok = await datgbot(GetFullUserRequest(event.sender_id))
    await event.reply(f"**Hi ``!**\n\n**I am a channel auto-forward bot!! Read /help to know more!\n\nI can be used in only two channels at a time.**\n\n[Contact Owner](https://t.me/WolfOfficials)..", link_preview=False)

@datgbot.on(events.NewMessage(pattern="/help"))
async def helpp(event):
    await event.reply("**Help**\n\n**❄About this bot:\n➡This bot will send all new posts from destination channel to the one or more channels. (without forwarded tag)!**\n\n**❄How to use me?\n🏮Add me to the channels.\n🏮Make me an admin in all the channels.\n🏮Now all new messages would be autoposted on the linked channels!!**\n\n**Liked the bot?** [Purchase Code](https://t.me/WolfOfficials)", link_preview=False)

@datgbot.on(events.NewMessage(incoming=True, chats=frm))
async def forward_message(event):
    if not event.is_private:
        for destination_channel_id in destination_channels:
            try:
                await event.client.send_message(destination_channel_id, event.message)
            except Exception as e:
                print(f"Failed to forward message to destination channel {destination_channel_id}: {str(e)}")

print("Bot has started.")
datgbot.run_until_disconnected()
