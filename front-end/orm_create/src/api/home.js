// 获取初始信息
export async function apiGetInitData() {
  try {
    return await window.pywebview.api.init()
  } catch (e) {
    return { message: 'fail', data: {} }
  }
}

// 连接mysql数据库
export async function apiMysqlConnectDatabase(host, port, userName, password) {
  try {
    const result = await window.pywebview.api.connect_mysql(host, port, userName, password)
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
    const result = await window.pywebview.api.get_mysql_table(
      host,
      port,
      userName,
      password,
      databaseName,
    )
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
    const result = await window.pywebview.api.connect_sqlite()
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
    const result = await window.pywebview.api.get_sqlite_table(databaseFile)
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
    const result = await window.pywebview.api.select_output_file()
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
  userName,
  password,
  databaseName,
  datbabaseTableList,
  outputFile,
) {
  try {
    const result = await window.pywebview.api.create_mysql_model(
      host,
      userName,
      password,
      databaseName,
      datbabaseTableList,
      outputFile,
    )
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
    const result = await window.pywebview.api.create_sqlite_model(
      databaseFile,
      datbabaseTableList,
      outputFile,
    )
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
    const result = await window.pywebview.api.open_output_folder(outputFile)
    if (result.message === 'success') {
      return result
    } else {
      return { message: 'fail', data: {} }
    }
  } catch (e) {
    return { message: 'fail', data: {} }
  }
}
