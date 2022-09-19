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
GUILD_ID = 1004495124451053608
ROLES = {
    "admin": 1004495124451053613,
    "dev": 1004495124451053612,
}

EXP_ROLES = {
    "Akamateur": [11, 19],
    "Akamate": [20, 34],
    "Akacool": [35, 49],
    "Akaicon": [50, 59],
    "Akaidol": [60, 200]
    }

ADMINS = (
    "Dog  犬", "Daxeko",  "thetimedoesfly", "Kikko"
)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
PASSW_LENGTH = 16
WAIT_FOR_COMMENT = 60

INVITES_CAP = 10
UPDATE_ROLES_EVERY = 24 # 24 * 5 mins = 2h
VERIFICATION_CHANNEL = 1017360549425709097
LEADERBOARD_CHANNEL = 1021457318300373113
ALLOWED_CHANNELS = {
    'twitter-verification': VERIFICATION_CHANNEL,
    "leaderboard": LEADERBOARD_CHANNEL,
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
        self.update_roles_count = UPDATE_ROLES_EVERY
        self._on_ready = "[INFO] Bot now online"
        self.add_commands()
        self.db = database
        self.guild_id = GUILD_ID


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
            users = await self.db.fetch('SELECT * FROM users')
            promo = await self.db.fetch('SELECT * FROM promo')
            retweets = await self.db.fetch('SELECT * FROM retweets')

            data = {
                "users": await unpack_records(users),
                "promo": await unpack_records(promo),
                "retweets": await unpack_records(retweets),
            }
            with open(fname, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error during backup {e}")
        logger.info(f"BACKUP COMPLETE")

    @tasks.loop(minutes=5)
    async def leaderboard(self):
        def format_leaderboard(lb):
            sorted_exps = sorted(
                [[name, exp] for name, exp in lb],
                key=lambda x: x[1],
                reverse=True
            )
            lb = []
            line = ""
            for el in sorted_exps:
                if len(line) < 1800:
                    line += f"{el[0]}: {int(el[1])}exp\n"
                else:
                    lb.append(line)
                    line = ""
            return lb

        def get_role(exp):
            for role_name, minmax in EXP_ROLES.items():
                if minmax[0] <= exp <= minmax[1]:
                    return role_name

        guild = self.get_guild(self.guild_id)
        guild_roles = guild.roles
        roles = {role_name: get(guild_roles, name=role_name) for role_name in EXP_ROLES.keys()}
        guild_members = {member.id: member for member in guild.members}
        members_roles = {member.id: {role.name: role for role in member.roles if role.name in EXP_ROLES.keys()}
                         for member in guild.members}
        await self.update_invites(guild)
        await self.add_senior_exp(guild)

        users = {}
        for user in await self.db.fetch('SELECT * FROM users'):
            iexp = e if (e := user.get("iexp")) is not None else 0
            exp = iexp if iexp <= INVITES_CAP else INVITES_CAP
            exp += e if (e := user.get("texp")) is not None else 0
            exp += e if (e := user.get("aexp")) is not None else 0
            users[user.get("uid")] = {
                "uname": user.get("uname"),
                "exp":  exp,
            }

        leaderboard = []
        for uid, data in users.items():
            exp = data["exp"]
            if (uname := data["uname"]) in ADMINS: continue
            if self.update_roles_count == 0:
                self.update_roles_count = UPDATE_ROLES_EVERY
                member = guild_members[uid]
                current_roles = members_roles[uid]
                if not (expected_role_name := get_role(exp)): continue
                expected_role = roles[expected_role_name]

                if len(current_roles.keys()) == 0:
                    await member.add_roles(expected_role)
                elif [expected_role_name] != list(current_roles.keys()):
                    for _, role in current_roles.keys():
                        await member.remove_roles(role)
                    await member.add_roles(expected_role)
            else:
                self.update_roles_count -= 1

            leaderboard.append([uname, exp])



        await self.get_channel(LEADERBOARD_CHANNEL).send("LEADERBOARD UPDATES \n+++\n check your rank")
        for line in format_leaderboard(leaderboard):
            await self.get_channel(LEADERBOARD_CHANNEL).send(line)


    async def update_invites(self, guild):
        for inv in await guild.invites():
            user_data = await self.db.fetch('SELECT * from users WHERE uid = $1', inv.inviter.id)
            if len(user_data) > 0:
                await self.db.write('UPDATE users SET iexp = $1 WHERE uid = $2', inv.uses, inv.inviter.id)
            else:
                await self.db.write('INSERT INTO users(uid, uname, iexp) VALUES($1, $2, $3)',
                                    inv.inviter.id, inv.inviter.name, inv.uses,)

    async def add_senior_exp(self, guild):
        for user in guild.members:
            if "Akasenior" in [r.name for r in user.roles]:
                user_data = await self.db.fetch('SELECT * from users WHERE uid = $1', user.id)
                if len(user_data) > 0:
                    await self.db.write('UPDATE users SET aexp = 35 WHERE uid = $1', user.id)
                else:
                    await self.db.write('INSERT INTO users(uid, uname, aexp) VALUES($1, $2, 35)',
                                        user.id, user.name)

    async def _fetch_promos(self):
        promos = await self.db.fetch('SELECT * FROM promo')
        self.tweet_to_promo_code = {el.get("url"): el.get("code") for el in promos} if promos else {}
        self.used_codes = sorted([
            int(el.split(PROMO_PREFIX)[-1]) for el in self.tweet_to_promo_code.values()
        ]) if self.tweet_to_promo_code else []

    async def on_ready(self):
        await self.db._init()
        await self._fetch_promos()
        self.leaderboard.start()
        self.dump_db.start()
        logger.info("BOT STARTED")

        print(self._on_ready)

    async def _generate_otp(self):
        return secrets.token_urlsafe(PASSW_LENGTH)

    async def _is_admin(self, ctx):
        return ctx.author.name in ADMINS

    async def _promo_claimed(self, author_id, promo_code):
        promo_by_author = await self.db.fetch('SELECT * FROM retweets WHERE UID = $1', author_id)
        if promo_by_author and promo_code in [el.get("code") for el in promo_by_author]:
            return True


    async def update_promo(self, author_id, promo_code):
        await self.db.write('INSERT INTO retweets(uid, code) VALUES($1, $2)', author_id, promo_code)

    async def add_exp(self, author_id, author_uname):
        exp = await self.db.fetch('SELECT * FROM users WHERE uid = $1', author_id)
        if exp:
            await self.db.write('UPDATE users SET texp = texp + 1 WHERE uid = $1', author_id)
        else:
            await self.db.write('INSERT INTO users(uid, uname, texp) VALUES($1, $2, 1)', author_id, author_uname)

    async def _is_promo_allowed(self, promo_code):
        return promo_code in self.tweet_to_promo_code.values()


    async def is_channel_allowed(self, ctx, channels):

        allowed_channels_ids = []
        for channel in channels:
            allowed_channels_ids.append(ALLOWED_CHANNELS[channel])

        if ctx.channel.id in allowed_channels_ids:
            return True

        command = ctx.message.content.split()[0]
        await ctx.author.send(f"The command {command} can only be used in the following channels:\n {format_output()}")
        return False


    async def is_valid_content(self, url):
        if "/twitter.com/akajukus/" in url:
            return True

    def add_commands(self):
        @self.command(name="promo", pass_context=True)
        async def promo(ctx):

            if not await self._is_admin(ctx):
                await ctx.author.send("Admin only command!")
                return

            try:
                url = ctx.message.content.split()[1]
            except Exception as e:
                await ctx.author.send("Wrong message format. The correct format is '!promo tweet_url'")
                logger.error(f"Promo command error {e}")
                return
            if not await self.is_valid_content(url):
                return await ctx.author.send(
                    f"{url} is not a valid tweet"
                )

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



        @self.command(name="verify", pass_context=True)
        async def verify(ctx):
            if not await self.is_channel_allowed(ctx, ["twitter-verification"]):
                return
            try:
                url = ctx.message.content.split()[1]
                promo_code = ctx.message.content.split()[2]
                raw_tweet_id = url.split("/")[-1]
                tweet_id = raw_tweet_id.split("?")[0]
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
            await ctx.author.send(f"Comment your tweet with the following code within the next {WAIT_FOR_COMMENT} seconds. Code:")
            await ctx.author.send(f"{otp}")
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


m = ctx.guild.members 
m.guild_permissions.send_messages
"""


