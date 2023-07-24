

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from config.database import Database

db = Database()

def start_kb():
    Start_kb = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton('🔍 Поиск', callback_data='start_registration'),
        InlineKeyboardButton('📮 Публикация', callback_data='start_create_order')
    ]
    Start_kb.add(*buttons)
    return Start_kb


def state_stop():
    State_Stop = ReplyKeyboardMarkup(resize_keyboard=True)
    State_Stop.add(KeyboardButton(text='❌ Отменить'))
    return State_Stop

def get_location():
    GetLoc = ReplyKeyboardMarkup(resize_keyboard=True)
    GetLoc.add(KeyboardButton('🌍 Отправить 🌏', request_location=True))
    GetLoc.add(KeyboardButton(text='❌ Отменить'))
    return GetLoc

def profile_kb():
    Profile = InlineKeyboardMarkup()
    Profile.add(InlineKeyboardButton(text='✏️ Редактировать профиль', callback_data='edit_profile'))
    return Profile

def edit_my_profile_kb():
    Edit = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text='👤 Имя', callback_data='edit_name'),
        InlineKeyboardButton(text='🔢 Возраст', callback_data='edit_years'),
        InlineKeyboardButton(text='🌐 Город', callback_data='edit_city'),
        InlineKeyboardButton(text='📸 Фото', callback_data='edit_photo')
    ]
    Edit.add(*buttons)
    return Edit

async def main_menu_kb(user_id):
    Main_Menu = ReplyKeyboardMarkup(resize_keyboard=True)
    if await db.check_user_in_db(user_id):
        buttons = [
            KeyboardButton(text='😎 Профиль'),
            KeyboardButton(text='🔎 Заказы'),
            KeyboardButton(text='🌟 Создать заказ'),
            KeyboardButton(text='🗂️ Мои заказы'),
            KeyboardButton(text='🗃️ Архив'),
            KeyboardButton(text='💼 В работе'),
            KeyboardButton(text='🤚 Отклики'),
            KeyboardButton(text='🤝 Реферальная система')
        ]
    else:
        buttons = [
            KeyboardButton(text='🌟 Создать заказ'),
            KeyboardButton(text='🗂️ Мои заказы'),
            KeyboardButton(text='🗃️ Архив')
        ]
    Main_Menu.add(*buttons)
    if await db.check_user_in_db(user_id):
        data = await db.select_user_rights(user_id)
        if data[0] == 'admin':
            Main_Menu.add(KeyboardButton(text='🔽 Команды Администратора 🔽'))
            buttons = [
                KeyboardButton(text='🛠️ Пользователи'),
                KeyboardButton(text='🗂️ Проверка заказов'),
                KeyboardButton(text='📊 Статистика')
            ]
            Main_Menu.add(*buttons)
    return Main_Menu

def create_order_title():
    TOrder = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton(text='Вакансия'),
        KeyboardButton(text='Подработка/задача')
    ]
    TOrder.add(*buttons)
    TOrder.add(KeyboardButton(text='❌ Отменить'))
    return TOrder

async def create_order_category(title):
    COrder = ReplyKeyboardMarkup()
    data = await db.select_categories(title)
    for i in data:
        COrder.add(KeyboardButton(text=i[0]))
    COrder.add(KeyboardButton(text='Другое'))
    COrder.add(KeyboardButton(text='❌ Отменить'))
    return COrder

async def job_format(data):
    JFOrder = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton(text='Онлайн'),
        KeyboardButton(text='Оффлайн')
    ]

    if data == 'Вакансия':
        buttons.append(KeyboardButton(text='Гибрид'))

    JFOrder.add(*buttons)
    JFOrder.add(KeyboardButton(text='❌ Отменить'))
    return JFOrder

async def check_orders_kb(page, last_page, post_id):
    C_Orders = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text='✅ Одобрить', callback_data=f'check_approve_{post_id}'),
        InlineKeyboardButton(text='❌ Отклонить', callback_data=f'check_reject_{post_id}')
    ]
    C_Orders.add(*buttons)

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text='◀️ Назад', callback_data=f'page_{int(page)-1}'))
    if page >= 0 and not last_page:
        buttons.append(InlineKeyboardButton(text='Дальше ▶️', callback_data=f'page_{int(page)+1}'))
    C_Orders.add(*buttons)

    return C_Orders

async def search_orders_kb(page, last_page, post_id):
    S_Orders = InlineKeyboardMarkup(row_width=2)
    S_Orders.add(InlineKeyboardButton(text='🤚 Откликнуться', callback_data=f'respond_{post_id}'))

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text='◀️ Назад', callback_data=f'search_pg_{int(page) - 1}'))
    if page >= 0 and not last_page:
        buttons.append(InlineKeyboardButton(text='Дальше ▶️', callback_data=f'search_pg_{int(page) + 1}'))
    S_Orders.add(*buttons)

    return S_Orders


async def My_orders_kb(page, last_page, post_id):
    M_Orders = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text='🤚 Отклики', callback_data=f'responsed_{post_id}'),
        InlineKeyboardButton(text='🗃️ В архив', callback_data=f'archive_{post_id}_{page}')
    ]
    M_Orders.add(*buttons)

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text='◀️ Назад', callback_data=f'morders_pg_{int(page) - 1}'))
    if page >= 0 and not last_page:
        buttons.append(InlineKeyboardButton(text='Дальше ▶️', callback_data=f'morders_pg_{int(page) + 1}'))

    M_Orders.add(*buttons)
    return M_Orders

