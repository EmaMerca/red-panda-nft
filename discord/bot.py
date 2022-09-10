import os

import discord
import secrets
from dotenv import load_dotenv
from discord.ext import commands
import asyncio

from verify import verify_tweet


async def add_experience(user):
    pass


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PASSW_LENGTH = 16
WAIT_FOR_COMMENT = 30


class TwitterBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)
        self._on_ready = "[INFO] Bot now online"
        self.add_commands()

    async def on_ready(self):
        print(self._on_ready)

    async def generate_otp(self):
        return secrets.token_urlsafe(PASSW_LENGTH)

    def add_commands(self):
        @self.command(name="verify", pass_context=True)
        async def verify(ctx):
            try:
                url = ctx.message.content.split()[1]
                content_code = ctx.message.content.split()[2]
                tweet_id = url.split("/")[-1]
                tweet_author = url.split("/")[3]
            except IndexError:
                await ctx.author.send("Wrong message format. The correct format is '!verify tweet_url promo_code'")
                return

            # if not is_unique(tweet_author, content_code):
            #     await ctx.author.send(f"You have already claimed your reward for the following code: {content_code}")
            #     return

            otp = await self.generate_otp()
            await ctx.author.send(f"Comment your tweet with the following code within the next 30 seconds.\nCode: {otp}")
            await asyncio.sleep(WAIT_FOR_COMMENT)

            if not await verify_tweet(tweet_id, tweet_author, otp):
                await ctx.author.send(f"Couldn't verify the post. you either "
                                      f"commented with the wrong code or commented the wrong tweet")
                return

            await add_experience(ctx.author)
            await ctx.author.send(f"Tweet has been verified!")

