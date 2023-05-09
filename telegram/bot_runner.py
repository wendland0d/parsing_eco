from tg_bot import dp
from bot_setup import tg_bot

import asyncio

async def main():
    await dp.start_polling(tg_bot)

if __name__ == '__main__':
    asyncio.run(main())