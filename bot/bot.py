from aiogram import Bot,Dispatcher,executor,types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import  StatesGroup,State
from aiogram.types import ReplyKeyboardMarkup,KeyboardButton

from config import token_api
from sqlite import db_start,create_profile, edit_profile

async def on_startup(_):
    await db_start()
storage=MemoryStorage()
bot=Bot(token_api)
dp=Dispatcher(bot,storage=storage)

class ProfilStateaGroup(StatesGroup):

    photo=State()
    name=State()
    age=State()
    description=State()

def get_kb():
    kb=ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/create'))
    return kb
def get_cancel_kb():
    kb=ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/cancel'))
    return kb

@dp.message_handler(commands=["start"])
async def cmd_start(message:types.Message):
    await message.answer('Welcome!So as to create profile - type /create',
                         reply_markup=get_kb())
    await create_profile(user_id=message.from_user.id)
@dp.message_handler(commands=["create"])
async def cmd_create(message:types.Message):
    await message.reply("Let's create your profile! To begin with, send me your photo)",
                        reply_markup=get_cancel_kb())
    await ProfilStateaGroup.photo.set()
@dp.message_handler(commands=["cancel"],state='*')
async def cmd_cancel(message:types.Message,state:FSMContext):
    if state is None:
        return
    await state.finish()
    await message.reply('You cancel action ',reply_markup=get_kb())

@dp.message_handler(lambda message: not message.photo,state=ProfilStateaGroup.photo)
async def check_photo(message:types.Message):
    await message.reply('It is not photo')
@dp.message_handler(content_types=['photo'],state=ProfilStateaGroup.photo)
async def load_photo(message: types.Message,state: FSMContext):
    async with state.proxy() as data:
        data['photo']=message.photo[0].file_id

    await message.reply('Now send your name')
    await ProfilStateaGroup.next()

@dp.message_handler(state=ProfilStateaGroup.name)
async def load_name(message: types.Message,state: FSMContext):
    async with state.proxy() as data:
        data['name']=message.text

    await message.reply('Now send your age')
    await ProfilStateaGroup.next()

@dp.message_handler(lambda message:  not message.text.isdigit() or int(message.text) <=0
,state=ProfilStateaGroup.age)
async def check_age(message:types.Message):
    await message.reply('It is not true age)')

@dp.message_handler(state=ProfilStateaGroup.age)
async def load_age(message: types.Message,state: FSMContext):
    async with state.proxy() as data:
        data['age']=message.text

    await message.reply('Some words about you')
    await ProfilStateaGroup.next()

@dp.message_handler(state=ProfilStateaGroup.description)
async def load_description(message: types.Message,state: FSMContext):
    async with state.proxy() as data:
        data['description']=message.text
        await bot.send_photo(chat_id=message.from_user.id,
                       photo=data['photo'],
                       caption=f"{data['name']},{data['age']}\n{data['description']}")
    await edit_profile(state,user_id=message.from_user.id)
    await message.reply('Yout form is saved ')
    await state.finish()


if __name__=='__main__':
    executor.start_polling(dp,skip_updates=True,on_startup=on_startup)