import time
import asyncio

async def get_something():
    print("In Asynccccc")
    await asyncio.sleep(10)
    print("----- After await")


async def main():
    await asyncio.gather(get_something() , get_something())
    
asyncio.run(main())