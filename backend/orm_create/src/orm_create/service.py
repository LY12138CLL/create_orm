import pymysql
import sqlite3
import webview
from typing import Optional, List
from sqlalchemy import create_engine, MetaData
# 生成orm模型代码
def generate_orm_code( db_url: str, tables: Optional[List[str]] = None) -> str:
    """
    直接使用 DeclarativeGenerator 在内存中为指定表生成 ORM 代码字符串。

    :param db_url: 数据库连接字符串
    :param tables: 要生成的表名列表。为 None 时生成所有表。
    :return: 生成的 Python 代码字符串
    """
    from sqlacodegen.generators import DeclarativeGenerator
    try:
        engine = create_engine(db_url)
        metadata = MetaData()

        # 核心改动在这里：将 tables 列表传递给 only 参数
        if tables:
            metadata.reflect(bind=engine, only=tables)
        else:
            metadata.reflect(bind=engine)  # 不指定则反射所有表

        generator = DeclarativeGenerator(metadata, engine, set())
        return generator.generate()
    except:
        return None
# 生成py文件
def generate_file( file_path: str, code: str) -> bool:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        return True
    except:
        return False


# 初始化
def service_init():
    return {
        'message': 'success',
        'data': {
            'dataBaseType': ['MySQL', 'Sqlite'],
            'host': 'localhost',
            'port': '3306',
            'userName': 'root',
            'outFile': r'C:\\Users\\Administrator\\Desktop\\models.py',
        }
    }
# 连接mysql数据库
def service_connect_mysql(host: str, port: str, user_name: str, password: str) -> dict:
    conn = None
    # MySQL 自带的系统库
    SYSTEM_DBS = {'information_schema', 'mysql', 'performance_schema', 'sys'}
    try:
        conn = pymysql.connect(
            host=host,
            port=int(port),
            user=user_name,
            password=password,
            charset='utf8mb4',
            connect_timeout=5,
        )
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA "
                "ORDER BY SCHEMA_NAME"
            )
            dbs = [row[0] for row in cursor.fetchall()]
        dbs = [db for db in dbs if db not in SYSTEM_DBS]
        result = {
            'message': 'success',
            'data': {
                'dataBaseList': dbs
            },
        }
    except pymysql.MySQLError as e:
        result = {
            'message': 'fail',
            'data': {},
        }
    finally:
        if conn:
            conn.close()
        return result
# 获取mysql数据库表
def service_get_mysql_table(host: str, port: str, user_name: str, password: str, database_name: str) -> dict:
    conn = pymysql.connect(
        host=host,
        port=int(port),
        user=user_name,
        password=password,
        database=database_name,
        charset='utf8mb4',
        connect_timeout=5,
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
        result = {
            'message': 'success',
            'data': {
                'dataBaseTableList': tables
            }
        }
    except:
        result = {
            'message': 'fail',
            'data': {}
        }
    finally:
        conn.close()
        return result
# 连接sqlite数据库
def service_connect_sqlite(window) -> dict:
    # 定义文件类型过滤器
    file_types = ('SSQLite Database (*.db;*.sqlite;*.sqlite3)',)
    # 调用 create_file_dialog，指定对话框类型为 OPEN_DIALOG
    result = window.create_file_dialog(
        webview.OPEN_DIALOG,  # 对话框类型：打开文件
        allow_multiple=False,  # 是否允许选择多个文件
        file_types=file_types  # 文件类型过滤
    )
    if result:
        selected_file = result[0]  # 返回的是一个元组，取第一个文件
        result = {
            'message': 'success',
            'data': {
                'databaseFile': selected_file,
            }
        }
    else:
        result = {
            'message': 'fail',
            'data': {}
        }
    return result
# 获取sqlite数据库表
def service_get_sqlite_table(database_file: str) -> dict:
    try:
        with sqlite3.connect(database_file) as conn:
            cursor = conn.execute("""
              SELECT name
              FROM sqlite_master
              WHERE type = 'table'
                AND name NOT LIKE 'sqlite_%'
              ORDER BY name
              """)
            tables = [row[0] for row in cursor]
        result = {
            'message': 'success',
            'data': {
                'dataBaseTableList': tables
            }
        }
    except:
        result = {
            'message': 'fail',
            'data': {}
        }
    return result
# 选择输出文件
def service_select_output_file(window) -> dict:
    file_types = ('Python Files (*.py)',)
    result = window.create_file_dialog(
        webview.FileDialog.SAVE,
        save_filename='model.py',
        file_types=file_types
    )
    # 处理返回结果
    if result:
        selected_file = result[0]  # 返回的是一个元组，取第一个文件
    else:
        selected_file = ''
    result = {
        'message': 'success',
        'data': {
            'outputFile': selected_file,
        }
    }
    return result
# 生成mysql数据库模型
def service_create_mysql_model(host: str, user_name: str, password: str, database_name: str, table_name_list: list, output_file:str) -> dict:
    db_url = f"mysql+pymysql://{user_name}:{password}@{host}/{database_name}"
    code = generate_orm_code(db_url,table_name_list)
    if code:
        generate_result = generate_file(output_file, code)
        if generate_result:
            result = {
                'message': 'success',
                'data': {
                    'outputFile': output_file,
                }
            }
            return result
    result = {
        'message': 'fail',
        'data': {}
    }
    return result
# 生成sqlite数据库模型
def service_create_sqlite_model(database_file: str, table_name_list: list, output_file:str) -> dict:
    db_url = f"sqlite:///{database_file}"
    code = generate_orm_code(db_url, table_name_list)
    if code:
        generate_result = generate_file(output_file, code)
        if generate_result:
            result = {
                'message': 'success',
                'data': {
                    'outputFile': output_file,
                }
            }
            return result
    result = {
        'message': 'fail',
        'data': {}
    }
    return result
# 打开输出目录定位到输出文件
def service_open_output_folder(output_file:str) -> dict:
    import os
    import subprocess
    # 检查文件是否存在
    if not os.path.exists(output_file):
        result = {
        'message': 'fail',
        'data': {}
    }
        return result
    # 规范化为绝对路径（处理斜杠、相对路径等）
    abs_path = os.path.abspath(output_file)

    # 调用 explorer /select 命令，/select 后路径必须用英文双引号包裹
    subprocess.run(f'explorer /select,"{abs_path}"', shell=True)
    result = {
        'message': 'success',
        'data': {
            'outputFile': output_file,
        }
    }
    return result
