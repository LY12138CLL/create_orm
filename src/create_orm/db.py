"""数据库连接串构造与库/表元数据加载。"""

from urllib.parse import quote_plus

from sqlalchemy import create_engine, inspect, text


def build_db_url(db_type, params):
    if db_type == "SQLite":
        path = params.get("database", "").strip()
        if not path:
            raise ValueError("请选择 SQLite 数据库文件")
        return "sqlite:///" + path.replace("\\", "/")

    host = params.get("host", "").strip()
    port = params.get("port", "").strip() or "3306"
    user = params.get("user", "").strip()
    password = params.get("password", "")
    database = params.get("database", "").strip()

    if not host:
        raise ValueError("请填写主机地址")
    if not user:
        raise ValueError("请填写用户名")
    if not database:
        raise ValueError("请选择数据库")

    # 用户名/密码可能包含 @ : # % 等字符，必须编码后再拼进连接串
    return (f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
            f"@{host}:{port}/{database}?charset=utf8mb4")


def build_server_url(params):
    host = params.get("host", "").strip()
    port = params.get("port", "").strip() or "3306"
    user = params.get("user", "").strip()
    password = params.get("password", "")
    if not host:
        raise ValueError("请填写主机地址")
    if not user:
        raise ValueError("请填写用户名")
    return (f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
            f"@{host}:{port}/")


def load_tables(db_url):
    engine = create_engine(db_url)
    try:
        return inspect(engine).get_table_names()
    finally:
        engine.dispose()


def load_databases(server_url):
    engine = create_engine(server_url)
    try:
        with engine.connect() as conn:
            return [row[0] for row in conn.execute(text("SHOW DATABASES"))]
    finally:
        engine.dispose()