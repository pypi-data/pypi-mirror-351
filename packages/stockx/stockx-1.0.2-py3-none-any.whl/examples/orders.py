from stockx.connection import setup
from stockx.orders import get_single_order

import asyncio

setup("", "")

async def main():
    res = await get_single_order("orderid")
    print(res)


asyncio.run(main())
