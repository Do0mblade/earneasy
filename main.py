

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove

from geopy.geocoders import Nominatim

from config.bot import TOKEN, OWNER_ID
from config.database import Database

from defs.keyboards import start_kb, state_stop, get_location, profile_kb, edit_my_profile_kb, main_menu_kb, create_order_title, create_order_category, job_format, check_orders_kb, search_orders_kb, My_orders_kb, responsed_order_kb, ready_order, work_orders_kb, answer_work_true, responsed_kb, add_referal, Archive_orders_kb, me_kb, admin_users_kb, admin_user_change_status

import asyncio


bot = Bot(token=TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())

db = Database()

class Reg_Form(StatesGroup):
    name = State()
    years = State()
    photo = State()
    city = State()
    ref_id = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext):
    if await db.check_user_in_db(message.from_user.id):
        await menu(message)
    else:
        start_command = message.text
        ref_id = str(start_command[7:])
        try:
            if ref_id == '' or int(ref_id) == message.from_user.id:
                ref_id = 0
        except:
            ref_id = 0
        async with state.proxy() as data:
            data['ref_id'] = ref_id
        await message.answer('👋 Привет, я бот для подработок!\n💸 Если хочешь найти исполнителя или заработать денег, то ты по адресу!', reply_markup=start_kb())

