from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
import asyncpg
import json
import logging
import os

app = FastAPI()
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@db:5432/dbname")
db_pool = None

async def create_tables():
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS plots (
                id VARCHAR(10) PRIMARY KEY,
                type TEXT,
                plot JSON
            )
        ''')
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS graph (
                id VARCHAR(10) PRIMARY KEY,
                node JSON,
                edges JSON
            )
        ''')

        await conn.execute('''
                           
        ''')

        # Create Stored Procedures
    except asyncpg.PostgresError as e:
        logging.error(f"Error creating table: {e}")
    finally:
        if conn:
            await conn.close()        

async def get_db():
    return db_pool

@app.on_event("startup")
async def startup():
    global db_pool
    await create_tables()
    db_pool = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    await db_pool.close()

@app.get("/health")
async def health_check(request: Request):
    db = await get_db()
    conn = await db.acquire()
    try:
        await conn.execute("SELECT 1")
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await db.release(conn)

@app.get("/add")
async def add(request: Request):
    db = await get_db()
    conn = await db.acquire()
    sample = {
        'id': 'MSC123',
        'name': 'Nick'
    }
    try:
        await conn.execute('''
            INSERT INTO plots(id, type, plot) 
            VALUES($1, $2, $3)
            ON CONFLICT (id)
            DO UPDATE SET plot = $3
        ''', 'MSC123', 'AIR', json.dumps(sample))

        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await db.release(conn)

@app.get("/delete")
async def delete(request: Request):
    db = await get_db()
    conn = await db.acquire()
    try:
        await conn.execute('''
            DELETE FROM plots
            WHERE id = 'MSC123'   
        ''')

        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await db.release(conn)

@app.get("/get")
async def get(request: Request):
    db = await get_db()
    conn = await db.acquire()
    try:
        # rows = await conn.fetch('''
        #     SELECT plot FROM plots 
        # ''')
        # print(rows[0]['plot'])

        # Search JSON
        rows = await conn.fetch(
            """
            SELECT *
            FROM plots
            WHERE plot ->> 'name' = $1
            """,
            'Nick'
        )
        # return jsonable_encoder(rows[0]['plot'])
        return json.loads(rows[0]['plot'])
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await db.release(conn)

# @app.get("/data")
# async def get_data(request: Request):
#     db = await get_db()
#     conn = await db.acquire()
#     try:
#         rows = await conn.fetch("SELECT * FROM test_table")
#         return {"data": [dict(row) for row in rows]}
#     except Exception as e:
#         return {"error": str(e)}
#     finally:
#         await db.release(conn)