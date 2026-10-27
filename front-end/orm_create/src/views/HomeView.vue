<template>
  <el-container id="home">
    <el-main>
      <el-form
        ref="my-form"
        :model="formData"
        :rules="rules"
        label-width="auto"
        hide-required-asterisk
      >
        <!-- 数据库类型 -->
        <el-row>
          <el-col :span="12">
            <el-form-item label="数据库类型" prop="dbType">
              <el-select
                v-model="formData.dbType"
                @change="onSelectDbType"
                :disabled="isCreateModelLoading"
                placeholder=""
              >
                <el-option
                  v-for="item in dbTypeList"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 主机、端口 -->
        <el-row>
          <el-col :span="16">
            <el-form-item label="主机" prop="host">
              <el-input
                v-model="formData.host"
                :disabled="isCreateModelLoading || formData.dbType === 'Sqlite'"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="端口" prop="port">
              <el-input
                v-model="formData.port"
                :disabled="isCreateModelLoading || formData.dbType === 'Sqlite'"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 用户名 -->
        <el-row>
          <el-col :span="24">
            <el-form-item label="用户名" prop="userName">
              <el-input
                v-model="formData.userName"
                :disabled="isCreateModelLoading || formData.dbType === 'Sqlite'"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 密码 -->
        <el-row>
          <el-col :span="24">
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="formData.password"
                :disabled="isCreateModelLoading || formData.dbType === 'Sqlite'"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 数据库名/文件、连接 -->
        <el-row>
          <el-col :span="20">
            <el-form-item label="数据库名/文件" prop="dbName">
              <el-input
                v-if="formData.dbType === 'Sqlite'"
                v-model="formData.dbName"
                :disabled="isCreateModelLoading"
              />
              <el-select
                v-else
                v-model="formData.dbName"
                @change="onGetMySqlDbTable"
                :disabled="isCreateModelLoading"
                placeholder=""
              >
                <el-option
                  v-for="item in dbNameList"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="3" :offset="1">
            <el-button
              v-if="formData.dbType === 'Sqlite'"
              @click="onConnectSqlite"
              :disabled="isCreateModelLoading"
              >浏览</el-button
            >
            <el-button v-else @click="onConnectMysql" :disabled="isCreateModelLoading"
              >连接</el-button
            >
          </el-col>
        </el-row>

        <!-- 数据表 -->
        <el-row>
          <el-col :span="24">
            <el-form-item label="数据表" prop="dbTableNameList">
              <el-select
                v-model="formData.dbTableNameList"
                :disabled="isCreateModelLoading"
                placeholder=""
                multiple
                class="db-table-select"
              >
                <el-option
                  v-for="item in dbTableList"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 输出文件、浏览 -->
        <el-row>
          <el-col :span="20">
            <el-form-item label="输出文件" prop="outputFile">
              <el-input v-model="formData.outputFile" :disabled="isCreateModelLoading" />
            </el-form-item>
          </el-col>
          <el-col :span="3" :offset="1">
            <el-button @click="onSelectOutputFile">浏览</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-main>
    <el-footer class="footer">
      <!-- 状态、生成模型 -->
      <el-row>
        <el-col :span="20">
          <span :class="stateStyle.stateClass">{{ stateInfo.state }}</span>
          &nbsp;&nbsp;
          <span :class="stateStyle.messageClass" @click="openOutputFolder">{{
            stateInfo.message
          }}</span>
        </el-col>
        <el-col :span="4" style="text-align: right">
          <el-button type="primary" @click="onCreateModel" :disabled="isCreateModelLoading"
            >生成模型</el-button
          >
        </el-col>
      </el-row>
    </el-footer>
  </el-container>
</template>

<script setup>
import { computed, ref, useTemplateRef } from 'vue'
import {
  apiMysqlConnectDatabase,
  apiMysqlGetDatabaseTable,
  apiSqliteGetDatabaseTable,
  apiSqliteConnectDatabase,
  apiGetInitData,
  apiSelectOutputFile,
  apiMysqlCrateModel,
  apiSqliteCreateModel,
  apiOpenOutputFolder,
} from '@/api/home'

