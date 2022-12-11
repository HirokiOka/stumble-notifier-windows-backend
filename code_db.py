import os
from dotenv import load_dotenv
import sqlalchemy as sa

load_dotenv()
driver = os.getenv('DEV_DRIVER')
user = os.getenv('DEV_USER')
password = os.getenv('DEV_PASSWORD')
host = os.getenv('DEV_HOST')
port = os.getenv('DEV_PORT')
db_name = os.getenv('DEV_DBNAME')


def connect_db():
    conn = sa.create_engine(f'{driver}://{user}:{password}@{host}:{port}/{db_name}')
    return conn


def get_all_data(conn):
    query = 'SELECT * FROM exelog'
    rows = conn.execute(query)
    return rows


def get_unique_users(conn):
    query = 'SELECT userid FROM exelog'
    row_data = conn.execute(query)
    users = [x[0] for x in row_data]
    unique_users = list(set(users))
    return unique_users


def get_code_params(conn, user_id):
    query = f'SELECT executedAt, sloc, ted FROM exelog WHERE userid={user_id}'
    code_params = conn.execute(query)
    return code_params


def get_source_code(conn, user_id, executed_time):
    query = f"SELECT sourceCode FROM exelog\
              WHERE userid={user_id} and executedAt='{executed_time}'"
    row_data = conn.execute(query)
    source_code = [x[0] for x in row_data][0]
    return source_code


def get_latest_params(conn, user_id):
    query = f'SELECT executedAt, sloc, ted FROM exelog\
              WHERE userid={user_id} ORDER BY executedAt DESC LIMIT 1'
    latest_executed_date = conn.execute(query)
    result = [x[0] for x in latest_executed_date]
    return result


"""
conn = connect_db()
data = get_latest_params(conn, 1)
print(data)
"""
