import logging
import discord
from bot import TwitterBot, TOKEN
# TODO: ROLES, exp con invit, ok **verifica unique per twitter verification**, exp in base a twiyyer
# twitte +1xp
# invite +1xp

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
    bot = TwitterBot(command_prefix='!', intents=intents)
    bot._init()
    bot.run(TOKEN)
