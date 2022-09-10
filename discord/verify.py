from dotenv import load_dotenv
import os
import aiohttp
import json
from dotenv import load_dotenv
import secrets

load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
HEADER = {"Authorization": f"Bearer {BEARER_TOKEN}"}


async def conversation_by_tweet(tweet_id):
    url = f"https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{tweet_id}"
    async with aiohttp.ClientSession(headers=HEADER) as session:
        async with session.get(url) as response:
            data = await response.text()
            return await json.loads(data)["data"]


async def user_id_by_author(author):
    url = f"https://api.twitter.com/2/users/by/username/{author}"
    async with aiohttp.ClientSession(headers=HEADER) as session:
        async with session.get(url) as response:
            data = await response.text()
            return json.loads(data)["data"]["id"]


async def recent_tweets_by_user(user_id):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    async with aiohttp.ClientSession(headers=HEADER) as session:
        async with session.get(url) as response:
            return {
                tweet["id"]: tweet["text"]
                for tweet in json.loads(await response.text())["data"]
            }


async def conversation_by_tweet(tweet_id):
    url = f"https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{tweet_id}"
    async with aiohttp.ClientSession(headers=HEADER) as session:
        async with session.get(url) as response:
            tweets = json.loads(await response.text()).get("data")
            if tweets:
                return {
                    tweet["id"]: tweet["text"]
                    for tweet in tweets
                }


async def _verify(conversation, recent_tweets, otp):
    for id_, text in conversation.items():
        if secrets.compare_digest(text, otp) and id_ in recent_tweets.keys():
            return True


async def verify_tweet(tweet_id, tweet_author, otp):
    uid = await user_id_by_author(tweet_author)
    recent_tweets = await recent_tweets_by_user(uid)
    convo = await conversation_by_tweet(tweet_id)
    if convo:
        return await _verify(convo, recent_tweets, otp)

