import service
class Api:
    def __init__(self):
        self._window = None
    def init(self) -> dict:
        return service.service_init()
    def connect_mysql(self,host: str, port: str, user_name: str, password: str) -> dict:
        return service.service_connect_mysql(host, port, user_name, password)
    def get_mysql_table(self, host: str, port: str, user_name: str, password: str, database_name: str) -> dict:
        return service.service_get_mysql_table(host, port, user_name, password, database_name)
    def connect_sqlite(self):
        return service.service_connect_sqlite(self._window)
    def get_sqlite_table(self, database_file: str) -> dict:
        return service.service_get_sqlite_table(database_file)
    def select_output_file(self):
        return service.service_select_output_file(self._window)
    def create_mysql_model(self, host: str, user_name: str, password: str, database_name: str, table_name_list: list, output_file:str) -> dict:
        return service.service_create_mysql_model(host, user_name, password, database_name, table_name_list, output_file)
    def create_sqlite_model(self, database_file: str, table_name_list: list, output_file:str) -> dict:
        return service.service_create_sqlite_model(database_file, table_name_list, output_file)
    def open_output_folder(self,output_file):
        return service.service_open_output_folder(output_file)