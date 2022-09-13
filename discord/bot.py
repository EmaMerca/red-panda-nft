import os
import secrets
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
import hashlib

from verify import verify_tweet

PROMO_PREFIX = "AKA"

ROLES = {
    "admin": 1004495124451053613,
    "dev": 1004495124451053612,
}


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PASSW_LENGTH = 16
WAIT_FOR_COMMENT = 60



class TwitterBot(commands.Bot):
    def __init__(self, command_prefix, intents, database):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)
        self._on_ready = "[INFO] Bot now online"
        self.add_commands()
        self.db = database

    async def _init(self):
        await self._fetch_promos()

    async def _fetch_promos(self):
        promos = await self.db.fetch('SELECT * FROM promo')
        self.tweet_to_promo_code = {el.get("url"): el.get("code") for el in promos}
        self.used_codes = sorted([
            int(el.split(PROMO_PREFIX)[-1]) for el in self.tweet_to_promo_code.values()
        ])

    async def on_ready(self):
        print(self._on_ready)

    async def _generate_otp(self):
        return secrets.token_urlsafe(PASSW_LENGTH)

    async def _is_admin(self, ctx):
        roles = [role.id for role in ctx.author.roles]
        return ROLES["admin"] in roles

    async def _promo_claimed(self, author_id, promo_code):
        promo_by_author = self.db.fetch('SELECT * FROM retweets WHERE UID = $1', author_id)
        if promo_code in [el.get("code") for el in promo_by_author]:
            return True

    async def _is_promo_allowed(self, promo_code):
        return promo_code in self.db.tweet_to_promo_code.values()

    async def hash(self, text):
        return hashlib.sha256(f"{text}".encode()).hexdigest()

    def add_commands(self):
        @self.command(name="promo", pass_context=True)
        async def promo(ctx):
            if not await self._is_admin(ctx):
                return
            try:
                url = ctx.message.content.split()[1]
            except IndexError:
                await ctx.author.send("Wrong message format. The correct format is '!promo tweet_url'")
                return
            if url in self.tweet_to_promo_code:
                await ctx.author.send(
                    f"This tweet already has a promo code. Promo code: {self.tweet_to_promo_code[url]}"
                )
                return

            new_code = int(self.used_codes[-1]) + 1
            self.tweet_to_promo_code[url] = PROMO_PREFIX + str(new_code)
            await self.db.insert('INSERT INTO promo(url, promo) VALUES($1, $2)', url, self.tweet_to_promo_code[url])
            await ctx.author.send(f"Promo code: {self.tweet_to_promo_code[url]}")

        @self.command(name="all-exp", pass_context=True)
        async def all_exp(ctx):
            if not await self._is_admin(ctx):
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
                promo_code = ctx.message.content.split()[2]
                tweet_id = url.split("/")[-1]
                tweet_author = url.split("/")[3]
            except IndexError:
                await ctx.author.send("Wrong message format. The correct format is '!verify tweet_url promo_code'")
                return

            if not await self._is_promo_allowed(promo_code):
                await ctx.author.send(f"The promo code {promo_code} is not valid!")
                return

            if await self._promo_claimed(author_id, promo_code):
                await ctx.author.send(f"You have already claimed your reward for the following code: {promo_code}")
                return

            otp = await self._generate_otp()
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