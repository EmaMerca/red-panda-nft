import logging
import discord
import asyncio
from bot import TwitterBot, TOKEN
from database import Database, create_database

logging.basicConfig(filename="log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Running Urban Planning")

logger = logging.getLogger('urbanGUI')




if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    db = Database("akajukus", "diocane96", "discord")
    bot = TwitterBot(command_prefix='!', intents=intents, database=db)
    bot.run(TOKEN)