/* DOM */
const form = useTemplateRef('my-form')

/* 数据 */
// 表单
const formData = ref({
  dbType: '', // 数据库类型
  port: '', // 端口
  host: '', // 主机
  userName: '', // 用户名
  password: '', // 密码
  dbName: '', // 数据库名/文件
  dbTableNameList: '', // 数据库表
  outputFile: '', // 输出文件
})
// 数据库类型列表
const dbTypeList = ref([])
// 数据库名列表
const dbNameList = ref([])
// 数据库表列表
const dbTableList = ref([
  { key: 'table1', value: 'table1' },
  { key: 'table2', value: 'table2' },
  { key: 'table3', value: 'table3' },
])
// 状态信息
const stateInfo = ref({ state: '', message: '' })

/* 辅助变量 */
// 表单校验规则
const rules = {
  dbType: [{ required: true, message: '数据库类型不能为空', trigger: 'manual' }],
  host: [{ required: true, message: '主机地址不能为空', trigger: 'manual' }],
  port: [{ required: true, message: '端口号不能为空', trigger: 'manual' }],
  userName: [{ required: true, message: '用户名不能为空', trigger: 'manual' }],
  password: [{ required: true, message: '密码不能为空', trigger: 'manual' }],
  dbName: [{ required: true, message: '数据库不能为空', trigger: 'manual' }],
  dbTableNameList: [{ required: true, message: '数据表不能为空', trigger: 'manual' }],
  outputFile: [{ required: true, message: '输出文件不能为空', trigger: 'manual' }],
}
// 当前状态样式
const stateStyle = computed(() => {
  const state = stateInfo.value.state
  const success = { stateClass: 'success', messageClass: 'message' }
  const error = { stateClass: 'error', messageClass: '' }
  if (state === '生成成功') {
    return { stateClass: 'success', messageClass: 'message create-success' }
  } else if (state.includes('成功')) {
    return success
  } else if (state.includes('失败')) {
    return error
  } else {
    return { stateClass: '', messageClass: '' }
  }
})
const isCreateModelLoading = ref(false) // 是否生成模型中

/* 功能函数 */
// 选择数据库类型
function onSelectDbType() {
  formData.value.dbName = ''
  formData.value.dbTableNameList = []
  dbTableList.value = []
  dbNameList.value = []
  stateInfo.value.state = '就绪'
  stateInfo.value.message = ''
}
// 连接mysql数据库
async function onConnectMysql() {
  try {
    await form.value.validateField(['host', 'port', 'userName', 'password'])
  } catch {
    // 校验失败
    return
  }
  reset()
  stateInfo.value.state = '正在连接中...'
  stateInfo.value.message = ''
  const result = await apiMysqlConnectDatabase(
    formData.value.host,
    formData.value.port,
    formData.value.userName,
    formData.value.password,
  )
  if (result.message === 'success') {
    dbNameList.value = result.data.dataBaseList.map((item) => ({ label: item, value: item }))
    formData.value.dbName = dbNameList.value.length ? dbNameList.value[0].value : ''
    await onGetMySqlDbTable()
  } else {
    stateInfo.value.state = '连接失败'
    stateInfo.value.message = ''
  }
}

// 获取mysql数据库表
async function onGetMySqlDbTable() {
  try {
    await form.value.validateField(['host', 'port', 'userName', 'password'])
  } catch {
    // 校验失败
    return
  }
  stateInfo.value.state = '正在连接中...'
  stateInfo.value.message = ''
  const result = await apiMysqlGetDatabaseTable(
    formData.value.host,
    formData.value.port,
    formData.value.userName,
    formData.value.password,
    formData.value.dbName,
  )
  if (result.message === 'success') {
    dbTableList.value = result.data.dataBaseTableList.map((item) => ({ label: item, value: item }))
    stateInfo.value.state = '连接成功'
    formData.value.dbTableNameList = dbTableList.value.length ? [dbTableList.value[0].value] : []
    stateInfo.value.message = `共 ${dbTableList.value.length} 张表`
  } else {
    dbTableList.value = []
    stateInfo.value.state = '连接失败'
    stateInfo.value.message = ''
  }
}

