import os
import time
import requests
from bs4 import BeautifulSoup
import discord

from dotenv import load_dotenv
from discord.ext import commands

from verify import fetch_tweet

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

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
async def me(ctx):
    await ctx.send(f'You are {ctx.message.author}')
    user = await bot.fetch_user(ctx.message.author.id)

@bot.command()
async def you(ctx):
    response = "I'm a catgirl, p-pet me. Meow :3"
    await ctx.send(response)

@bot.command()
async def verify(ctx):

    await ctx.author.send("000000")
    await ctx.send(ctx.message.content.split(" ")[-1])
    tweet = await fetch_tweet(ctx.message.content.split(" ")[-1])
    with open("tweet.html", "w") as f:
        f.write(tweet)


# !verify https://twitter.com/2Fast_4Love/status/1567815691293659136


bot.run(TOKEN)
# client.run(TOKEN)