@dp.message_handler(text = '❌ Отменить', state='*')
async def stop_state_(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await menu(message)
    else:
        await state.finish()
        if await db.check_user_in_db(message.from_user.id):
            await message.answer('❌ Действие было отменено!', reply_markup=await main_menu_kb(message.from_user.id))
        else:
            await message.answer('❌ Действие было отменено!', reply_markup=ReplyKeyboardRemove())
            await start(message, state)

@dp.callback_query_handler(text='start_create_order')
async def start_create_order(callback: types.CallbackQuery):
    await callback.message.answer('qq', reply_markup=await main_menu_kb(callback.from_user.id))

@dp.callback_query_handler(text='start_registration')
async def start_registration_(callback: types.CallbackQuery, state: FSMContext):
    if await db.check_user_in_db(callback.from_user.id):
        await callback.answer('🥴 Вы уже зарегистрированы!')
    else:
        await Reg_Form.name.set()
        await bot.send_message(chat_id=callback.from_user.id, text='Давай познакомимся!🙋\nНапиши, <b>как тебя зовут</b>?', reply_markup=state_stop())

        await asyncio.sleep(10800)
        if await state.get_state() == 'Reg_Form:years' and not await state.get_state() is None:
            await callback.answer('🤷 Я до сих пор не знаю, <b>как можно к тебе обращаться?</b>')

@dp.message_handler(state=Reg_Form.name)
async def add_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Reg_Form.next()
    await message.answer('<b>🔢 Сколько тебе лет?</b>', reply_markup=state_stop())

    await asyncio.sleep(10800)
    if await state.get_state() == 'Reg_Form:years' and not await state.get_state() is None:
        await message.answer('🤷 Я до сих пор не знаю, <b>какой у тебя возраст?</b>')

@dp.message_handler(state=Reg_Form.years)
async def add_years(message: types.Message, state: FSMContext):
    try:
        if int(message.text) > 0:
            if int(message.text) < 100:
                async with state.proxy() as data:
                    data['years'] = int(message.text)
                await Reg_Form.next()
                await message.answer('Улыбочку…📸 \nОтправь свое лучшее фото для анкеты!', reply_markup=state_stop())

                await asyncio.sleep(10800)
                if await state.get_state() == 'Reg_Form:photo' and not await state.get_state() is None:
                    await message.answer('🤷 Я до сих пор не знаю, <b>как ты выглядишь?</b>')

            else:
                await state.set_state(Reg_Form.years.state)
                await message.answer('🙃 Вам слишком много лет.\n\nВведите настоящий возраст 😊')
        else:
            await state.set_state(Reg_Form.years.state)
            await message.answer(
                '🤪 Ваш возраст не может быть меньше или равен <b>0</b>\n\nВведите настоящий возраст 😊')
    except:
        await state.set_state(Reg_Form.years.state)
        await message.answer('😦 Вы неправильно указали ваш возраст!\n\nПопробуйте снова.')

@dp.message_handler(content_types=['photo'], state=Reg_Form.photo)
async def add_years(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await Reg_Form.next()
    await message.answer('<b>🌐 Отправьте мне свою геолокацию или напишите ваш город.</b>\n\nЕсли город будет написан неправильно, то вы <b>не сможете</b> найти себе подработку по городу!\n\nПример:\n<code>Москва</code>\n<code>Сочи</code>\n<code>Ростов-на-Дону</code>', reply_markup=get_location())

    await asyncio.sleep(10800)
    if await state.get_state() == 'Reg_Form:years' and not await state.get_state() is None:
        await message.answer('🤷 Я до сих пор не знаю, <b>в каком ты городе живёшь?</b>', reply_markup=get_location())

@dp.message_handler(content_types=['location', 'text'], state=Reg_Form.city)
async def add_years(message: types.Message, state: FSMContext):
    try:
        if message.text is None:
            lat = message.location.latitude
            lon = message.location.longitude
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.reverse(f'{lat}, {lon}')
            address = location.raw['address']
            city = address.get('city', '')
        else:
            city = message.text
        async with state.proxy() as data:
            data['city'] = city
        data = await state.get_data()
        await state.finish()
        username = message.from_user.username
        user_id = message.from_user.id
        if message.from_user.id == OWNER_ID:
            await db.insert_user(user_id, data, username, rights='admin')
        else:
            await db.insert_user(user_id, data, username)
        await message.answer('✅ Вы успешно зарегистрировались!\n\nВоспользуйтесь командой <b>/help</b>, чтобы узнать что умеет этот бот.', reply_markup=await main_menu_kb(message.from_user.id))
    except KeyError:
        await state.set_state(Reg_Form.city.state)
        await message.answer('📛 Что-то пошло не так, попробуйте снова.')

@dp.message_handler(commands=['profile'])
async def profile(message: types.Message):
    if await db.check_user_in_db(message.from_user.id):
        data = await db.select_user(message.from_user.id)
        count_referals = await db.count_referals(message.from_user.id)

        text = f"""
🧿 <i>{data[2]}, {data[4]}</i>
🌎 <i>{data[5]}</i>

❤️ <i>Приведено друзей:</i> <code>{count_referals}</code>

🤝 <i>Совершено сделок:</i> <code>{data[11]}</code>

<b>ID:</b> <code>{data[1]}</code>
"""
        photo = data[3]

        if len(text) < 1023:
            await bot.send_photo(chat_id=message.from_user.id, photo=photo, caption=text, reply_markup=profile_kb())
        else:
            await bot.send_photo(chat_id=message.from_user.id, photo=photo)
            await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=profile_kb())
    else:
        await message.reply('<i>📛 Чтобы использовать эту команду вам нужно создать профиль - <b>/start</b></i>', reply_markup=await main_menu_kb(message.from_user.id))


@dp.callback_query_handler(text='edit_profile')
async def edit_my_profile(callback: types.CallbackQuery):
    await bot.send_message(chat_id=callback.from_user.id, text='📜 Выберите, что хотите изменить:', reply_markup=edit_my_profile_kb())


class Edit_Profile(StatesGroup):
    photo = State()
    name = State()
    years = State()
    city = State()

@dp.callback_query_handler(text_contains='edit_')
async def edit_(callback: types.CallbackQuery):
    data = (callback.data)[5:]
    if data == 'name':
        await Edit_Profile.name.set()
        await callback.message.answer('📣 Как к тебе можно обращаться?', reply_markup=state_stop())
    elif data == 'years':
        await Edit_Profile.years.set()
        await callback.message.answer('🔢 Сколько тебе лет?', reply_markup=state_stop())
    elif data == 'city':
        await Edit_Profile.city.set()
        await callback.message.answer('🌐 Отправьте мне свою геолокацию или напишите ваш город.\n\nЕсли город будет написан неправильно, то вы <b>не сможете</b> найти себе подработку по городу!\n\nПример:\n<code>Москва</code>\n<code>Сочи</code>\n<code>Ростов-на-Дону</code>', reply_markup=get_location())
    elif data == 'photo':
        await Edit_Profile.photo.set()
        await callback.message.answer('📸 Отправьте мне новую фотографию.', reply_markup=state_stop())

@dp.message_handler(state=Edit_Profile.name)
async def update_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    data = await state.get_data()
    await state.finish()
    if data['name'] != ((await db.select_user(message.from_user.id))[2]):
        await db.update_profile(user_id=message.from_user.id, name=data['name'])
        await message.answer('✅ Вы успешно обновили своё имя!', reply_markup=await main_menu_kb(message.from_user.id))
    else:
        await message.answer('🙃 У вас уже установлено такое имя!', reply_markup=await main_menu_kb(message.from_user.id))

@dp.message_handler(state=Edit_Profile.years)
async def update_years(message: types.Message, state: FSMContext):
    try:
        if int(message.text) > 0:
            if int(message.text) < 100:
                async with state.proxy() as data:
                    data['years'] = int(message.text)
                data = await state.get_data()
                await state.finish()
                if data['years'] != ((await db.select_user(message.from_user.id))[4]):
                    await db.update_profile(user_id=message.from_user.id, years=data['years'])
                    await message.answer('✅ Вы успешно обновили свой возраст!', reply_markup=await main_menu_kb(message.from_user.id))
                else:
                    await message.answer('🙃 У вас уже установлен такой возраст!', reply_markup=await main_menu_kb(message.from_user.id))
            else:
                await state.set_state(Edit_Profile.years.state)
                await message.answer('🙃 Вам слишком много лет.\n\nВведите настоящий возраст 😊')
        else:
            await state.set_state(Edit_Profile.years.state)
            await message.answer(
                '🤪 Ваш возраст не может быть меньше или равен <b>0</b>\n\nВведите настоящий возраст 😊')
    except:
        await state.set_state(Edit_Profile.years.state)
        await message.answer('🧐 Вы неправильно указали ваш возраст!\n\nПопробуйте снова.')

@dp.message_handler(content_types=['location', 'text'], state=Edit_Profile.city)
async def update_city(message: types.Message, state: FSMContext):
    try:
        if message.text is None:
            lat = message.location.latitude
            lon = message.location.longitude
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.reverse(f'{lat}, {lon}')
            address = location.raw['address']
            city = address.get('city', '')
        else:
            city = message.text
        async with state.proxy() as data:
            data['city'] = city
        data = await state.get_data()
        await state.finish()
        if data['city'] != ((await db.select_user(message.from_user.id))[5]):
            await db.update_profile(user_id=message.from_user.id, city=data['city'])
            await message.answer('✅ Вы успешно обновили свой город!', reply_markup=await main_menu_kb(message.from_user.id))
        else:
            await message.answer('🙃 У вас уже установлено такой город!', reply_markup=await main_menu_kb(message.from_user.id))
    except:
        await state.set_state(Edit_Profile.city.state)
        await message.answer('😵 Что-то пошло не так, попробуйте снова.')

@dp.message_handler(content_types=['photo'], state=Edit_Profile.photo)
async def update_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    data = await state.get_data()
    await state.finish()
    await db.update_profile(user_id=message.from_user.id, photo=data['photo'])
    await message.answer('✅ Вы успешно обновили фотографию!', reply_markup=await main_menu_kb(message.from_user.id))

@dp.message_handler(commands=['ref'])
async def referal_url(message: types.Message):
    if await db.check_user_in_db(message.from_user.id):
        count_referals = await db.count_referals(message.from_user.id)
        user = await db.select_user(message.from_user.id)
        me = await bot.get_me()
        if int(user[6]) != 0:
            referer = f'\n🌝 <i>ID вашего реферера:</i> \n<code>{user[6]}</code>\n'
        else:
            referer = ''
        text = f"""
🌚 <b>Реферальная система</b>    

❤️ <i>Приведено друзей:</i> <code>{count_referals}</code>
{referer}
🌐 <i>Ваша реферальная ссылка:</i>
<code>https://t.me/{me.username}?start={message.from_user.id}</code>

🛡️ <i>Ваш реферальный код:</i> 
<code>{message.from_user.id}</code>

<span class="tg-spoiler">Надеюсь на наше сотрудничество 😁</span>

<b><i>/me</i> - о нас и розыгрышах. 🎁🎉</b>
"""
        await message.answer(text, reply_markup=await add_referal(message.from_user.id))
    else:
        await message.reply('<i>📛 Чтобы использовать эту команду вам нужно создать профиль - <b>/start</b></i>', reply_markup=await main_menu_kb(message.from_user.id))

class ADDref(StatesGroup):
    ref_id = State()

@dp.callback_query_handler(text='add_referal')
async def add_referal_id(callback: types.CallbackQuery, state: FSMContext):
    await ADDref.next()
    await callback.message.answer('🔢 Введите реферальный код.', reply_markup=state_stop())

@dp.message_handler(state=ADDref.ref_id)
async def add_ref_id(message: types.Message, state: FSMContext):
    try:
        if int(message.text) != message.from_user.id:
            dt = await db.select_user(int(message.text))
            if not dt is None:
                async with state.proxy() as data:
                    data['ref_id'] = message.text
                st = await state.get_data()
                await state.finish()
                await db.update_ref_id(message.from_user.id, int(st['ref_id']))
                await message.answer('✅ Вы успешно добавили реферера!')
            else:
                await message.answer('📛 Вы ввели неверный реферальный код!', reply_markup=state_stop())
        else:
            await message.answer('😉 Вы не можете использовать свой реферальный код!', reply_markup=state_stop())
    except:
        await message.answer('📛 Вы ввели неверный реферальный код!', reply_markup=state_stop())

@dp.message_handler(commands=['menu'])
async def menu(messgae: types.Message):
    await messgae.answer('📝', reply_markup=await main_menu_kb(messgae.from_user.id))

class Create_Order(StatesGroup):
    title = State()
    category = State()
    subcategory = State()
    company = State()
    format_job = State()
    adress = State()
    cost = State()
    deadlines = State()
    duties = State()
    requirements = State()
    additionally = State()

@dp.message_handler(commands=['cr'])
async def create_order(message: types.Message):
    await Create_Order.title.set()
    await message.answer('📌 Выберите, какое объявление хотите разместить.\n\n<i>Вакансия - долгосрочная позиция\nПодработка/задача - 1-3 дня на выполнение</i>', reply_markup=create_order_title())

@dp.message_handler(state=Create_Order.title)
async def add_title(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['title'] = message.text
    st = await state.get_data()
    await Create_Order.next()
    if st['title'] == 'Вакансия':
        await message.answer('✅ <b>Выберите категорию</b>, которая подходит под Вашу вакансию.\n\n<i>P.S. Постарайтесь выбрать категорию из предложенного списка, не нажимая на «другое». Тогда вакансия будет предложена целевым соискателям и будет лучше ранжироваться.</i>', reply_markup=await create_order_category('Вакансия'))
    elif st['title'] == 'Подработка/задача':
        await message.answer('✅ <b>Выберите задачу</b> из списка, на которую Вам нужно подобрать исполнителя.', reply_markup=await create_order_category('Подработка/задача'))
    else:
        await Create_Order.title.set()
        await message.answer('📋 Выберите тип объявления из предложенного.', reply_markup=create_order_title())

@dp.message_handler(state=Create_Order.category)
async def add_category(message: types.Message, state: FSMContext):
    st = await state.get_data()
    categories = []
    cat = []
    if st['title'] == 'Вакансия':
        cat = await db.select_categories('Вакансия')
    elif st['title'] == 'Подработка/задача':
        cat = await db.select_categories('Подработка/задача')
    for i in cat:
        categories.append(i[0])
    if message.text in categories or message.text == 'Другое':
        async with state.proxy() as data:
            data['category'] = message.text
        if message.text == 'Другое':
            if st['title'] == 'Вакансия':
                await Create_Order.next()
                await message.answer('✍️ Впишите, на какую <b>вакансию</b> Вам нужен сотрудник.\n\n<i>Пример:\nIT-Рекрутер</i>', reply_markup=state_stop())
            else:
                await Create_Order.next()
                await message.answer('🎯 Напишите, под какую задачу нужен исполнитель.', reply_markup=state_stop())
        else:
            async with state.proxy() as data:
                data['subcategory'] = None
            await Create_Order.company.set()
            await message.answer('🏦Укажите название  и деятельность компании.\nЕсли Вы размещаете объявление не от лица компании, укажите <b>ФИО</b>.\n\n<i>Пример:\nТипография «ЛистАрт»/Алексеев Алексей Алексеевич</i>')

    else:
        await Create_Order.category.set()
        await message.answer('📋 Выберите категорию объявления из предложенного.', reply_markup=await create_order_category(st['title']))

@dp.message_handler(state=Create_Order.subcategory)
async def add_subcategory(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['subcategory'] = message.text
    await Create_Order.next()
    await message.answer('🏦Укажите название  и деятельность компании.\nЕсли Вы размещаете объявление не от лица компании, укажите <b>ФИО</b>.\n\n<i>Пример:\nТипография «ЛистАрт»/Алексеев Алексей Алексеевич</i>')

@dp.message_handler(state=Create_Order.company)
async def add_company(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['company'] = message.text
    dt = await state.get_data()
    await Create_Order.next()
    await message.answer('👨‍💻 Уточните <b>формат работы</b>.', reply_markup=await job_format(dt['title']))

@dp.message_handler(state=Create_Order.format_job)
async def add_format_job(message: types.Message, state: FSMContext):
    formats = ['Онлайн', 'Оффлайн', 'Гибрид']
    st = await state.get_data()
    if message.text in formats:
        async with state.proxy() as data:
            data['format_job'] = message.text
        await Create_Order.next()
        st = await state.get_data()
        if st['format_job'] != 'Онлайн':
            if st['title'] == 'Вакансия':
                await message.answer('📍 Напишите <b>местоположение Вашего офиса</b>. Можете указать город.\n\n<i>Пример:\nг.Москва, ул.Самокатная д.4 стр.1</i>', reply_markup=state_stop())
            else:
                await message.answer('📍 Напишите место выполнения задачи.\n\n<i>Пример:\nм.Щелковская, около главного входа ТЦ «Щёлковский».</i>', reply_markup=state_stop())
        else:
            async with state.proxy() as data:
                data['adress'] = None
            await Create_Order.cost.set()
            if st['title'] == 'Вакансия':
                await message.answer('💸 Укажите <b>информацию об оплате</b>.\n\n<i>Пример:\nОклад 30 тыс.р. + 5 тыс.р. за каждую закрытую вакансию.</i>', reply_markup=state_stop())
            else:
                await message.answer('💸 Укажите <b>информацию об оплате</b>.\n\n<i>Пример:\nОплата почасовая - 350р/час.</i>', reply_markup=state_stop())
    else:
        await Create_Order.format_job.set()
        await message.answer('📛 Вы неверно указали формат работы, пожалуйста, нажмите на соответствующую кнопку.', reply_markup=await job_format(st['title']))


@dp.message_handler(state=Create_Order.adress)
async def add_adress(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['adress'] = message.text
    st = await state.get_data()
    if st['title'] == 'Вакансия':
        await Create_Order.next()
        await message.answer('💸 Укажите <b>информацию об оплате</b>.\n\n<i>Пример:\nОклад 30 тыс.р. + 5 тыс.р. за каждую закрытую вакансию</i>', reply_markup=state_stop())
    else:
        await Create_Order.next()
        await message.answer('💸 Укажите <b>информацию об оплате</b>.\n\n<i>Пример:\nОплата почасовая - 350р/час.</i>', reply_markup=state_stop())

@dp.message_handler(state=Create_Order.cost)
async def add_cost(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['cost'] = message.text
    st = await state.get_data()
    if st['title'] == 'Вакансия':
        await Create_Order.next()
        await message.answer('⏰ Укажите <b>график работы</b>.\n\n<i>Пример:\n5/2 с 9:00 до 18:00.</i>')
    else:
        await Create_Order.next()
        await message.answer('⏰ Укажите <b>информацию о сроках.</b>\n\n<i>Пример:\nВыйти на точку для раздачи листовок необходимо 12 сентября в 17:30 и до 19:30.</i>', reply_markup=state_stop())

@dp.message_handler(state=Create_Order.deadlines)
async def add_deadlines(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['deadlines'] = message.text
    dt = await state.get_data()
    await Create_Order.next()
    if dt['title'] == 'Вакансия':
        await message.answer('💼 Укажите <b>обязанности кандидата</b>.\n\n<i>Пример:\n•Проведение телефонных, видео интервью;\n•Ведение вакансии под ключ;\n•Общение с заказчиками;\n•Ежедневная отчетность.</i>', reply_markup=state_stop())
    else:
        await message.answer('💼 Укажите <b>обязанности кандидата.</b>\n\n<i>Пример:\nРаздача листовок около метро с кратким скриптом для привлечения.</i>')

@dp.message_handler(state=Create_Order.duties)
async def add_duties(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['duties'] = message.text
    dt = await state.get_data()
    await Create_Order.next()
    if dt['title'] == 'Вакансия':
        await message.answer('🧑‍💼 Укажите <b>требования к кандидату</b>.\n\n<i>Пример:\n•Грамотная устная и письменная речь;\n•Опыт ведения телефонных или личных переговоров;\n•Опыт в найме или управлении приветствуется.</i>', reply_markup=state_stop())
    else:
        await message.answer('🤵🏼‍♂️ Укажите <b>требования к кандидату.</b>\n\n<i>Пример:\n•Возраст 18+\n•Грамотная устная речь;\n•Активность;\n•Хорошее настроение:)</i>')

@dp.message_handler(state=Create_Order.requirements)
async def add_requirements(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['requirements'] = message.text
    dt = await state.get_data()
    await Create_Order.next()
    if dt['title'] == 'Вакансия':
        await message.answer('🗂️ Укажите дополнительные условия работы.\nЕсли их нет, напишите «нет»\n\n<i>Пример:\n•Дружный коллектив;\n•Поддержка на всех этапах работы;\n•Карьерный рост;\n•Первая неделя - испытательный срок. Не оплачивается.</i>', reply_markup=state_stop())
    else:
        await message.answer('✍🏻 Укажите <b>дополнительные условия работы.</b>\nЕсли их нет, напишите «нет»\n\n<i>Пример:\nПеред началом работы будет краткий инструктаж в ZOOM.\nЛистовки нужно будет забрать с офиса на м.Курская.</i>', reply_markup=state_stop())


@dp.message_handler(state=Create_Order.additionally)
async def add_additionally(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['additionally'] = message.text
    data = await state.get_data()
    await state.finish()
    username = message.from_user.username
    await db.insert_order(message.from_user.id, data, username)
    data2 = await db.select_all_AdminsAndModers()
    dc = await db.Dont_Check_orders()
    for i in data2:
        await bot.send_message(chat_id=i[0], text=f'❗ Появился новый заказ, требующий проверки!\n\nНазвание компании: <b>{data["company"]}</b>\n\nВсего не проверенных заказов: <code>{len(dc)}</code>\n\n<i><b>/check</b></i> - начать проверку заказов.')

    await message.answer('🛠️ Ваше объявление было отправлено на модерацию.\n\nПосле одобрения вы получите уведомление.', reply_markup=await main_menu_kb(message.from_user.id))

@dp.message_handler(commands=['search'])
async def search_orders(message: types.Message, page=0, message_id=None):
    if await db.check_user_in_db(message.from_user.id):
        data = await db.search_orders(message.from_user.id)
        last_page = False
        if data == []:
            if message_id is None:
                await message.answer('🚫 На данный момент нет заказов от работодателей.\n\nВаши заказы не будут отображаться у вас в поиске, чтобы их посмотреть введите команду <b>/my_orders</b>.')
            else:
                await bot.edit_message_text(message_id=message_id, chat_id=message.from_user.id, text='🚫 На данный момент нет заказов от работодателей.')
        else:
            if message_id is None:
                await message.answer(f'🌟 Найдено заказов: {len(data)}')
            if last_page == False:
                try:
                    dt = data[int(page) + 1]
                except:
                    last_page = True
            if len(data) == 1:
                last_page = True
            data = data[int(page)]

            if data[7] == 'None':
                adress = ''
            else:
                adress = f'\n🔷 <b>Адрес</b>:\n<code>{data[6]}</code>\n'

            if data[4] == 'None':
                 subcategory = ''
            else:
                subcategory = ': ' + data[4]

            text = f"""
🔶 <b>{data[2]}</b>:
{data[3]}{subcategory}

🔷 <b>Работодатель</b>:
<code><b>{data[5]}</b></code>

🔷 <b>{data[6]}</b>
{adress}
🔷 <b>Оплата</b>:
{data[8]}

🔷 <b>График</b>:
{data[9]}

🔷 <b>Обязанности</b>:
{data[11]}

🔷 <b>Требования к кандидату</b>:
{data[12]}

🔷 <b>Дополнительные условия работы</b>:
{data[10]}

<code>{data[18]}</code>
"""
            post_id = data[0]
            if message_id is None:
                await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=await search_orders_kb(page, last_page, post_id))
            else:
                await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=message_id, reply_markup=await search_orders_kb(page, last_page, post_id))
    else:
        await message.reply('<i>📛 Чтобы использовать эту команду вам нужно создать профиль - <b>/start</b></i>', reply_markup=await main_menu_kb(message.from_user.id))



@dp.callback_query_handler(text_contains='search_pg_')
async def next_back_page_search(callback: types.CallbackQuery):
    data = (callback.data)[10:]
    await search_orders(callback, page=int(data), message_id=callback.message.message_id)

@dp.callback_query_handler(text_contains='respond_')
async def next_back_page_search(callback: types.CallbackQuery):
    order_id = (callback.data)[8:]
    if await db.check_responses_on_order_user(callback.message.chat.id, int(order_id)):
        await callback.message.answer('📛 Вы уже откликались на этот заказ!')
    else:
        await db.insert_response(callback.message.chat.id, int(order_id))
        data = await db.select_order_for_id(int(order_id))
        user = await db.select_user(callback.message.chat.id)
        responses = await db.select_all_responses_order(int(order_id))
        await callback.message.answer('✅ Вы успешно откликнулись на этот заказ!')
        if data[4] == 'None':
            subcategory = data[3]
        else:
            subcategory = ': ' + data[4]
        await bot.send_message(chat_id=data[1], text=f'Новый отклик ✨\n\nЗаказ:\n<b>{data[2]}: {subcategory}</b>\n\nПользователь:\n<b>{user[2]}, {user[4]}, {user[5]}</b>\n\nВсего откликов: <code>{len(responses)}</code>\n\n/my_orders - посмотреть ваши заказы и отклики на них.')

@dp.message_handler(commands=['my_orders'])
async def my_orders(message: types.Message, page=0, message_id=None):
        data = await db.orders_user(message.from_user.id)
        last_page = False
        if data == []:
            if message_id is None:
                await message.answer('🚫 У вас нет созданных заказов.')
            else:
                await bot.edit_message_text(message_id=message_id, chat_id=message.from_user.id, text='🚫 У вас нет созданных заказов.')
        else:
            if message_id is None:
                await message.answer(f'🧾 Ваши заказы: {len(data)}')
            if last_page == False:
                try:
                    dt = data[int(page) + 1]
                except:
                    last_page = True
            if len(data) == 1:
                last_page = True
            try:
                data = data[int(page)]
            except:
                data = data[0]

            if data[15]:
                if data[16]:
                    ban = '\n<code><b>Блокировка поста</b></code>'
                else:
                    ban = ''
                txt = f'\nСтатус проверки: <code>Одобрено</code>{ban}'
            else:
                txt = '\nСтатус проверки: <code>Отклонено</code>'

            resp = await db.select_all_responses_order(data[0])

            if data[7] == 'None':
                adress = ''
            else:
                adress = f'\n🔷 <b>Адрес</b>:\n<code>{data[6]}</code>\n'

            if data[4] == 'None':
                subcategory = ''
            else:
                subcategory = ': ' + data[4]

            text = f"""
🔶 <b>{data[2]}</b>:
{data[3]}{subcategory}

🔷 <b>Работодатель</b>:
<code><b>{data[5]}</b></code>

🔷 <b>{data[6]}</b>
{adress}
🔷 <b>Оплата</b>:
{data[8]}

🔷 <b>График</b>:
{data[9]}

🔷 <b>Обязанности</b>:
{data[11]}

🔷 <b>Требования к кандидату</b>:
{data[12]}

🔷 <b>Дополнительные условия работы</b>:
{data[10]}

🔽 <b>Данные по заказу</b> 🔽
Создан: <code>{data[18]}</code>{txt}
Откликов: <code>{len(resp)}</code>
"""
            post_id = data[0]
            if message_id is None:
                await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=await My_orders_kb(page, last_page, post_id))
            else:
                await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=message_id, reply_markup=await My_orders_kb(page, last_page, post_id))


@dp.callback_query_handler(text_contains='morders_pg_')
async def next_back_page_my_orders(callback: types.CallbackQuery):
        data = (callback.data)[11:]
        await my_orders(callback, page=int(data), message_id=callback.message.message_id)

@dp.callback_query_handler(text_contains='archive_')
async def archive_order(callback: types.CallbackQuery):
        data = ((callback.data)[8:]).split('_')
        await db.archive_order(int(data[0]))
        await callback.answer('🗃️ Ваш заказ был добавлен в архив.')
        await my_orders(callback, page=int(data[1])+1, message_id=callback.message.message_id)

@dp.callback_query_handler(text_contains='responsed_')
async def responsed_order(callback: types.CallbackQuery, page=0, message_id=None, order_id=None):
        if order_id is None:
            data = (callback.data)[10:]
            order_id = data
        data = await db.select_all_responses_order(int(order_id))
        last_page = False
        if data == []:
            if message_id is None:
                await callback.message.answer('🚫 Откликов не обнаружено.')
            else:
                await bot.edit_message_text(message_id=message_id, chat_id=callback.from_user.id,
                                            text='🚫 Откликов не обнаружено.')
        else:
            if last_page == False:
                try:
                    dt = data[int(page) + 1]
                except:
                    last_page = True
            if len(data) == 1:
                last_page = True
            try:
                data = data[int(page)]
            except:
                data = data[0]

            user_info = await db.select_user(data[1])
            text = f"""
🧿 <i>{user_info[2]}, {user_info[4]}</i>
🌎 <i>{user_info[5]}</i>

🤝 <i>Совершено сделок:</i> <code>{user_info[11]}</code>
"""
            if message_id is None:
                await bot.send_message(chat_id=callback.from_user.id, text=text, reply_markup=await responsed_order_kb(page, last_page, order_id, user_info[1]))
            else:
                await bot.edit_message_text(text=text, chat_id=callback.from_user.id, message_id=message_id, reply_markup=await responsed_order_kb(page, last_page, order_id, user_info[1]))

@dp.callback_query_handler(text_contains='rorder_pg_')
async def next_back_page_responsed(callback: types.CallbackQuery):
        data = ((callback.data)[10:]).split('_')
        await responsed_order(callback, page=int(data[0]), message_id=callback.message.message_id, order_id=int(data[1]))

@dp.callback_query_handler(text_contains='respons_true_')
async def respons_true_user(callback: types.CallbackQuery):
        data = ((callback.data)[13:]).split('_')
        order_data = await db.order(int(data[1]))
        user_data = await db.select_user(int(data[0]))
        if order_data[4] == 'None':
            subcategory = order_data[3]
        else:
            subcategory = order_data[4]
        text = f"""
☕ Поздравляю, {user_data[2]} 🎉 🎊

🔮 Тебя выбрали для выполнения заказа:
<b>{order_data[2]}: {subcategory}</b>

🎨 Нажимай на кнопку ниже и подтверди свою готовность!
"""
        data.append(order_data[1])
        await bot.send_message(chat_id=data[0], text=text, reply_markup=await ready_order(data))
        await bot.delete_message(message_id=callback.message.message_id, chat_id=callback.from_user.id)
        await callback.message.answer(f'📧 Сообщение пользователю <b>{user_data[2]}</b> было отправлено!\nКак только он подтвердит свою готовность, вы получите контакты для связи.')

@dp.callback_query_handler(text_contains='ready_order_')
async def answer_user_on_order(callback: types.CallbackQuery):
    if await db.check_user_in_db(callback.from_user.id):
        data = ((callback.data)[12:]).split('_')
        check = await db.select_executor_order(int(data[2]))
        if check[0] is None:
            if data[0] == 'true':
                await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
                executor_data = await db.select_user(callback.from_user.id)
                order_data = await db.order(int(data[2]))
                await db.update_executor_id_order(callback.from_user.id, int(data[2]))
                if order_data[7] == 'None':
                    adress = ''
                else:
                    adress = f'\n🔷 <b>Адрес</b>:\n<code>{order_data[6]}</code>\n'
                if order_data[4] == 'None':
                    subcategory = ''
                else:
                    subcategory = ': ' + order_data[4]
                text1 = f'👤 <b>Заказчик</b>:\n@{order_data[21]}'
                text2 = f"""
🔶 <b>{order_data[2]}</b>:
{order_data[3]}{subcategory}

🔷 <b>Работодатель</b>:
<code><b>{order_data[5]}</b></code>

🔷 <b>{order_data[6]}</b>
{adress}
🔷 <b>Оплата</b>:
{order_data[8]}

🔷 <b>График</b>:
{order_data[9]}

🔷 <b>Обязанности</b>:
{order_data[11]}

🔷 <b>Требования к кандидату</b>:
{order_data[12]}

🔷 <b>Дополнительные условия работы</b>:
{order_data[10]}

<i><b>/work</b> - посмотреть заказы в работе или подтвердить их выполнение.</i>
"""
                await bot.send_message(chat_id=callback.from_user.id, text=text1)
                await bot.send_message(chat_id=callback.from_user.id, text=text2)
                if order_data[4] == 'None':
                    subcategory = order_data[3]
                else:
                    subcategory = order_data[4]
                text3 = f"""
🧿 <i>{executor_data[2]}, {executor_data[4]}</i>
🌎 <i>{executor_data[5]}</i>
🦾 <b>@{executor_data[10]}</b>

👍 Согласился на выполнение:
<b>{order_data[2]}: {subcategory}</b>

⚠️ После успешно выполненной задачи, <b>вы должны будете подтвердить её выполнение здесь</b>.
"""
                photo2 = executor_data[3]
                await bot.send_photo(chat_id=order_data[1], photo=photo2, caption=text3)
            elif data[0] == 'false':
                await db.delete_respons_user(callback.from_user.id, int(data[2]))
                await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
                await callback.message.answer('Очень жаль, что вы отказались 😔')
                await bot.send_message(chat_id=data[3], text='😔 К сожалению, пользователь отказался от выполнения заказа.')
        else:
            await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text='😔 К сожалению, кто-то опередил вас и принял заказ раньше.')


@dp.message_handler(commands=['work'])
async def orders_in_work(message: types.Message, page=0, message_id=None):
    if await db.check_user_in_db(message.from_user.id):
        data = await db.orders_in_progress(message.from_user.id)
        last_page = False
        if data == []:
            if message_id is None:
                await message.answer('🚫 У вас нет заказов в работе.')
            else:
                await bot.edit_message_text(message_id=message_id, chat_id=message.from_user.id,
                                            text='🚫 У вас нет заказов в работе.')
        else:
            if last_page == False:
                try:
                    dt = data[int(page) + 1]
                except:
                    last_page = True
            if len(data) == 1:
                last_page = True
            try:
                data = data[int(page)]
            except:
                data = data[0]

            if data[7] == 'None':
                adress = ''
            else:
                adress = f'\n🔷 <b>Адрес</b>:\n<code>{data[6]}</code>\n'

            if data[4] == 'None':
                subcategory = ''
            else:
                subcategory = ': ' + data[4]

            text = f"""
🔶 <b>{data[2]}</b>:
{data[3]}{subcategory}

🔷 <b>Работодатель</b>:
<code><b>{data[5]}</b></code>

🔷 <b>{data[6]}</b>
{adress}
🔷 <b>Оплата</b>:
{data[8]}

🔷 <b>График</b>:
{data[9]}

🔷 <b>Обязанности</b>:
{data[11]}

🔷 <b>Требования к кандидату</b>:
{data[12]}

🔷 <b>Дополнительные условия работы</b>:
{data[10]}
"""
            post_id = data[0]
            username = data[21]
            if message_id is None:
                await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=await work_orders_kb(page, last_page, post_id, username))
            else:
                await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=message_id, reply_markup=await work_orders_kb(page, last_page, post_id, username))
    else:
        await message.reply('<i>📛 Чтобы использовать эту команду вам нужно создать профиль - <b>/start</b></i>', reply_markup=await main_menu_kb(message.from_user.id))



@dp.callback_query_handler(text_contains='work_pg_')
async def next_back_page_my_orders(callback: types.CallbackQuery):
    if await db.check_user_in_db(callback.from_user.id):
        data = (callback.data)[8:]
        await orders_in_work(callback, page=int(data), message_id=callback.message.message_id)

@dp.callback_query_handler(text_contains='work_answer_')
async def work_answer(callback: types.CallbackQuery):
    if await db.check_user_in_db(callback.from_user.id):
        data = ((callback.data)[12:]).split('_')
        order_data = await db.order(int(data[1]))
        user_data = await db.select_user(callback.from_user.id)
        if data[0] == 'true':
            await callback.message.answer('📧 Сообщение с подтверждением отправлено работодателю, ожидайте.')
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
            if order_data[4] == 'None':
                subcategory = order_data[3]
            else:
                subcategory = order_data[4]
            await bot.send_message(chat_id=order_data[1], text=f'✅ Пользователь <b>{user_data[2]}</b> выполнил свою работу.\n\nЗаказ:\n<b>{order_data[2]}: {subcategory}</b>\n\nПодтвердите выполнение заказа или опровергните это.', reply_markup=answer_work_true(data[1]))
        elif data[0] == 'false':
            await db.del_update_executor_id_order(int(data[1]))
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
            await callback.message.answer('Очень жаль, что вы отказались 😔')
            await bot.send_message(chat_id=order_data[1], text='😔 К сожалению, пользователь отказался от выполнения заказа.')
            await db.delete_respons_user(user_data[1], order_data[0])

@dp.callback_query_handler(text_contains='work_completed_')
async def work_completed(callback: types.CallbackQuery):
        data = ((callback.data)[15:]).split('_')
        order_data = await db.order(int(data[1]))
        user_dt = await db.select_user(order_data[20])
        if data[0] == 'true':
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
            await callback.message.answer('✅ Заказ был успешно закрыт.')
            await bot.send_message(chat_id=user_dt[1], text='✅ Хорошая работа! Заказчик остался доволен твоей работой!')
            rep = await db.select_transactions_completed(user_dt[1])
            await db.update_transactions_completed(user_dt[1], (int(rep[0])+1))
            if await db.check_user_in_db(order_data[1]):
                rep = await db.select_transactions_completed(order_data[1])
                await db.update_transactions_completed(order_data[1], (int(rep[0]) + 1))
            await db.completed_order(int(data[1]))
            await db.delete_respons_user(user_dt[1], data[1])
        elif data[0] == 'false':
            await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
            await callback.message.answer('Благодарим за честность. 👍')
            await bot.send_message(chat_id=user_dt[1], text='📛 Заказчик отказался принимать вашу работу.')

@dp.message_handler(commands='responses')
async def responses_user(message: types.Message, page=0, message_id=None):
    if await db.check_user_in_db(message.from_user.id):
        data = await db.select_all_responses_user(message.from_user.id)
        last_page = False
        if data == []:
            if message_id is None:
                await message.answer('🚫 У вас нет откликов.')
            else:
                await bot.edit_message_text(message_id=message_id, chat_id=message.from_user.id,
                                            text='🚫 У вас нет откликов.')
        else:
            if last_page == False:
                try:
                    dt = data[int(page) + 1]
                except:
                    last_page = True
            if len(data) == 1:
                last_page = True
            try:
                data = data[int(page)]
            except:
                data = data[0]

            data = await db.order(data[2])

            if data[7] == 'None':
                adress = ''
            else:
                adress = f'\n🔷 <b>Адрес</b>:\n<code>{data[6]}</code>\n'

            if data[4] == 'None':
                subcategory = ''
            else:
                subcategory = ': ' + data[4]

            text = f"""
🔶 <b>{data[2]}</b>:
{data[3]}{subcategory}

🔷 <b>Работодатель</b>:
<code><b>{data[5]}</b></code>

🔷 <b>{data[6]}</b>
{adress}
🔷 <b>Оплата</b>:
{data[8]}

🔷 <b>График</b>:
{data[9]}

🔷 <b>Обязанности</b>:
{data[11]}

🔷 <b>Требования к кандидату</b>:
{data[12]}

🔷 <b>Дополнительные условия работы</b>:
{data[10]}
"""
            post_id = data[0]
            if message_id is None:
                await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=await responsed_kb(page, last_page, post_id, message.from_user.id))
            else:
                await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=message_id, reply_markup=await responsed_kb(page, last_page, post_id, message.from_user.id))
    else:
        await message.reply('<i>📛 Чтобы использовать эту команду вам нужно создать профиль - <b>/start</b></i>', reply_markup=await main_menu_kb(message.from_user.id))


@dp.callback_query_handler(text_contains='order_respo_')
async def no_respons(callback: types.CallbackQuery):
    if await db.check_user_in_db(callback.from_user.id):
        data = ((callback.data)[12:]).split('_')
        await db.delete_respons_user(int(data[1]), int(data[0]))
        await callback.message.answer('✅ Отклик был успешно удалён!')
        await responses_user(callback, int(data[2]), callback.message.message_id)

@dp.callback_query_handler(text_contains='order_respons_pg_')
async def next_back_page_responses_user(callback: types.CallbackQuery):
    if await db.check_user_in_db(callback.from_user.id):
        data = (callback.data)[17:]
        await responses_user(callback, page=int(data), message_id=callback.message.message_id)


@dp.message_handler(commands='archive')
async def archive_orders_user(message: types.Message, page=0, message_id=None):
        data = await db.select_archive_orders_user(message.from_user.id)
        last_page = False
        if data == []:
            if message_id is None:
                await message.answer('🚫 У вас нет заказов в архиве.')
            else:
                await bot.edit_message_text(message_id=message_id, chat_id=message.from_user.id, text='🚫 У вас нет заказов в архиве.')
        else:
            if last_page == False:
                try:
                    dt = data[int(page) + 1]
                except:
                    last_page = True
            if len(data) == 1:
                last_page = True
            try:
                data = data[int(page)]
            except:
                data = data[0]

            if data[13]:
                if data[14]:
                    ban = '<code><b>Блокировка поста</b></code>'
                else:
                    ban = ''
                txt = f'\nСтатус проверки: <code>Одобрено</code>\n{ban}'
            else:
                txt = '\nСтатус проверки: <code>Отклонено</code>'

            resp = await db.select_all_responses_order(data[0])

            if data[6] == 'None':
                adress = ''
            else:
                adress = f'\n🔷 <b>Адрес</b>:\n<code>{data[6]}</code>\n'

            if data[4] == 'None':
                subcategory = ''
            else:
                subcategory = ': ' + data[4]

            text = f"""
🔶 <b>{data[2]}</b>:
{data[3]}{subcategory}

🔷 <b>Работодатель</b>:
<code><b>{data[5]}</b></code>

🔷 <b>{data[6]}</b>
{adress}
🔷 <b>Оплата</b>:
{data[8]}

🔷 <b>График</b>:
{data[9]}

🔷 <b>Обязанности</b>:
{data[11]}

🔷 <b>Требования к кандидату</b>:
{data[12]}

🔷 <b>Дополнительные условия работы</b>:
{data[10]}

🔽 <b>Данные по заказу</b> 🔽
Создан: <code>{data[18]}</code>{txt}
Откликов: <code>{len(resp)}</code>
"""
            post_id = data[0]
            if message_id is None:
                await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=await Archive_orders_kb(page, last_page, post_id))
            else:
                await bot.edit_message_text(text=text, chat_id=message.from_user.id, message_id=message_id, reply_markup=await Archive_orders_kb(page, last_page, post_id))