// 连接sqlite数据库
async function onConnectSqlite() {
  reset()
  stateInfo.value.state = '正在连接中...'
  const result = await apiSqliteConnectDatabase()
  if (result.message === 'success') {
    if (result.data.databaseFile) {
      formData.value.dbName = result.data.databaseFile
      await onGetSqliteDbTable()
    } else {
      formData.value.dbName = ''
      stateInfo.value.state = '连接失败'
      stateInfo.value.message = ''
    }
  } else {
    formData.value.dbName = ''
    stateInfo.value.state = '连接失败'
    stateInfo.value.message = ''
  }
}

// 获取sqlite数据库表
async function onGetSqliteDbTable() {
  try {
    await form.value.validateField(['dbName'])
  } catch {
    // 校验失败
    return
  }
  stateInfo.value.state = '正在连接中...'
  stateInfo.value.message = ''
  const result = await apiSqliteGetDatabaseTable(formData.value.dbName)
  if (result.message === 'success') {
    dbTableList.value = result.data.dataBaseTableList.map((item) => ({ label: item, value: item }))
    stateInfo.value.state = '连接成功'
    formData.value.dbTableNameList = dbTableList.value.length ? [dbTableList.value[0].value] : []
    stateInfo.value.message = `共 ${dbTableList.value.length} 张表`
  } else {
    dbTableList.value = []
    stateInfo.value.state = '连接失败'
    stateInfo.value.message = ''
  }
}

// 选择输出文件
async function onSelectOutputFile() {
  const result = await apiSelectOutputFile()
  if (result.message === 'success') {
    if (result.data.outputFile) {
      formData.value.outputFile = result.data.outputFile
    }
  } else {
    formData.value.outputFile = ''
    stateInfo.value.state = '选择输出文件失败'
    stateInfo.value.message = ''
  }
}

// 生成模型
async function onCreateModel() {
  if (formData.value.dbType === 'MySQL') {
    await createMySqlModel()
  } else {
    await createSqliteModel()
  }
}
// 生成mysql模型
async function createMySqlModel() {
  try {
    await form.value.validateField(['host', 'userName', 'password', 'dbName', 'dbTableNameList'])
  } catch {
    // 校验失败
    return
  }
  stateInfo.value.state = '正在生成中...'
  stateInfo.value.message = ''
  isCreateModelLoading.value = true
  const result = await apiMysqlCrateModel(
    formData.value.host,
    formData.value.userName,
    formData.value.password,
    formData.value.dbName,
    formData.value.dbTableNameList,
    formData.value.outputFile,
  )
  if (result.message === 'success') {
    stateInfo.value.state = '生成成功'
    stateInfo.value.message = result.data.outputFile
    ElMessageBox.alert('生成成功', '提示', {
      confirmButtonText: '确认',
      type: 'success',
    })
  } else {
    stateInfo.value.state = '生成失败'
    stateInfo.value.message = ''
  }
  isCreateModelLoading.value = false
}
// 生成sqlite模型
async function createSqliteModel() {
  try {
    await form.value.validateField(['dbName', 'dbTableNameList'])
  } catch {
    // 校验失败
    return
  }
  stateInfo.value.state = '正在生成中...'
  stateInfo.value.message = ''
  isCreateModelLoading.value = true
  const result = await apiSqliteCreateModel(
    formData.value.dbName,
    formData.value.dbTableNameList,
    formData.value.outputFile,
  )
  if (result.message === 'success') {
    stateInfo.value.state = '生成成功'
    stateInfo.value.message = result.data.outputFile
    ElMessageBox.alert('生成成功', '提示', {
      confirmButtonText: '确认',
      type: 'success',
    })
  } else {
    stateInfo.value.state = '生成失败'
    stateInfo.value.message = ''
  }
  isCreateModelLoading.value = false
}
// 打开输出目录
async function openOutputFolder() {
  if (stateInfo.value.state === '生成成功') {
    try {
      const result = await apiOpenOutputFolder(formData.value.outputFile)
      if (result.message === 'fail') {
        ElMessageBox.alert('打开失败，文件不存在', '提示', {
          confirmButtonText: '确认',
          type: 'error',
        })
      }
    } catch {
      ElMessageBox.alert('打开失败，文件不存在', '提示', {
        confirmButtonText: '确认',
        type: 'error',
      })
    }
  }
}

