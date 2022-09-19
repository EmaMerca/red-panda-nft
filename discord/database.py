import asyncpg
import datetime
import asyncio
from abc import abstractmethod


async def create_database(user, passw, db):
    db = Database(user, passw, db)
    await db._init()
    return db

class Database:
    def __init__(self, user, passw, db):
        self.user = user
        self.passw = passw
        self.db = db

    async def _init(self):
        await self._create_pool()
        await self._create_exp_db()
        await self._create_promo_db()
        await self._create_retweets_db()
        await self._create_users_db()

    async def _create_pool(self):
        self.pool = await asyncpg.create_pool(f'postgresql://{self.user}:{self.passw}@localhost/{self.db}')

    async def _create_exp_db(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    await connection.execute(
                        'CREATE TABLE experience(id serial PRIMARY KEY, uid bigint, uname text, exp float)'
                    )
                except asyncpg.exceptions.DuplicateTableError:
                    pass

    async def _create_users_db(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    await connection.execute(
                        'CREATE TABLE users(id serial PRIMARY KEY, uid bigint, uname text, iexp float, texp float, aexp float, role text)'
                    )
                except asyncpg.exceptions.DuplicateTableError:
                    pass

    async def _create_retweets_db(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    await connection.execute(
                        'CREATE TABLE retweets(id serial PRIMARY KEY, uid bigint, code text)'
                    )
                except asyncpg.exceptions.DuplicateTableError:
                    pass

    async def _create_promo_db(self):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                try:
                    await connection.execute(
                        'CREATE TABLE promo(id serial PRIMARY KEY, url text, code text)'
                    )
                except asyncpg.exceptions.DuplicateTableError:
                    pass


    async def write(self, query, *values):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(query, *values)
                return

    async def fetch(self, query, *values):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                return await connection.fetch(query, *values)

async def main():
    # Establish a connection to an existing database named "test"
    # as a "postgres" user.

    db = await create_database("akajukus", "diocane96", "discord")
    conn = await asyncpg.connect('postgresql://akajukus:diocane96@localhost/discord')
    # Execute a statement to create a new table.
    # await conn.execute('''
    #         DROP TABLE users
    #     ''')
    try:
        await conn.execute('''
            CREATE TABLE users(
                id serial PRIMARY KEY,
                name text,
                dob date
            )
        ''')
    except asyncpg.exceptions.DuplicateTableError:
        pass

    # Insert a record into the created table.
    await conn.execute('''
        INSERT INTO users(name, dob) VALUES($1, $2)
    ''', 'Bob', datetime.date(1984, 3, 1))

    await conn.execute('''
        INSERT INTO users(name, dob) VALUES($1, $2)
    ''', 'Bab', datetime.date(1984, 3, 2))
    # Select a row from the table.
    row = await conn.fetch(
        'SELECT * FROM users where NAME = $1', "Bob")
    # *row* now contains
    # asyncpg.Record(id=1, name='Bob', dob=datetime.date(1984, 3, 1))
    print(row)
    # Close the connection.
    await conn.close()

# asyncio.get_event_loop().run_until_complete(main())
