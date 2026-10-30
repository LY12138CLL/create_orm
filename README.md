# orm_create
这是一个数据库表生成python sqlalchemy类型的orm模型类的工具
## 技术
使用Tauri2实现的，前端页面使用的是vue3 + element plus + vue-router，采用前后端分离技术，所有功能都在rust端实现并暴漏接口供前端调用

核心使用uvg.exe工具实现orm模型代码生成，该工具的github为：https://github.com/johndauphine/uvg


## 性能

应用的启动时间大约3秒

mysql数据库连接超时时间为10秒，生成模型超时时间约为23秒

## 功能

支持选择多个数据表，生成一个python文件

支持的数据库：
- mysql
- sqlite

使用场景：
- 服务器数据库模型类映射，如FastAPI

  
支持的操作系统：
- windows10
- 其它系统未测试

## 使用

核心工具uvg.exe存放位置：src-tauri\binaries
打包后需放置在与主程序同级目录下才能真正运行

初始化：
~~~cmd
pnpm install
~~~


调试：
~~~cmd
pnpm tauri dev
~~~

构建打包：
~~~cmd
pnpm tauri build
~~~




![描述](./doc/1.jpg)