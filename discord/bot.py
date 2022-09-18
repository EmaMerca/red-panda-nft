import math
import logging
import os
import secrets
from dotenv import load_dotenv
from discord.utils import get
from discord.ext import commands, tasks
import asyncio
import json
from datetime import datetime
from verify import verify_tweet
import math
PROMO_PREFIX = "AKA"

ROLES = {
    "admin": 1004495124451053613,
    "dev": 1004495124451053612,
}

EXP_ROLES = {
    "test-role": [10, 19],
    "test-role1": [20, 34],
#     "role3": [35, 49],
#     "role4": [50, 59],
#     "role5": [60, 200]
}

ADMINS = (
    "Dog  犬", "Daxeko", "Kikko", "thetimedoesfly"
)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PASSW_LENGTH = 16
WAIT_FOR_COMMENT = 60

ALLOWED_CHANNELS = {
    1017360549425709097: 'twitter-verification'
}


logging.basicConfig(filename="log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logging.info("Discord")

logger = logging.getLogger('TwitterVerification')


class TwitterBot(commands.Bot):
    def __init__(self, command_prefix, intents, database):
        commands.Bot.__init__(self, command_prefix=command_prefix, intents=intents)
        self._on_ready = "[INFO] Bot now online"
        self.add_commands()
        self.db = database


    @tasks.loop(hours=24)
    async def dump_db(self):
        logger.info(f"STARTING BACKUP")

        async def unpack_records(records):
            data = []
            for el in records:
                record = []
                for k, v in el.items():
                    record.append((k, v))
                data.append(record)
            return data
        try:
            time = datetime.now()
            fname = f"./dumps/dump_{time.year}{time.month}{time.hour}{time.day}-{time.hour}.json"
            experience = await self.db.fetch('SELECT * FROM experience')
            promo = await self.db.fetch('SELECT * FROM promo')
            retweets = await self.db.fetch('SELECT * FROM retweets')

            data = {
                "experience": await unpack_records(experience),
                "promo": await unpack_records(promo),
                "retweets": await unpack_records(retweets),
            }
            with open(fname, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error during backup {e}")
        logger.info(f"BACKUP COMPLETE")

    async def _fetch_promos(self):
        promos = await self.db.fetch('SELECT * FROM promo')
        self.tweet_to_promo_code = {el.get("url"): el.get("code") for el in promos} if promos else {}
        self.used_codes = sorted([
            int(el.split(PROMO_PREFIX)[-1]) for el in self.tweet_to_promo_code.values()
        ]) if self.tweet_to_promo_code else []

    async def on_ready(self):
        await self.db._init()
        await self._fetch_promos()
        self.dump_db.start()
        logger.info("BOT STARTED")

        print(self._on_ready)

    async def _generate_otp(self):
        return secrets.token_urlsafe(PASSW_LENGTH)

    async def _is_admin(self, ctx):
        roles = [role.id for role in ctx.author.roles]
        return ROLES["admin"] in roles

    async def _promo_claimed(self, author_id, promo_code):
        promo_by_author = await self.db.fetch('SELECT * FROM retweets WHERE UID = $1', author_id)
        if promo_by_author and promo_code in [el.get("code") for el in promo_by_author]:
            return True


    async def update_promo(self, author_id, promo_code):
        await self.db.write('INSERT INTO retweets(uid, code) VALUES($1, $2)', author_id, promo_code)

    async def add_exp(self, author_id, author_uname):
        exp = await self.db.fetch('SELECT * FROM experience WHERE UID = $1', author_id)
        if exp:
            await self.db.write('UPDATE experience SET exp = exp + 1 WHERE uid = $1', author_id)
        else:
            await self.db.write('INSERT INTO experience(uid, uname, exp) VALUES($1, $2, 1)', author_id, author_uname)

    async def _is_promo_allowed(self, promo_code):
        return promo_code in self.tweet_to_promo_code.values()


    async def is_channel_allowed(self, ctx):
        def format_output():
            return '\n'.join(list(ALLOWED_CHANNELS.values()))

        if ctx.channel.id in ALLOWED_CHANNELS:
            return True

        command = ctx.message.content.split()[0]
        await ctx.author.send(f"The command {command} can only be used in the following channels:\n {format_output()}")
        return False


    async def fetch_exp_and_levelup(self, ctx):
        tweet_experience = [[el["uid"], int(el["exp"]), el["uname"]] for el in
                            await self.db.fetch('SELECT * FROM experience')]
        invites_by_user = [[i.inviter.id, i.uses, i.inviter.name] for i in await ctx.guild.invites() if i.uses > 0]

        exp_by_uname = {}
        exp_by_uid = {}
        for uid, exp, uname in tweet_experience + invites_by_user:
            if uname not in exp_by_uname:
                exp_by_uname[uname] = 0
            exp_by_uname[uname] += exp

            if uid not in exp_by_uid:
                exp_by_uid[uid] = 0
            exp_by_uid[uid] += exp

        for user in ctx.guild.members:
            if user.name in ADMINS: continue
            if user and user.id in exp_by_uid:
                for role_name, minmax in EXP_ROLES.items():
                    role = get(ctx.guild.roles, name=role_name)
                    if minmax[0] <= exp_by_uid[user.id] <= minmax[1]:
                        await user.add_roles(role)
                        logger.info(f"add {role.name} for {user.name}")
                    else:
                        for user_role in [r.name for r in user.roles]:
                            if user_role == role.name:
                                await user.remove_roles(role)
                                logger.info(f"remove {role.name} for {user.name}")

        return exp_by_uname, exp_by_uid

    def add_commands(self):
        @self.command(name="promo", pass_context=True)
        async def promo(ctx):

            if not await self.is_channel_allowed(ctx):
                return
            if not await self._is_admin(ctx):
                await ctx.author.send("Admin only command!")
                return

            try:
                url = ctx.message.content.split()[1]
            except Exception as e:
                await ctx.author.send("Wrong message format. The correct format is '!promo tweet_url'")
                logger.error(f"Promo command error {e}")
                return

            if url in self.tweet_to_promo_code:
                await ctx.author.send(
                    f"This tweet already has a promo code. Promo code: {self.tweet_to_promo_code[url]}"
                )
                return

            new_code = int(self.used_codes[-1]) + 1 if len(self.used_codes) > 0 else 0
            self.tweet_to_promo_code[url] = PROMO_PREFIX + str(new_code)
            self.used_codes.append(new_code)
            await self.db.write('INSERT INTO promo(url, code) VALUES($1, $2)', url, self.tweet_to_promo_code[url])
            await ctx.author.send(f"Promo code: {self.tweet_to_promo_code[url]}")
            logger.info(f"{ctx.author.name} generated promo {self.tweet_to_promo_code[url]} for content {url}")



        @self.command(name="leaderboard", pass_context=True)
        async def leaderboard(ctx):
            def format_output(experience):
                sorted_exps = sorted(
                    [[name, exp] for name, exp in experience.items() if name not in ADMINS],
                    key=lambda x: x[1],
                    reverse=True
                )
                return "\n".join([f"{el[0]}: {el[1]}exp" for el in sorted_exps])

            if not await self.is_channel_allowed(ctx):
                return

            exp_by_uname, exp_by_uid = await self.fetch_exp_and_levelup(ctx)
            await ctx.channel.send(format_output(exp_by_uname))


        @self.command(name="verify", pass_context=True)
        async def verify(ctx):

            if not await self.is_channel_allowed(ctx):
                return
            try:
                url = ctx.message.content.split()[1]
                promo_code = ctx.message.content.split()[2]
                tweet_id = url.split("/")[-1]
                tweet_author = url.split("/")[3]
                author_id = ctx.author.id
            except Exception as e:
                logger.error(f"Verification error {e}")
                await ctx.author.send("Wrong message format. The correct format is '!verify tweet_url promo_code'")
                return

            if not await self._is_promo_allowed(promo_code):
                await ctx.author.send(f"The promo code {promo_code} is not valid!")
                return

            if await self._promo_claimed(author_id, promo_code):
                await ctx.author.send(f"You have already claimed your reward for the following code: {promo_code}")
                return

            otp = await self._generate_otp()
            await ctx.author.send(f"Comment your tweet with the following code within the next {WAIT_FOR_COMMENT} seconds.\nCode: {otp}")
            await asyncio.sleep(WAIT_FOR_COMMENT)

            if not await verify_tweet(tweet_id, tweet_author, otp):
                await ctx.author.send(f"Couldn't verify the post. you either "
                                      f"commented with the wrong code or commented the wrong tweet")
                return

            await self.add_exp(author_id, ctx.author.name)

            await self.update_promo(author_id, promo_code)
            await ctx.author.send(f"Tweet has been verified!")
            logger.info(f"{ctx.author.name} verified")




"""
            invites_by_user = {i.inviter.id: i.uses for i in await ctx.guild.invites()}
                invites_by_user = {i.inviter.id: i.uses for i in await ctx.guild.invites() if i.uses > 0}
!promo https://twitter.com/akajukus/status/1568992773235245058?s=46&t=3aa7bb85dOByP9OlN4F-NA
!verify https://twitter.com/2Fast_4Love/status/1569987234874507265 AKA0                
"""


