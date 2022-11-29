from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import websockets

from db import crud


from config import Config

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher(bot)


uri = Config.BOT_WS_URL


@dp.message_handler(commands=["start"])
async def process_start_command(message: types.Message):
    id = message.from_user.id
    name = message.from_user.first_name

    pic = await message.from_user.get_profile_photos()
    file_location = f"images/profile_pic/{id}.jpg" if pic.total_count != 0 else None

    user = await crud.create_user(id, name, profile_pic=file_location, url_ws=uri)
    await message.reply(f"{Config.ADMIN_URL}{user.token}")

    if pic.total_count != 0:
        await pic.photos[0][-1].download(destination=file_location)


if __name__ == "__main__":
    executor.start_polling(dp)