@dp.callback_query_handler(text_contains='archive_orders_pg_')
async def next_back_page_my_orders(callback: types.CallbackQuery):
        data = (callback.data)[18:]
        await archive_orders_user(callback, page=int(data), message_id=callback.message.message_id)

@dp.callback_query_handler(text_contains='public_')
async def archive_order(callback: types.CallbackQuery):
        data = ((callback.data)[7:]).split('_')
        await db.public_order(int(data[0]))
        await callback.answer('✅ Ваш заказ был успешно опубликован.')
        await archive_orders_user(callback, page=int(data[1])+1, message_id=callback.message.message_id)

@dp.message_handler(commands=['me'])
async def me(message: types.Message):
    text = """
Проект <b>«EarnEasy»</b> создан, чтобы ускорить процесс поиска и выкладки подработки, сделать его простым и удобным для каждого.

Здесь можно получить индивидуальную подборку актуальных предложений и начать зарабатывать уже сегодня!

<i>Чтобы знать больше, подпишись на официальную группу <b><a href="https://vk.com/earneasybot">ВКонтакте</a></b>!

<span class="tg-spoiler">Там ты найдешь подборки самых интересных вакансий, а также сможешь принимать участие в регулярных розыгрышах призов🎁</span></i>
"""
    await message.answer(text, reply_markup=me_kb())





