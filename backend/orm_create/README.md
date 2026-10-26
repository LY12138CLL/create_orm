# orm_create
这是orm_create pywebview版的python端项目
使用的是pywebview做GUI界面，使用前后端分离，前端项目在front-end文件夹内
核心orm模型代码生成使用的是sqlacodegen库

初始化项目：
~~~cmd
uv sync --locked
~~~

入口文件是main.py，直接执行它就可以运行

打包工具使用的是pyinstaller，打包命令：
~~~cmd
uv run pyinstaller -w ^
  -i ./src/orm_create/app.ico ^
  --paths=./src/orm_create ^
  --hidden-import=api ^
  --hidden-import=service ^
  --collect-all=sqlacodegen ^
  --collect-all=inflect ^
  --add-data "./src/orm_create/web;web" ^
  --add-data "./src/orm_create/app.ico;." ^
  --upx-dir D:/python/upx-5.2.1-win64 ^
  --name orm_create ^
  ./src/orm_create/main.py
~~~

![描述](./doc/1.jpg)