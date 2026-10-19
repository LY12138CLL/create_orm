"""
入口：隐藏 CLI 分支判断 + 启动 GUI。
"""

import sys
import tkinter as tk

from create_orm.app import OrmCodegenGUI
from create_orm.codegen import run_sqlacodegen_cli
from create_orm.config import CLI_FLAG
from create_orm.theme import enable_high_dpi


def main():
    # 隐藏 CLI 分支：GUI 会用 exe 自身作为子进程调起这里跑 sqlacodegen
    if len(sys.argv) >= 2 and sys.argv[1] == CLI_FLAG:
        run_sqlacodegen_cli(sys.argv[2:])
        return

    enable_high_dpi()
    root = tk.Tk()
    OrmCodegenGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()