async def responsed_order_kb(page, last_page, order_id, user_id):
    R_Orders = InlineKeyboardMarkup(row_width=2)

    buttons = [
        InlineKeyboardButton(text='💼 Выбрать', callback_data=f'respons_true_{user_id}_{order_id}')
    ]
    R_Orders.add(*buttons)

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text='◀️ Назад', callback_data=f'rorder_pg_{int(page) - 1}_{order_id}'))
    if page >= 0 and not last_page:
        buttons.append(InlineKeyboardButton(text='Дальше ▶️', callback_data=f'rorder_pg_{int(page) + 1}_{order_id}'))

    R_Orders.add(*buttons)
    return R_Orders

async def ready_order(data):
    R_Order = InlineKeyboardMarkup()

    executor_id = data[0]
    order_id = data[1]
    user_id = data[2]

    buttons = [
        InlineKeyboardButton(text='📊 Начнём 📈', callback_data=f'ready_order_true_{executor_id}_{order_id}_{user_id}'),
        InlineKeyboardButton(text='😔 В другой раз 😥', callback_data=f'ready_order_false_{executor_id}_{order_id}_{user_id}')
    ]

    R_Order.add(*buttons)
    return R_Order


async def work_orders_kb(page, last_page, order_id, username):
    W_Orders = InlineKeyboardMarkup(row_width=2)

    buttons = [
        InlineKeyboardButton(text='✅ Выполнено', callback_data=f'work_answer_true_{order_id}'),
        InlineKeyboardButton(text='❌ Отказаться', callback_data=f'work_answer_false_{order_id}'),
        InlineKeyboardButton(text='👤 Заказчик', url=f'https://t.me/{username}')
    ]
    W_Orders.add(*buttons)

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text='◀️ Назад', callback_data=f'work_pg_{int(page) - 1}'))
    if page >= 0 and not last_page:
        buttons.append(InlineKeyboardButton(text='Дальше ▶️', callback_data=f'work_pg_{int(page) + 1}'))

    W_Orders.add(*buttons)
    return W_Orders

def answer_work_true(order_id):
    AW_Order = InlineKeyboardMarkup(row_width=2)

    buttons = [
        InlineKeyboardButton(text='✅ Подтвердить', callback_data=f'work_completed_true_{order_id}'),
        InlineKeyboardButton(text='❌ Опровергнуть', callback_data=f'work_completed_false_{order_id}')
    ]

    AW_Order.add(*buttons)
    return AW_Order

async def responsed_kb(page, last_page, post_id, user_id):
    R_Orders = InlineKeyboardMarkup(row_width=2)

    R_Orders.add(InlineKeyboardButton(text='❌ Отменить', callback_data=f'order_respo_{post_id}_{user_id}_{int(page)}'))

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text='◀️ Назад', callback_data=f'order_respons_pg_{int(page) - 1}'))
    if page >= 0 and not last_page:
        buttons.append(InlineKeyboardButton(text='Дальше ▶️', callback_data=f'order_respons_pg_{int(page) + 1}'))

    R_Orders.add(*buttons)
    return R_Orders

async def add_referal(user_id):
    check = await db.check_ref_user(user_id)
    if int(check[0]) != 0:
        pass
    else:
        AR_user = InlineKeyboardMarkup()
        AR_user.add(InlineKeyboardButton(text='🍉 Стать рефералом 🍎', callback_data='add_referal'))
        return AR_user

async def Archive_orders_kb(page, last_page, post_id):
    A_Orders = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text='📰 Опубликовать', callback_data=f'public_{post_id}_{page}')
    ]
    A_Orders.add(*buttons)

    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(text='◀️ Назад', callback_data=f'archive_orders_pg_{int(page) - 1}'))
    if page >= 0 and not last_page:
        buttons.append(InlineKeyboardButton(text='Дальше ▶️', callback_data=f'archive_orders_pg_{int(page) + 1}'))

    A_Orders.add(*buttons)
    return A_Orders

def me_kb():
    me = InlineKeyboardMarkup()
    me.add(InlineKeyboardButton(text='ВКонтакте', url='https://vk.com/earneasybot'))
    return me

def admin_users_kb():
    Admin_U = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text='🗄️ База данных ☢️', callback_data='database_users'),
        InlineKeyboardButton(text='📊 Изменить статус', callback_data='admin_change_status'),
        InlineKeyboardButton(text='👑 Короли', callback_data='database_kings'),
        InlineKeyboardButton(text='🚫 Бан ☢️', callback_data='database_admin_ban')
    ]
    Admin_U.add(*buttons)
    return Admin_U

async def admin_user_change_status(user_id):
    AD_CST = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text='👑 Админ', callback_data=f'change_status_admin_{user_id}'),
        InlineKeyboardButton(text='⚙️ Модер', callback_data=f'change_status_moder_{user_id}'),
        InlineKeyboardButton(text='👤 Пользователь', callback_data=f'change_status_user_{user_id}')
    ]
    AD_CST.add(*buttons)
    return AD_CST




