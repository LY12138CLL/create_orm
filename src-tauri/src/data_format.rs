// 数据结构体
use serde::Serialize;
use sqlx::FromRow;

// 数据库名
#[derive(Debug, FromRow)]
pub struct DatabaseName {
    pub database: String,
}
// 数据表名
#[derive(Debug, FromRow)]
pub struct TableName {
    pub table_name: String,
}

// 查询出的所有数据库
#[derive(Serialize, Default, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Databaes {
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub databases: Option<Vec<String>>,
}
// 查询出的所有数据表
#[derive(Serialize, Default, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Tables {
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub tables: Option<Vec<String>>,
}
// 初始化数据
#[derive(Serialize, Default, Debug)]
#[serde(rename_all = "camelCase")]
pub struct InitData {
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub data_base_type: Option<Vec<String>>,
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub host: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub port: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub user_name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub out_file: Option<String>,
}
// 模型生成结果数据
#[derive(Serialize, Default, Debug)]
#[serde(rename_all = "camelCase")]
pub struct CreateResultData {
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub out_file: Option<String>,
}
// sqlite文件路径
#[derive(Serialize, Default, Debug)]
#[serde(rename_all = "camelCase")]
pub struct SelectSqlitePath {
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub database_file: Option<String>,
}
// 文件保存路径
#[derive(Serialize, Default, Debug)]
#[serde(rename_all = "camelCase")]
pub struct SelectSavePath {
    #[serde(skip_serializing_if = "Option::is_none", default)]
    pub save_path: Option<String>,
}
// 响应给前端的数据库查询结果
#[derive(Serialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ResponseDatabases {
    pub message: String,
    pub data: Databaes,
}
// 响应给前端的数据表查询结果
#[derive(Serialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ResponseTables {
    pub message: String,
    pub data: Tables,
}
// 响应给前端的初始化数据
#[derive(Serialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ResponseInitData {
    pub message: String,
    pub data: InitData,
}
// 响应给前端的模型生成结果
#[derive(Serialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ResponseCreateResult {
    pub message: String,
    pub data: CreateResultData,
}
// 响应给前端的sqlite文件选择结果
#[derive(Serialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ResponseSelectSqlitePath {
    pub message: String,
    pub data: SelectSqlitePath,
}
// 响应给前端的文件报错结果
#[derive(Serialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ResponseSelectSavePath {
    pub message: String,
    pub data: SelectSavePath,
}
// 响应给前端的打开文件所在目录结果
#[derive(Serialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct ResponseOpenFileFolder {
    pub message: String
}