use crate::data_format::{ResponseCreateResult, ResponseDatabases, ResponseInitData, ResponseTables, ResponseSelectSqlitePath, ResponseSelectSavePath,ResponseOpenFileFolder};
use crate::service::{
    create_mysql_model, create_sqlite_model, get_mysql_databases, get_mysql_tables,
    get_sqlite_tables, init_data,
    get_sqlite_file, get_save_path,open_file_folder
};
use tauri::AppHandle;
// 初始化数据
#[tauri::command]
pub async fn api_init_data() -> ResponseInitData {
    init_data().await
}
// 获取mysql数据库
#[tauri::command]
pub async fn api_get_mysql_databases(host: String, port: String, user_name: String, password: String, ) -> ResponseDatabases {
    get_mysql_databases(&host, &port, &user_name, &password).await
}
// 获取mysql数据表
#[tauri::command]
pub async fn api_get_mysql_tables(host: String, port: String, user_name: String, password: String, db_name: String, ) -> ResponseTables {
    get_mysql_tables(&host, &port, &user_name, &password, &db_name).await
}
// 获取sqlite数据表
#[tauri::command]
pub async fn api_get_sqlite_tables(db_file_path: String) -> ResponseTables {
    get_sqlite_tables(&db_file_path).await
}
// 生成mysql模型文件
#[tauri::command]
pub async fn api_create_mysql_model(host: String, port: String, user_name: String, password: String, db_name: String, tables: Vec<String>, out_file: String, ) -> ResponseCreateResult {
    create_mysql_model(
        &host, &port, &user_name, &password, &db_name, tables, &out_file,
    )
    .await
}
// 生成sqlite模型文件
#[tauri::command]
pub async fn api_create_sqlite_model(db_file_path: String, tables: Vec<String>, out_file: String, ) -> ResponseCreateResult {
    create_sqlite_model(&db_file_path, tables, &out_file).await
}
#[tauri::command]
pub async fn api_get_sqlite_file(app: AppHandle) -> ResponseSelectSqlitePath {
    get_sqlite_file(&app).await
}
// 选择保存路径
#[tauri::command]
pub async fn api_select_file_save_path(app: AppHandle) -> ResponseSelectSavePath {
    get_save_path(&app).await
}
// 打开输出文件所在目录
#[tauri::command]
pub async fn api_open_file_folder(file_path: String) -> ResponseOpenFileFolder {
    open_file_folder(&file_path).await
}