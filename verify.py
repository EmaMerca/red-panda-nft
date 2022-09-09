from dotenv import load_dotenv
import os
import aiohttp
import json
from dotenv import load_dotenv



load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
HEADER = {"Authorization": f"Bearer {BEARER_TOKEN}"}


async def conversation_by_tweet(tweet_id):
    url = f"https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{tweet_id}"
    async with aiohttp.ClientSession(headers=HEADER) as session:
        async with session.get(url) as response:
            return await json.loads(response.text)["data"]


async def user_id_by_author(author):
    url = f"https://api.twitter.com/2/users/by/username/{author}"
    async with aiohttp.ClientSession(headers=HEADER) as session:
        async with session.get(url) as response:
            return await json.loads(response.text)["data"]["id"]


async def recent_tweets_by_user(user_id):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    async with aiohttp.ClientSession(headers=HEADER) as session:
        async with session.get(url) as response:
            return {
                tweet["id"]: tweet["text"]
                async for tweet in await json.loads(response.text)["data"]
            }


async def conversation_by_tweet(tweet_id):
    url = f"https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{tweet_id}"
    async with aiohttp.ClientSession(headers=HEADER) as session:
        async with session.get(url) as response:
            return {
                tweet["id"]: tweet["text"]
                async for tweet in await json.loads(response.text)["data"]
            }


async def _verify(conversation, recent_tweets, otp):
    for id_, text in conversation.items():
        if text == otp and id_ in recent_tweets.keys():
            return True


async def verify_tweet(tweet_id, tweet_author, otp):
    uid = await user_id_by_author(tweet_author)
    recent_tweets = await recent_tweets_by_user(uid)
    convo = await conversation_by_tweet(tweet_id)
    return await _verify(convo, recent_tweets, otp)

