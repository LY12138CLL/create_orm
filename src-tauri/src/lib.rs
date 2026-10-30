mod api;
mod data_format;
mod service;
use crate::api::{
    api_create_mysql_model, api_create_sqlite_model, api_get_mysql_databases, api_get_mysql_tables,
    api_get_sqlite_tables, api_init_data,api_get_sqlite_file,api_select_file_save_path,api_open_file_folder
};

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            api_init_data,
            api_get_mysql_databases,
            api_get_mysql_tables,
            api_get_sqlite_tables,
            api_create_mysql_model,
            api_create_sqlite_model,
            api_get_sqlite_file,
            api_select_file_save_path,
            api_open_file_folder
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
