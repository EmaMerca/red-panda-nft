import os

import discord
import secrets
from dotenv import load_dotenv
from discord.ext import commands
import asyncio

from verify import fetch_conversation, is_unique

def add_experience(user):
    pass


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PASSW_LENGTH = 10
WAIT_FOR_COMMENT = 30

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "who are you?":
        response = "I'm a catgirl, p-pet me. Meow :3"
        await message.channel.send(response)
        await message.channel.send(message.author.mention)

@bot.command()
async def verify(ctx):
    url = ctx.message.content.split()[2]
    content_code = ctx.message.content.split()[1]
    tweet_id = url.split("/")[-1]
    tweet_author = url.split("/")[3]

    if not is_unique(tweet_author, content_code):
        await ctx.author.send(f"You have already claimed your reward for the following code: {content_code}")
        return

    otp = secrets.token_urlsafe(PASSW_LENGTH)
    await ctx.author.send(f"Comment your tweet with the following code within the next 30 seconds")
    await ctx.author.send(f"code: {otp}")
    await asyncio.sleep(WAIT_FOR_COMMENT)

    if not await verify_tweet(tweet_id, tweet_author, otp):
        await ctx.author.send(f"You commented with the wrong code!")
        return

    add_experience(ctx.author)
    await ctx.author.send(f"Tweet has been verified!")

# !verify https://twitter.com/2Fast_4Love/status/1567815691293659136

bot.run(TOKEN)



