import os
import secrets
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import json

from verify import verify_tweet


ADMIN_ACCOUNTS = [
    "Daxeko",
    "Dog 犬",
    "Kikko",
    "thetimedoesfly"
]

PROMO_PREFIX = "AKA"

ROLES = {
    "admin": 1004495124451053613,
    "dev": 1004495124451053612,
}
async def add_experience(user):
    pass


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PASSW_LENGTH = 16
WAIT_FOR_COMMENT = 60



class TwitterBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)
        self._on_ready = "[INFO] Bot now online"
        self.add_commands()
        self.exp = self.load_json("exp.json")
        self.promo = self.load_json("promo.json")
        self.used_codes = sorted([int(el.split(PROMO_PREFIX)[-1]) for el in self.promo.values()])


    def load_json(self, fname):
        with open(fname, "r") as f:
            return json.load(f)

    async def save_json(self, fname, data):
        with open(fname, "w") as f:
            json.dump(data, f)

    async def on_ready(self):
        print(self._on_ready)

    async def generate_otp(self):
        return secrets.token_urlsafe(PASSW_LENGTH)

    async def is_admin(self, ctx):
        roles = [role.id for role in ctx.author.roles]
        return ROLES["admin"] in roles

    def add_commands(self):
        @self.command(name="promo", pass_context=True)
        async def promo(ctx):
            if not await self.is_admin(ctx):
                return
            try:
                url = ctx.message.content.split()[1]
            except IndexError:
                await ctx.author.send("Wrong message format. The correct format is '!promo tweet_url'")
                return
            if url in self.promo:
                await ctx.author.send(f"This tweet already has a promo code. Promo code: {self.promo[url]}")
                return

            new_code = int(self.used_codes[-1]) + 1
            self.promo[url] = PROMO_PREFIX + str(new_code)
            await ctx.author.send(f"Promo code: {self.promo[url]}")
            await self.save_json("promo.json", self.promo)

        @self.command(name="all-exp", pass_context=True)
        async def all_exp(ctx):
            if not await self.is_admin(ctx):
                return
            await ctx.author.send(self.exp)

        @self.command(name="exp", pass_context=True)
        async def exp(ctx):
            author = ctx.author.name
            if author in self.exp:
                await ctx.author.send(f"You have {self.exp[author]} exp")
            else:
                await ctx.author.send("You have 0 exp")

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




"""
            invites = []
            for i in await ctx.guild.invites():
                invites.append(i)
"""