# ADMIN COMMANDS
@dp.message_handler(commands=['set_admin'])
async def set_admin(message: types.Message):
    if await db.check_user_in_db(message.from_user.id):
        if message.from_user.id == OWNER_ID:
            await db.update_rights(message.from_user.id, 'admin')
            await message.answer('👑 Ваши права повышены до администратора!')


@dp.message_handler(commands=['check'])
async def check_orders(message: types.Message, page=0, message_id=None):
    if await db.check_user_in_db(message.from_user.id):
        data = await db.select_user_rights(message.from_user.id)
        if data[0] == 'admin':
            data = await db.Dont_Check_orders()
            last_page = False
            if data == []:
                if message_id is None:
                    await message.answer('🚫 На данный момент нет заказов на модерации.')
                else:
                    await bot.edit_message_text(message_id=message_id, chat_id=message.from_user.id, text='🚫 На данный момент нет заказов на модерации.')
            else:
                if message_id is None:
                    await message.answer(f'❕ Не проверенных заказов: {len(data)}')
                if last_page == False:
                    try:
                        dt = data[int(page)+1]
                    except:
                        last_page = True
                if len(data) == 1:
                    last_page = True
                data = data[int(page)]

                if data[7] == 'None':
                    adress = ''
                else:
                    adress = f'\n🔷 <b>Адрес</b>:\n<code>{data[6]}</code>\n'

                if data[4] == 'None':
                    subcategory = ''
                else:
                    subcategory = ': '+ data[4]

                text=f"""
🔶 <b>{data[2]}</b>:
{data[3]}{subcategory}

🔷 <b>Работодатель</b>:
<code><b>{data[5]}</b></code>

🔷 <b>{data[6]}</b>
{adress}
🔷 <b>Оплата</b>:
{data[8]}

🔷 <b>График</b>:
{data[9]}

🔷 <b>Обязанности</b>:
{data[11]}

🔷 <b>Требования к кандидату</b>:
{data[12]}

🔷 <b>Дополнительные условия работы</b>:
{data[10]}

<code>{data[18]}</code>
"""
                post_id = data[0]
                if message_id is None:
                    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=await check_orders_kb(page, last_page, post_id))
                else:
                    await bot.edit_message_text(chat_id=message.from_user.id, text=text, message_id=message_id, reply_markup=await check_orders_kb(page, last_page, post_id))


