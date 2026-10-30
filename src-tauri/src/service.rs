use crate::data_format::{
    CreateResultData, Databaes, DatabaseName, InitData, ResponseCreateResult, ResponseDatabases,
    ResponseInitData, ResponseTables, TableName, Tables,
    ResponseSelectSqlitePath, SelectSqlitePath,
    ResponseSelectSavePath, SelectSavePath,
    ResponseOpenFileFolder
};
use std::process::Command;
use std::os::windows::process::CommandExt;
use sqlx::mysql::{MySqlPool, MySqlPoolOptions};
use sqlx::sqlite::{SqlitePool, SqlitePoolOptions};
use std::time::Duration;
use tauri_plugin_dialog::DialogExt;
use tauri::AppHandle;
use std::path::{Path, PathBuf};

// 连接mysql
async fn connect_mysql( host: &str, port: &str, user_name: &str, password: &str, ) -> Result<MySqlPool, sqlx::Error> {
    // 连接地址
    let database_url = format!("mysql://{}:{}@{}:{}", user_name, password, host, port);
    // 创建连接池
    MySqlPoolOptions::new()
        .max_connections(5)
        .acquire_timeout(Duration::from_secs(10))
        .connect(&database_url)
        .await
}
// 连接sqlite
async fn connect_sqlite(db_file_path: &str) -> Result<SqlitePool, sqlx::Error> {
    SqlitePoolOptions::new()
        .max_connections(5)
        .connect(&db_file_path)
        .await
}
// 获取uvg.exe路径
fn get_uvg_path() -> PathBuf {
    // 获取主程序的父目录
    let exe_dir = std::env::current_exe()
        .expect("无法获取当前程序路径")
        .parent()
        .expect("无法获取父级目录")
        .to_path_buf();
    // 生产环境：主程序同级目录
    let prod = exe_dir.join("uvg.exe");
    if prod.exists() {
        return prod;
    }
    // 开发环境：src-tauri/binaries/
    let dev = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("binaries")
        .join("uvg.exe");
    if dev.exists() {
        return dev;
    }
    // 都找不到事返回生成路径，让调用方报清晰的错误
    prod
}
// 初始化数据
pub async fn init_data() -> ResponseInitData {
    // 获取桌面路径
    let desktop_path: String;
    match dirs::desktop_dir() {
        Some(path) => desktop_path = path.display().to_string(),
        None => desktop_path = "".into(),
    }
    ResponseInitData {
        message: "success".into(),
        data: InitData {
            data_base_type: Some(vec!["MySQL".into(), "Sqlite".into()]),
            host: Some("localhost".into()),
            port: Some("3306".into()),
            user_name: Some("root".into()),
            out_file: Some(format!("{}\\model.py",desktop_path)),
        },
    }
}
// 获取mysql所有数据库名称
pub async fn get_mysql_databases(host: &str, port: &str, user_name: &str, password: &str, ) -> ResponseDatabases {
    // 连接数据库
    let pool = match connect_mysql(host, port, user_name, password).await {
        Ok(pool) => pool,
        Err(_) => {
            return ResponseDatabases {
                message: "fail".into(),
                data: Databaes::default(),
            };
        }
    };
    // 查询数据库
    let result = sqlx::query_as::<_, DatabaseName>(
        r#"
        SELECT `SCHEMA_NAME` AS `database`
        FROM `information_schema`.`SCHEMATA`
        WHERE `SCHEMA_NAME` NOT IN (
            'information_schema',
            'performance_schema',
            'mysql',
            'sys'
        )
        ORDER BY `SCHEMA_NAME`
        "#,
    )
    .fetch_all(&pool)
    .await;

    // 获取查询出的数据库
    match result {
        Ok(databases) => {
            // 转换为vec格式
            let names: Vec<String> = databases.into_iter().map(|d| d.database).collect();
            // 关闭连接池
            pool.close().await;
            // 返回最终结果
            return ResponseDatabases {
                message: "success".into(),
                data: Databaes {
                    databases: Some(names),
                },
            };
        }
        Err(_) => {
            pool.close().await;
            return ResponseDatabases {
                message: "fail".into(),
                data: Databaes::default(),
            };
        }
    }
}
// 获取mysql数据库所有表名
pub async fn get_mysql_tables(host: &str, port: &str, user_name: &str, password: &str, db_name: &str, ) -> ResponseTables {
    // 连接数据库
    let pool = match connect_mysql(host, port, user_name, password).await {
        Ok(pool) => pool,
        Err(_) => {
            return ResponseTables {
                message: "fail".into(),
                data: Tables::default(),
            };
        }
    };
    // 查询指定数据库中的所有表名
    let result = sqlx::query_as::<_, TableName>(
        r#"
        SELECT TABLE_NAME AS `table_name`
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = ?
        "#,
    )
    .bind(db_name) // 绑定数据库名参数
    .fetch_all(&pool)
    .await;
    // 获取查询出的数据表
    match result {
        Ok(tables) => {
            // 转换为vec格式
            let names: Vec<String> = tables.into_iter().map(|r| r.table_name).collect();
            // 关闭连接池
            pool.close().await;
            // 返回最终结果
            return ResponseTables {
                message: "success".into(),
                data: Tables {
                    tables: Some(names),
                },
            };
        }
        Err(_) => {
            pool.close().await;
            return ResponseTables {
                message: "fail".into(),
                data: Tables::default(),
            };
        }
    }
}

