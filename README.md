

这是一个数据库表生成python sqlalchemy类型的orm模型类的工具

使用的是tkinter做GUI界面，orm生成工具用的是sqlalchemy

支持的数据库：
- mysql
- sqlite

使用场景：
- 服务器数据库模型类映射，如FastAPI

  
支持的操作系统：
- windows10
- 其它系统未测试

支持的python版本：
- python3.13.15
- 其它版本未测试

打包命令，项目根目录执行：
```cmd
uv run pyinstaller -F -w -n orm模型生成器 ^
    -i "%CD%\src\create_orm\app.ico" ^
    --upx-dir D:\python\upx-5.2.1-win64 ^
    -p "%CD%\src" ^
    --hidden-import create_orm ^
    --collect-submodules create_orm ^
    --collect-submodules sqlacodegen ^
    --collect-data sqlacodegen ^
    --hidden-import sqlacodegen.cli ^
    --copy-metadata sqlacodegen ^
    --collect-all inflect ^
    --collect-all typeguard ^
    --distpath "./output/dist" ^
    --workpath "./output/build" ^
    --specpath "./output" ^
    --add-data "%CD%\src\create_orm\app.ico;." ^
    --version-file "%CD%\src\create_orm\version_info.txt" ^
    --clean --noconfirm ^
    ./src/create_orm/main.py
```




![描述](./doc/1.jpg)