@dp.callback_query_handler(text_contains='page_')
async def next_back_page_check(callback: types.CallbackQuery):
    data = (callback.data)[5:]
    await check_orders(callback, page=int(data), message_id=callback.message.message_id)

@dp.callback_query_handler(text_contains='check_')
async def approve_reject_post(callback: types.CallbackQuery):
    data = (callback.data)[6:]
    data = data.split('_')
    try:
        bool = (await db.Check_stat_moder(int(data[1])))[0]
    except:
        bool = True
    if bool:
        await callback.message.answer('📛 Данный заказ уже был проверен!')
        await check_orders(callback, message_id=callback.message.message_id)
    else:
        await db.approve_reject_post_id(oper_type=data[0], post_id=int(data[1]), moder_id=callback.message.chat.id)
        user_id = await db.select_order_user_id(int(data[1]))
        if data[0] == 'approve':
            await callback.message.answer('✅ Вы успешно одобрили публикацию!')
            await check_orders(callback, message_id=callback.message.message_id)
            await bot.send_message(chat_id=user_id[0], text=f'✅ Публикация вашего заказа была <b>завершена</b>!')
        else:
            await callback.message.answer('❌ Вы запретили публикацию!')
            await check_orders(message=callback, message_id=callback.message.message_id)
            await bot.send_message(chat_id=user_id[0], text=f'❌ Публикация вашего заказы была <b>отклонена</b>!')


