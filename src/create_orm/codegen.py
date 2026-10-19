"""sqlacodegen 调用层：子进程执行（源码/打包两套命令）与隐藏 CLI 分支。"""

import os
import subprocess
import sys

from .config import CLI_FLAG, GEN_TIMEOUT


def run_sqlacodegen(db_url, table, outfile, timeout=GEN_TIMEOUT):
    """
    统一入口：
      · 源码运行 → python -m sqlacodegen ...
      · 打包运行 → exe --run-sqlacodegen ...  （走隐藏 CLI 子进程，不启动 Tk）
    都带超时；超时返回 CompletedProcess(returncode=124)。
    """
    if getattr(sys, "frozen", False):
        cmd = [sys.executable, CLI_FLAG,
               db_url, "--tables", table, "--outfile", outfile]
        extra = {"creationflags": subprocess.CREATE_NO_WINDOW} \
            if sys.platform == "win32" else {}
    else:
        cmd = [sys.executable, "-m", "sqlacodegen",
               db_url, "--tables", table, "--outfile", outfile]
        extra = {}

    try:
        return subprocess.run(
            cmd,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, **extra,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            args=cmd, returncode=124, stdout="",
            stderr=(f"sqlacodegen 执行超过 {timeout} 秒，已强制终止。\n"
                    f"请确认数据库可连、密码正确、表名无误，"
                    f"或调大 GEN_TIMEOUT（当前 {timeout}s）。"),
        )


def _ensure_stdio():
    """
    -w 打包后 sys.stdout / sys.stderr 为 None。
    作为子进程被启动时底层 fd 1/2 仍然有效（被父进程连到管道），
    这里重建出可写的文件对象，让父进程能 capture 到输出。
    """
    for name, fd in (("stdout", 1), ("stderr", 2)):
        if getattr(sys, name) is None:
            try:
                f = open(fd, "w", encoding="utf-8", buffering=1, closefd=False)
            except Exception:
                try:
                    f = open(os.devnull, "w", encoding="utf-8")
                except Exception:
                    import io
                    f = io.StringIO()
            setattr(sys, name, f)


def run_sqlacodegen_cli(args):
    """纯 CLI 模式：不启动 Tk，把 args 透传给 sqlacodegen。"""
    _ensure_stdio()
    try:
        from sqlacodegen.cli import main as scg_main
    except ImportError:
        try:
            from sqlacodegen.main import main as scg_main
        except ImportError as exc:
            print(f"无法导入 sqlacodegen：{exc}", file=sys.stderr)
            sys.exit(1)

    sys.argv = ["sqlacodegen", *args]
    try:
        scg_main()
    except SystemExit as exc:
        code = exc.code
        if code is None:
            sys.exit(0)
        sys.exit(code if isinstance(code, int) else 1)
    except Exception:
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)