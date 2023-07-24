

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from psycopg2.extras import execute_values

from config.bot import database

class Database():
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                user=database['user'],
                password=database['password'],
                host=database['host'],
                port="5432",
                database=database['db_name']
            )
            self.connection.autocommit = True
            self.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor = self.connection.cursor()
            try:
                self.cursor.execute(f"CREATE DATABASE {database['db_name']}")
            except (Exception, Error) as error:
                print("[ERROR] Ошибка при работе с PostgreSQL", error)

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY NOT NULL,
            user_id BIGINT NOT NULL,
            name VARCHAR NOT NULL,
            photo TEXT NOT NULL,
            years INT NOT NULL,
            city VARCHAR DEFAULT NULL,
            referal_id BIGINT DEFAULT NULL,
            requisites TEXT DEFAULT NULL,
            rights VARCHAR DEFAULT 'user',
            ban BOOL DEFAULT False,
            username VARCHAR NOT NULL,
            transactions_completed INT DEFAULT 0,
            balance INT DEFAULT 0,
            premium BIGINT DEFAULT 0,
            timestamp timestamp default current_timestamp
            )""")

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY NOT NULL,
            user_id BIGINT NOT NULL,
            title TEXT NOT NULL,
            category TEXT DEFAULT NULL,
            subcategory TEXT DEFAULT NULL,
            company TEXT DEFAULT NULL,
            format_job TEXT DEFAULT NULL,
            adress TEXT DEFAULT NULL,
            cost TEXT DEFAULT NULL,
            deadlines TEXT DEFAULT NULL,
            additionally TEXT DEFAULT NULL,
            duties TEXT DEFAULT NULL,
            requirements TEXT DEFAULT NULL,
            views INT DEFAULT 0,
            moderator BIGINT DEFAULT NULL,
            moder_check BOOL DEFAULT False,
            ban BOOL DEFAULT False,
            public BOOL DEFAULT False,
            timestamp timestamp default current_timestamp,
            completed BOOL DEFAULT False,
            executor_id BIGINT DEFAULT NULL,
            username_customer TEXT NOT NULL
            )""")

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS responses (
            id SERIAL PRIMARY KEY NOT NULL,
            user_id BIGINT NOT NULL,
            order_id INT NOT NULL,
            timestamp timestamp default current_timestamp
            )""")

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY NOT NULL,
            category_name TEXT NOT NULL,
            title TEXT NOT NULL
            )""")


            self.cursor.execute("SELECT version();")
            record = self.cursor.fetchone()
            print("Вы подключены к - ", record, "\n")

        except (Exception, Error) as error:
            print("[ERROR] Ошибка при работе с PostgreSQL", error)

    async def select_categories(self, title):
        with self.connection:
            self.cursor.execute(f"SELECT category_name FROM categories WHERE title = '{title}'")
            return self.cursor.fetchall()

    async def select_categories_data(self, title):
        with self.connection:
            self.cursor.execute(f"SELECT id, category_name FROM categories WHERE title = '{title}'")
            return self.cursor.fetchall()

    async def select_title_for_catid(self, cat_id):
        with self.connection:
            self.cursor.execute(f"SELECT title FROM categories WHERE id = {cat_id}")
            return self.cursor.fetchone()

    async def select_all_AdminsAndModers(self):
        with self.connection:
            self.cursor.execute(f"SELECT user_id FROM users WHERE rights='admin' OR rights='moder'")
            return self.cursor.fetchall()

    async def check_user_in_db(self, user_id):
        with self.connection:
            try:
                self.cursor.execute(f"""SELECT * FROM users WHERE user_id = {user_id}""")
                return bool(self.cursor.fetchone())
            except:
                return False

    async def insert_user(self, user_id, data, username, rights = 'user'):
        with self.connection:
            name = data['name']
            years = data['years']
            photo = data['photo']
            city = data['city']
            ref_id = data['ref_id']
            self.cursor.execute(f"INSERT INTO users (user_id, name, years, photo, city, username, rights, referal_id) VALUES ({user_id}, '{name}', {years}, '{photo}', '{city}', '{username}', '{rights}', {ref_id})")


    async def select_user(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}")
            return self.cursor.fetchone()

    async def select_transactions_completed(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT transactions_completed FROM users WHERE user_id = {user_id}")
            return self.cursor.fetchone()

    async def update_transactions_completed(self, user_id, rep):
        with self.connection:
            self.cursor.execute(f"UPDATE users SET transactions_completed = {rep} WHERE user_id = {user_id}")

    async def count_referals(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT user_id FROM users WHERE referal_id = {user_id}")
            return len(self.cursor.fetchall())

    async def update_profile(self, user_id = None, name = None, years = None, city = None, photo = None):
        if not name is None:
            with self.connection:
                self.cursor.execute(f"UPDATE users SET name = '{name}' WHERE user_id = {user_id}")
        elif not years is None:
            with self.connection:
                self.cursor.execute(f"UPDATE users SET years = {years} WHERE user_id = {user_id}")
        elif not city is None:
            with self.connection:
                self.cursor.execute(f"UPDATE users SET city = '{city}' WHERE user_id = {user_id}")
        elif not photo is None:
            with self.connection:
                self.cursor.execute(f"UPDATE users SET photo = '{photo}' WHERE user_id = {user_id}")

    async def update_rights(self, user_id, rights):
        with self.connection:
            self.cursor.execute(f"UPDATE users SET rights = '{rights}' WHERE user_id = {user_id}")

    async def insert_order(self, user_id, data, username):
        with self.connection:
            self.cursor.execute(f"INSERT INTO orders (user_id, title, category, subcategory, company, format_job, adress, cost, deadlines, additionally, duties, requirements, username_customer) VALUES ({user_id}, '{data['title']}', '{data['category']}', '{data['subcategory']}', '{data['company']}', '{data['format_job']}', '{data['adress']}', '{data['cost']}', '{data['deadlines']}', '{data['additionally']}', '{data['duties']}', '{data['requirements']}', '{username}')")


    async def Dont_Check_orders(self):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM orders WHERE moder_check = False")
            return self.cursor.fetchall()

    async def Check_stat_moder(self, id):
        with self.connection:
            self.cursor.execute(f"SELECT moder_check FROM orders WHERE id = {id}")
            return self.cursor.fetchone()

    async def select_user_rights(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT rights FROM users WHERE user_id = {user_id}")
            return self.cursor.fetchone()

    async def approve_reject_post_id(self, oper_type, post_id, moder_id):
        if oper_type == 'approve':
            with self.connection:
                self.cursor.execute(f"UPDATE orders SET moder_check = True, public = True, moderator = {int(moder_id)} WHERE id = {int(post_id)}")
        elif oper_type == 'reject':
            with self.connection:
                self.cursor.execute(f"UPDATE orders SET moder_check = True, public = False, ban = True, moderator = {int(moder_id)} WHERE id = {int(post_id)}")


    async def search_orders(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM orders WHERE moder_check = True AND ban = False AND public = True AND user_id != {user_id}")
            return self.cursor.fetchall()

    async def check_responses_on_order_user(self, user_id, order_id):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM responses WHERE user_id = {user_id} AND order_id = {order_id}")
            return bool(self.cursor.fetchone())

    async def insert_response(self, user_id, order_id):
        with self.connection:
            self.cursor.execute(f"INSERT INTO responses (user_id, order_id) VALUES ({user_id}, {order_id})")

    async def orders_user(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM orders WHERE user_id = {user_id} AND public = True")
            return self.cursor.fetchall()

    async def select_order_for_id(self, order_id):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM orders WHERE id = {order_id}")
            return self.cursor.fetchone()

    async def select_all_responses_order(self, orders_id):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM responses WHERE order_id = {orders_id}")
            return self.cursor.fetchall()

    async def select_order_user_id(self, order_id):
        with self.connection:
            self.cursor.execute(f"SELECT user_id FROM orders WHERE id = {order_id}")
            return self.cursor.fetchone()

    async def archive_order(self, order_id):
        with self.connection:
            self.cursor.execute(f"UPDATE orders SET public = False WHERE id = {order_id}")

    async def order(self, order_id):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM orders WHERE id = {order_id}")
            return self.cursor.fetchone()

    async def select_executor_order(self, order_id):
        with self.connection:
            self.cursor.execute(f"SELECT executor_id FROM orders WHERE id = {order_id}")
            return self.cursor.fetchone()

    async def update_executor_id_order(self, user_id, order_id):
        with self.connection:
            self.cursor.execute(f"UPDATE orders SET executor_id = {user_id}, public = False WHERE id = {order_id}")

    async def del_update_executor_id_order(self, order_id):
        with self.connection:
            self.cursor.execute(f"UPDATE orders SET executor_id = NULL, public = True WHERE id = {order_id}")

    async def select_user_rep_executor(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT executor_rank FROM users WHERE user_id = {user_id}")
            return self.cursor.fetchone()

    async def delete_respons_user(self, user_id, order_id):
        with self.connection:
            self.cursor.execute(f"DELETE FROM responses WHERE user_id = {user_id} AND order_id = {order_id}")

    async def orders_in_progress(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM orders WHERE executor_id = {user_id} AND completed = False")
            return self.cursor.fetchall()

    async def get_username(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT username FROM users WHERE user_id = {user_id}")
            return self.cursor.fetchone()

    async def completed_order(self, order_id):
        with self.connection:
            self.cursor.execute(f"UPDATE orders SET completed = True WHERE id = {order_id}")

    async def select_all_responses_user(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM responses WHERE user_id = {user_id}")
            return self.cursor.fetchall()

    async def check_ref_user(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT referal_id FROM users WHERE user_id = {user_id}")
            return self.cursor.fetchone()

    async def update_ref_id(self, user_id, ref_id):
        with self.connection:
            self.cursor.execute(f"UPDATE users SET referal_id = {ref_id} WHERE user_id = {user_id}")

    async def select_archive_orders_user(self, user_id):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM orders WHERE user_id = {user_id} AND public = False")
            return self.cursor.fetchall()

    async def public_order(self, order_id):
        with self.connection:
            self.cursor.execute(f"UPDATE orders SET public = True WHERE id = {order_id}")





    ### СТАТИСТИКА


    async def registered_users(self):
        with self.connection:
            self.cursor.execute("SELECT id FROM users")
            return len(self.cursor.fetchall())

    async def registered_executors(self):
        with self.connection:
            self.cursor.execute("SELECT id FROM users WHERE rights = 'user'")
            return len(self.cursor.fetchall())

    async def registered_admins(self):
        with self.connection:
            self.cursor.execute("SELECT id FROM users WHERE rights = 'admin'")
            return len(self.cursor.fetchall())

    async def registered_moders(self):
        with self.connection:
            self.cursor.execute("SELECT id FROM users WHERE rights = 'moder'")
            return len(self.cursor.fetchall())

    async def all_orders(self):
        with self.connection:
            self.cursor.execute("SELECT id FROM orders")
            return len(self.cursor.fetchall())

    async def all_archive_orders(self):
        with self.connection:
            self.cursor.execute("SELECT id FROM orders WHERE public = False")
            return len(self.cursor.fetchall())

    async def total_transactions_made(self):
        with self.connection:
            self.cursor.execute("SELECT transactions_completed FROM users")
            count = 0
            for i in self.cursor.fetchall():
                count += int(i[0])
            return count

    async def database_kings(self):
        with self.connection:
            self.cursor.execute("SELECT username FROM users WHERE rights = 'admin'")
            admins = self.cursor.fetchall()
            self.cursor.execute("SELECT username FROM users WHERE rights = 'moder'")
            moders = self.cursor.fetchall()
            return admins, moders

    async def change_status(self, user_id, status):
        with self.connection:
            self.cursor.execute(f"UPDATE users SET rights = '{status}' WHERE user_id = {user_id}")