@dp.message_handler(commands=['statistics'])
async def statistics_admin_panel(message: types.Message):
    if await db.check_user_in_db(message.from_user.id):
        data = await db.select_user_rights(message.from_user.id)
        if data[0] == 'admin':
            registered_users = await db.registered_users()
            create_orders = await db.all_orders()
            registered_executors = await db.registered_executors()
            registered_admins = await db.registered_admins()
            registered_moders = await db.registered_moders()
            public_orders = len(await db.search_orders(-99999))
            archive_orders = await db.all_archive_orders()
            moder_orders = len(await db.Dont_Check_orders())
            transactions_completed = await db.total_transactions_made()
            text = f"""
<b>📊 Статистика</b>

<b><i>👥 Пользователи:</i></b>
<i>👤 Зарегистрировано пользователей:</i> <code><b>{registered_users}</b></code>
<i>⚒️ Зарегистрировано исполнителей:</i> <code><b>{registered_executors}</b></code>
<i>👑 Администраторов:</i> <code><b>{registered_admins}</b></code>
<i>⚙️ Модераторов:</i> <code><b>{registered_moders}</b></code>

<b><i>📮 Объявления</i></b>
<i>🗂️ Созданных объявлений:</i> <code><b>{create_orders}</b></code>
<i>📰 Опубликовано объявлений:</i> <code><b>{public_orders}</b></code>
<i>🛠️ На модерации:</i> <code><b>{moder_orders}</b></code>
<i>🗃️ Объявлений в архиве:</i> <code><b>{archive_orders}</b></code>
<i>🤝 Совершено сделок:</i> <code><b>{transactions_completed}</b></code>
"""
            await message.answer(text)


