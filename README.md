# red-panda-nft

## discord bots
The aws instance is 
- instance id: `i-0f1cb0a66445ae3a0`
- public ipv4 dns `ec2-3-92-225-108.compute-1.amazonaws.com`
- instance user name: `ec2-user`


connect with 
```bash
ssh -i ~/ema-linux.pem ec2-user@ec2-3-92-225-108.compute-1.amazonaws.com
scp -i ~/ema-linux.pem ~/dev/red-panda-nft/discord/* ec2-user@ec2-3-92-225-108.compute-1.amazonaws.com:~/discord/.
python -m pip install -r requiremets.txt

    source discord_venv/bin/activate

```

Setting up PostgreSQL with Python 3 https://www.fullstackpython.com/blog/postgresql-python-3-psycopg2-ubuntu-1604.html