// 初始化
async function init() {
  const result = await apiGetInitData()
  if (result.message === 'success') {
    dbTypeList.value = result.data.dataBaseType.map((item) => ({ label: item, value: item }))
    formData.value.dbType = dbTypeList.value.length ? dbTypeList.value[0].value : ''
    formData.value.host = result.data.host
    formData.value.port = result.data.port
    formData.value.userName = result.data.userName
    formData.value.outputFile = result.data.outFile
    stateInfo.value.state = '就绪'
  }
}

/* 辅助函数 */
// 重置一些数据
function reset() {
  formData.value.dbName = ''
  formData.value.dbTableName = ''
  dbNameList.value = []
  dbTableList.value = []
  stateInfo.value.state = '就绪'
  stateInfo.value.message = ''
}
window.addEventListener('pywebviewready', async () => {
  await init()
})
init()
</script>
<style lang="css" scoped>
#home {
  height: 100vh; /* 占满窗口高度 */
  display: flex; /* el-container 本身是 flex，这里确保方向 */
  flex-direction: column;
  overflow: hidden; /* 窗口不出现滚动条 */
}

.error {
  color: red;
}
.success {
  color: green;
}
.message {
  color: #337ecc;
}
.create-success {
  cursor: pointer;
  text-decoration: underline #337ecc;
  text-underline-offset: 5px;
}

/* 数据表多选下拉：让选中值的字体样式与单选下拉保持一致 */
.db-table-select :deep(.el-select__selected-item .el-tag),
.db-table-select :deep(.el-select__tags .el-tag) {
  /* 用变量兜底（不同版本变量名/优先级略有差异） */
  --el-tag-bg-color: transparent;
  --el-tag-border-color: transparent;
  --el-tag-text-color: var(--el-text-color-regular);
  --el-tag-font-size: var(--el-font-size-base);

  /* 关键：直接写属性，覆盖 el-tag--primary 上的变量声明 */
  background-color: transparent;
  border: none;
  border-radius: 0;
  color: var(--el-text-color-regular); /* 与单选文字颜色一致 */
  font-size: var(--el-font-size-base); /* 14px，与单选一致 */
  font-weight: 400;
  line-height: inherit;
  height: auto;
  padding: 0;
  margin-right: 8px; /* 多个值之间的间距 */
}

/* 关闭按钮：颜色加深，hover 用主题色 */
.db-table-select :deep(.el-tag .el-tag__close) {
  /* 用次级文字色，比 placeholder 深一档；想更深可换 --el-text-color-regular */
  color: var(--el-text-color-primary);
  background-color: transparent;
  margin-left: 4px;
  margin-right: 0;
  font-size: 14px; /* 图标略放大，视觉更醒目 */
}
.db-table-select :deep(.el-tag .el-tag__close:hover) {
  color: var(--el-color-primary);
  background-color: transparent;
}

/* 让多选第一个值的左间距与单选一致 */
.db-table-select :deep(.el-select__wrapper) {
  /* 单选的默认水平 padding，兜底 11px */
  padding-left: var(--el-input-padding-horizontal, 11px);
}

/* 清掉选择区/标签容器可能存在的额外左侧偏移 */
.db-table-select :deep(.el-select__selection),
.db-table-select :deep(.el-select__selected-item),
.db-table-select :deep(.el-select__tags) {
  padding-left: 0;
  margin-left: 0;
}

/* 第一个标签不要左边距（多选换行时第二行也跟随对齐） */
.db-table-select :deep(.el-select__selected-item:first-child .el-tag),
.db-table-select :deep(.el-select__tags .el-tag:first-child) {
  margin-left: 0;
}
</style>