@dp.message_handler(commands=['users'])
async def admin_panel_users(message: types.Message):
    if await db.check_user_in_db(message.from_user.id):
        data = await db.select_user_rights(message.from_user.id)
        if data[0] == 'admin':
            await message.answer('<b><i>👥 Выберите действие:</i></b>', reply_markup=admin_users_kb())


@dp.callback_query_handler(text='database_kings')
async def database_kings(callback: types.CallbackQuery):
    if await db.check_user_in_db(callback.from_user.id):
        data = await db.select_user_rights(callback.from_user.id)
        if data[0] == 'admin':
            admins, moders = await db.database_kings()
            ad = ''
            md = ''
            for i in admins:
                ad += f'\n@{i[0]}'
            for i in moders:
                md += f'\n@{i[0]}'

            if md == '':
                title = ''
            else:
                title = '<b><i>⚙️ Модераторы:</i></b>'
            text = f"""
<b><i>👑 Администраторы:</i></b>
{ad}

{title}
{md}
"""
            await callback.message.answer(text)

class Admin_change_Status(StatesGroup):
    user_id = State()

@dp.callback_query_handler(text='admin_change_status')
async def get_user_id(callback: types.CallbackQuery):
    if await db.check_user_in_db(callback.from_user.id):
        data = await db.select_user_rights(callback.from_user.id)
        if data[0] == 'admin':
            await Admin_change_Status.next()
            await callback.message.answer('<b><i>🔢 Введите id пользователя</i></b>\n\n<i>Пример:\n<code>980491704</code>\n<code>6194552812</code></i>', reply_markup=state_stop())

