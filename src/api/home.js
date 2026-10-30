import {invoke} from "@tauri-apps/api/core"
// 获取初始信息
export async function apiGetInitData() {
  try {
    return await invoke('api_init_data')
  } catch (e) {
    return { message: 'fail', data: {} }
  }
}

// 连接mysql数据库
export async function apiMysqlConnectDatabase(host, port, userName, password) {
  try {
    const result = await invoke('api_get_mysql_databases', {host: host, port: port, userName: userName, password: password})
    if (result.message === 'success') {
      return result
    } else {
      return { message: 'fail', data: {} }
    }
  } catch (e) {
    return { message: 'fail', data: {} }
  }
}

// 获取Mysql数据库表
export async function apiMysqlGetDatabaseTable(host, port, userName, password, databaseName) {
  try {
    const result = await invoke('api_get_mysql_tables', {host: host, port: port, userName: userName, password:password, dbName: databaseName})
    if (result.message === 'success') {
      return result
    } else {
      return { message: 'fail', data: {} }
    }
  } catch (e) {
    return { message: 'fail', data: {} }
  }
}

// 连接sqlite数据库文件
export async function apiSqliteConnectDatabase() {
  try {
    const result = await await invoke('api_get_sqlite_file')
    if (result.message === 'success') {
      return result
    } else {
      return { message: 'fail', data: {} }
    }
  } catch (e) {
    return { message: 'fail', data: {} }
  }
}

// 获取Sqlite数据库表
export async function apiSqliteGetDatabaseTable(databaseFile) {
  try {
    const result = await invoke('api_get_sqlite_tables', {dbFilePath: databaseFile})
    if (result.message === 'success') {
      return result
    } else {
      return { message: 'fail', data: {} }
    }
  } catch (e) {
    return { message: 'fail', data: {} }
  }
}

// 选择输出文件
export async function apiSelectOutputFile() {
  try {
    const result = await invoke('api_select_file_save_path')
    if (result.message === 'success') {
      return result
    } else {
      return { message: 'fail', data: {} }
    }
  } catch (e) {
    return { message: 'fail', data: {} }
  }
}

// mysql生成模型
export async function apiMysqlCrateModel(
  host,
  port,
  userName,
  password,
  databaseName,
  datbabaseTableList,
  outputFile,
) {
  try {
    const result = await invoke('api_create_mysql_model', {host: host, port: port, userName: userName, password: password, dbName: databaseName, tables: datbabaseTableList, outFile: outputFile})
    console.log(result)
    if (result.message === 'success') {
      return result
    } else {
      return { message: 'fail', data: {} }
    }
  } catch (e) {
    return { message: 'fail', data: {} }
  }
}

// sqlite生成模型
export async function apiSqliteCreateModel(databaseFile, datbabaseTableList, outputFile) {
  try {
    const result = await invoke('api_create_sqlite_model', {dbFilePath: databaseFile, tables: datbabaseTableList, outFile: outputFile})
    if (result.message === 'success') {
      return result
    } else {
      return { message: 'fail', data: {} }
    }
  } catch (e) {
    return { message: 'fail', data: {} }
  }
}

// 打开资源管理器定位到输出文件
export async function apiOpenOutputFolder(outputFile) {
  try {
    const result = await invoke('api_open_file_folder', {filePath: outputFile})
    if (result.message === 'success') {
      return result
    } else {
      return { message: 'fail'}
    }
  } catch (e) {
    return { message: 'fail'}
  }
}
