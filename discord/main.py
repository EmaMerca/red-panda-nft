import logging
import discord
import asyncio
from bot import TwitterBot, TOKEN
from database import Database, create_database






if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    db = Database("akajukus", "diocane96", "discord")
    bot = TwitterBot(command_prefix='!', intents=intents, database=db)
    bot.run(TOKEN)