@dp.message_handler(state=Admin_change_Status.user_id)
async def text_user_id(message: types.Message, state: FSMContext):
    if await db.check_user_in_db(message.from_user.id):
        data_admin = await db.select_user_rights(message.from_user.id)
        if data_admin[0] == 'admin':
            try:
                async with state.proxy() as data:
                    data['user_id'] = int(message.text)
                data = await state.get_data()
                await state.finish()
                if await db.check_user_in_db(int(data['user_id'])):
                    if int(data['user_id']) == message.from_user.id and message.from_user.id != OWNER_ID:
                        await message.answer('<b>Вы не можете самостоятельно менять свой статус!</b>', reply_markup=await main_menu_kb(message.from_user.id))
                    else:
                        data_admin2 = await db.select_user_rights(int(data['user_id']))
                        if data_admin2[0] == 'admin' and message.from_user.id != OWNER_ID:
                            await message.answer('<b>Только ВЛАДЕЛЕЦ может изменять статус других администраторов!</b>', reply_markup=await main_menu_kb(message.from_user.id))
                        else:
                            await message.answer(f"<b>💠 Укажите статус для пользователя <code>{data['user_id']}</code></b>", reply_markup=await admin_user_change_status(data['user_id']))
                else:
                    await Admin_change_Status.user_id.set()
                    await message.reply('Пользователь не найден в базе.', reply_markup=state_stop())
            except:
                await Admin_change_Status.user_id.set()
                await message.reply('Введите число.', reply_markup=state_stop())

@dp.callback_query_handler(text_contains='change_status_')
async def change_stat(callback: types.CallbackQuery):
    if await db.check_user_in_db(callback.from_user.id):
        data_admin = await db.select_user_rights(callback.from_user.id)
        if data_admin[0] == 'admin':
            data = ((callback.data)[14:]).split('_')
            await db.change_status(int(data[1]), data[0])
            await bot.send_message(chat_id=data[1], text=f'📝 Ваши права были изменены на <code>{data[0]}</code>')
            await bot.delete_message(message_id=callback.message.message_id, chat_id=callback.from_user.id)
            await callback.message.answer(f'✅ Права пользователя <code>{data[1]}</code> были успешно изменены на <code>{data[0]}</code>', reply_markup=await main_menu_kb(callback.from_user.id))


@dp.message_handler(content_types=['text'])
async def redirection(message: types.Message):
    if message.text == '😎 Профиль':
        await profile(message)
    elif message.text == '🤝 Реферальная система':
        await referal_url(message)
    elif message.text =='🌟 Создать заказ':
        await create_order(message)
    elif message.text =='🔎 Заказы':
        await search_orders(message)
    elif message.text == '🗂️ Мои заказы':
        await my_orders(message)
    elif message.text == '🗃️ Архив':
        await archive_orders_user(message)
    elif message.text == '💼 В работе':
        await orders_in_work(message)
    elif message.text == '🤚 Отклики':
        await responses_user(message)
    elif message.text == '🛠️ Пользователи':
        await admin_panel_users(message)
    elif message.text == '🗂️ Проверка заказов':
        await check_orders(message)
    elif message.text == '📊 Статистика':
        await statistics_admin_panel(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)