// 获取sqlite数据库文件
pub async fn get_sqlite_file(app: &AppHandle) -> ResponseSelectSqlitePath{
    let file_path = app
        .dialog()
        .file()
        .add_filter("SQLite 数据库", &["db", "sqlite", "sqlite3"])
        .blocking_pick_file();

    match file_path {
        Some(path) => {
            match path.as_path() {
                Some(p) => {
                    let path_buf = p.to_path_buf();
                    let file_path = path_buf.to_string_lossy().to_string();
                    return ResponseSelectSqlitePath {
                        message: "success".into(),
                        data: SelectSqlitePath {
                            database_file: Some(file_path)
                        }
                    }
                }
                None => {
                    return ResponseSelectSqlitePath {
                        message: "fail".into(),
                        data: SelectSqlitePath::default()
                    }
                }
            }
        }
        None => return ResponseSelectSqlitePath {
            message: "success".into(),
            data: SelectSqlitePath {
                database_file: Some("".to_string())
            }
        }
    }
}
// 获取sqlite数据库所有表名
pub async fn get_sqlite_tables(db_file_path: &str) -> ResponseTables {
    // 连接数据库
    let pool = match connect_sqlite(db_file_path).await {
        Ok(pool) => pool,
        Err(_) => {
            return ResponseTables {
                message: "fail".into(),
                data: Tables::default(),
            };
        }
    };
    let result = sqlx::query_as::<_, TableName>(
        r#"
        SELECT name AS table_name FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        "#,
    )
    .fetch_all(&pool)
    .await;
    // 获取查询出的数据表
    match result {
        Ok(tables) => {
            // 转换为vec格式
            let names: Vec<String> = tables.into_iter().map(|r| r.table_name).collect();
            // 关闭连接池
            pool.close().await;
            // 返回最终结果
            return ResponseTables {
                message: "success".into(),
                data: Tables {
                    tables: Some(names),
                },
            };
        }
        Err(e) => {
            println!("{}", e);
            pool.close().await;
            return ResponseTables {
                message: "fail".into(),
                data: Tables::default(),
            };
        }
    }
}
// 生成mysql模型文件
pub async fn create_mysql_model(host: &str, port: &str, user_name: &str, password: &str, db_name: &str, tables: Vec<String>, out_file: &str, ) -> ResponseCreateResult {
    // uvg.exe路径
    let uvg_path = get_uvg_path();
    if !uvg_path.exists() {
        return ResponseCreateResult {
            message: "fail".into(),
            data: CreateResultData {
                out_file: Some("uvg.exe不存在".into()),
            },
        };
    }
    // println!("{}",&uvg_path);
    // 数据库连接地址
    let url = format!(
        "mysql://{}:{}@{}:{}/{}",
        user_name, password, host, port, db_name
    );
    // 需要生成的表
    let table_list = tables.join(",");
    // 调用uvg.exe，生成模型文件
    let mut cmd = Command::new(&uvg_path);
    cmd.arg(&url)
        .arg("--tables")
        .arg(&table_list)
        .arg("--outfile")
        .arg(&out_file);
    // 隐藏黑窗口
    #[cfg(windows)]
    {
        cmd.creation_flags(0x0800_0000);
    }
    let output = match cmd.output() {
        Ok(o) => o,
        Err(_) => {
            return ResponseCreateResult {
                message: "fail".into(),
                data: CreateResultData::default(),
            }
        }
    };
    if output.status.success() {
        ResponseCreateResult {
            message: "success".into(),
            data: CreateResultData {
                out_file: Some(out_file.into()),
            },
        }
    } else {
        ResponseCreateResult {
            message: "fail".into(),
            data: CreateResultData::default(),
        }
    }
}
// 生成sqlite模型文件
pub async fn create_sqlite_model(db_file_path: &str, tables: Vec<String>, out_file: &str, ) -> ResponseCreateResult {
    // uvg.exe路径
    let uvg_path = get_uvg_path();
    if !uvg_path.exists() {
        return ResponseCreateResult {
            message: "fail".into(),
            data: CreateResultData {
                out_file: Some("uvg.exe不存在".into()),
            },
        };
    }
    // 数据库连接地址
    let url = format!("sqlite:///{}", db_file_path);
    // 需要生成的表
    let table_list = tables.join(",");
    // 调用uvg.exe，生成模型文件
    let mut cmd = Command::new(&uvg_path);
    cmd.arg(&url)
        .arg("--tables")
        .arg(&table_list)
        .arg("--outfile")
        .arg(&out_file);
    #[cfg(windows)]
    {
        cmd.creation_flags(0x0800_0000);
    }
    let output = match cmd.output() {
        Ok(o) => o,
        Err(_) => {
            return ResponseCreateResult {
                message: "fail".into(),
                data: CreateResultData::default(),
            }
        }
    };
    if output.status.success() {
        ResponseCreateResult {
            message: "success".into(),
            data: CreateResultData {
                out_file: Some(out_file.into()),
            },
        }
    } else {
        ResponseCreateResult {
            message: "fail".into(),
            data: CreateResultData::default(),
        }
    }
}
// 获取文件保存路径
pub async fn get_save_path(app: &AppHandle) -> ResponseSelectSavePath {
    let file_path = app
        .dialog()
        .file()
        .add_filter("Python 文件",&["py"])
        .set_file_name("model.py")
        .blocking_save_file();
    match file_path {
        Some(path) => match path.as_path() {
            Some(p) => {
                let save_path = p.to_path_buf().to_string_lossy().to_string();
                return ResponseSelectSavePath{
                    message: "success".into(),
                    data: SelectSavePath {save_path: Some(save_path)}
                }
            }
            None => return ResponseSelectSavePath{
                message: "fail".into(),
                data: SelectSavePath::default()
            }
        }
        None =>  return ResponseSelectSavePath{
            message: "success".into(),
            data: SelectSavePath {save_path: Some("".into())}
        }
    }
}
// 资源管理器打开文件所在目录
pub async fn open_file_folder(file_path: &str) -> ResponseOpenFileFolder {
    // 转换为路径
    let path = Path::new(file_path);
    // 校验路径是否存在
    if !path.exists() {
        return ResponseOpenFileFolder{message: "fail".into()}
    }
    match Command::new("explorer").arg("/select,").arg(path).spawn() {
        Ok(_) => ResponseOpenFileFolder{message: "success".into()},
        Err(_) => ResponseOpenFileFolder{message: "fail".into()}
    }
}