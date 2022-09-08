
import aiohttp
import asyncio
from dotenv import load_dotenv
import requests

async def fetch_tweet_replies(tweet_id):

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])

            html = await response.text()
            return html


if __name__ == "__main__":
    import tweepy
    import os
    import aiohttp
    import asyncio
    from dotenv import load_dotenv
    import requests


    load_dotenv()
    BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    client = tweepy.Client(BEARER_TOKEN)
    tweet_id = 1567815691293659136


    header = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    import json

    cid = json.loads(requests.get(f"https://api.twitter.com/2/tweets?ids={tweet_id}&tweet.fields=conversation_id", headers=header).text)["data"][0]["conversation_id"]
    replies = json.loads(requests.get(f"https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{cid}", headers=header).text)["data"]
    for reply in replies:
        if reply["text"] == "lallero":
            print("verified")