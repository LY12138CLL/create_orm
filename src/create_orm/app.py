"""主窗口 OrmCodegenGUI。"""

import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, ttk

from .codegen import run_sqlacodegen
from .config import (
    ACCENT, BG_INPUT, BG_PAGE, BORDER, FG_DETAIL, FG_ERROR, FG_MUTED,
    FG_SUCCESS, FG_TEXT, GEN_TIMEOUT,
)
from .db import build_db_url, build_server_url, load_databases, load_tables
from .theme import (
    get_dpi_scale, pick_font_family, resource_path, set_window_icon,
    setup_modern_theme,
)


def default_outfile():
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.isdir(desktop):
        desktop = os.path.expanduser("~")
    return os.path.join(desktop, "models.py")


class OrmCodegenGUI:
    def __init__(self, root):
        self.root = root
        self._scale, dpi = get_dpi_scale(root)
        try:
            root.tk.call("tk", "scaling", dpi / 72.0)
        except Exception:
            pass

        root.title("ORM 模型生成器")
        w, h = int(780 * self._scale), int(560 * self._scale)
        root.geometry(f"{w}x{h}")
        root.minsize(int(740 * self._scale), int(520 * self._scale))

        set_window_icon(root, "app.ico")

        self._family = pick_font_family(root)
        setup_modern_theme(root, self._family, self._scale)

        self.db_type_var = tk.StringVar(value="MySQL")
        self.host_var = tk.StringVar(value="localhost")
        self.port_var = tk.StringVar(value="3306")
        self.user_var = tk.StringVar(value="root")
        self.password_var = tk.StringVar()
        self.database_var = tk.StringVar()

        self.table_var = tk.StringVar()
        self.outfile_var = tk.StringVar(value=default_outfile())

        self._db_url = None
        self._tables = []

        # 线程 → 主线程的消息队列；轮询在主线程执行，保证 Tkinter 线程安全
        self._queue = queue.Queue()
        self._busy = False

        self._build_ui()
        self._on_db_type_change()
        self.root.after(50, self._drain_queue)

    def _px(self, n):
        return max(1, round(n * self._scale))

    # ---------------------- 线程安全任务调度 ---------------------- #
    def _run_async(self, work, on_ok, on_err=None):
        """
        统一线程模板：
          work()   在后台线程执行，返回值通过 (True, result) 入队
          on_ok(result) / on_err(exc) 在主线程执行
        重复调用会被忽略（已有任务在跑时直接返回 False）。
        """
        if self._busy:
            return False
        self._set_busy(True)

        def worker():
            try:
                self._queue.put((True, work()))
            except Exception as exc:
                self._queue.put((False, exc))

        self._pending = (on_ok, on_err)
        threading.Thread(target=worker, daemon=True).start()
        return True

    def _drain_queue(self):
        """主线程轮询队列，取出后台任务结果并分发回调。"""
        try:
            while True:
                ok, payload = self._queue.get_nowait()
                on_ok, on_err = self._pending
                self._pending = None
                self._set_busy(False)
                try:
                    (on_ok if ok else (on_err or self._on_task_error))(payload)
                except Exception:
                    import traceback
                    traceback.print_exc()
        except queue.Empty:
            pass
        self.root.after(50, self._drain_queue)

    def _on_task_error(self, exc):
        """未单独指定 on_err 时的兜底错误处理。"""
        self._set_status("操作失败", prefix_color=FG_ERROR)
        self._show_message("错误", str(exc)[:1500], "error")

    # ---------------------- 自定义居中模态弹窗 ---------------------- #
    def _show_message(self, title, message, kind="info"):
        """居中于主窗口的模态提示框。kind: info / error / warning"""
        title_color = {
            "info": FG_SUCCESS,
            "error": FG_ERROR,
            "warning": ACCENT,
        }.get(kind, FG_TEXT)

        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.transient(self.root)
        dlg.resizable(False, False)
        dlg.configure(bg=BG_INPUT)
        dlg.grab_set()

        try:
            ico = resource_path("app.ico")
            if os.path.exists(ico):
                dlg.iconbitmap(ico)
        except Exception:
            pass

        pad = self._px(24)
        container = tk.Frame(dlg, bg=BG_INPUT, padx=pad, pady=self._px(20))
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container, text=title, fg=title_color, bg=BG_INPUT,
            font=(self._family, 11, "bold"), anchor="w",
        ).pack(anchor="w")

        tk.Frame(container, height=1, bg=BORDER).pack(
            fill=tk.X, pady=(self._px(10), self._px(12)))

        tk.Label(
            container, text=message, fg=FG_TEXT, bg=BG_INPUT,
            font=(self._family, 10), anchor="w", justify="left",
            wraplength=self._px(380),
        ).pack(anchor="w")

        btn_row = tk.Frame(container, bg=BG_INPUT)
        btn_row.pack(fill=tk.X, pady=(self._px(18), 0))
        ttk.Button(
            btn_row, text="确定", command=dlg.destroy,
            style="Accent.TButton").pack(side=tk.RIGHT)

        dlg.bind("<Return>", lambda e: dlg.destroy())
        dlg.bind("<Escape>", lambda e: dlg.destroy())

        dlg.update_idletasks()
        w = max(dlg.winfo_reqwidth(), self._px(400))
        h = dlg.winfo_reqheight()

        self.root.update_idletasks()
        rx, ry = self.root.winfo_rootx(), self.root.winfo_rooty()
        rw, rh = self.root.winfo_width(), self.root.winfo_height()
        x = rx + (rw - w) // 2
        y = ry + (rh - h) // 2
        dlg.geometry(f"{w}x{h}+{max(x, 0)}+{max(y, 0)}")

        self.root.wait_window(dlg)

    # ------------------------ 带空心箭头的 Combobox ------------------------ #
    def _make_combobox(self, parent, *, values=(), state="readonly",
                       width=None, textvariable=None):
        kwargs = {
            "values": values,
            "state": state,
            "textvariable": textvariable,
        }
        if width is not None:
            kwargs["width"] = width
        cb = ttk.Combobox(parent, **kwargs)

        size = self._px(14)
        arrow = tk.Canvas(
            cb, width=size, height=size, bg=BG_INPUT,
            highlightthickness=0, bd=0, cursor="hand2")
        arrow.place(relx=1.0, rely=0.5, anchor="e", x=-self._px(8))
        self._draw_arrow(arrow, size)
        arrow.bind("<Button-1>", lambda e, c=cb: self._post_combobox(c))

        cb._arrow_canvas = arrow
        return cb

    def _draw_arrow(self, canvas, size):
        pad_x = size * 0.30
        top = size * 0.40
        bottom = size * 0.62
        line_w = max(1, round(1.4 * self._scale))
        canvas.create_line(
            pad_x, top,
            size / 2, bottom,
            size - pad_x, top,
            fill=FG_MUTED, width=line_w,
            capstyle=tk.ROUND, joinstyle=tk.ROUND,
        )

    def _post_combobox(self, cb):
        try:
            cb.tk.call("ttk::combobox::Post", cb._w)
        except Exception:
            try:
                cb.event_generate("<Button-1>",
                                  x=cb.winfo_width() - 5, y=cb.winfo_height() // 2)
            except Exception:
                pass

    # ----------------------------- UI 构建 ----------------------------- #
    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=(self._px(28), self._px(24),
                                              self._px(28), self._px(18)))
        outer.pack(fill=tk.BOTH, expand=True)

        outer.columnconfigure(0, weight=0)
        outer.columnconfigure(1, weight=1)
        outer.columnconfigure(2, weight=0)
        outer.columnconfigure(3, weight=0)

        pad_x = (0, self._px(12))
        pad_y = self._px(6)
        gap_x = (self._px(16), self._px(10))
        row = 0

        ttk.Label(outer, text="数据库类型").grid(
            row=row, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.db_type_cb = self._make_combobox(
            outer, values=["MySQL", "SQLite"], state="readonly",
            width=14, textvariable=self.db_type_var,
        )
        self.db_type_cb.grid(row=row, column=1, sticky="w", pady=pad_y)
        self.db_type_cb.bind("<<ComboboxSelected>>",
                             lambda e: self._on_db_type_change(), add="+")
        self._bind_clear_selection(self.db_type_cb)
        row += 1

        ttk.Label(outer, text="主机").grid(
            row=row, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.host_entry = ttk.Entry(outer, textvariable=self.host_var)
        self.host_entry.grid(row=row, column=1, sticky="we", pady=pad_y)

        ttk.Label(outer, text="端口").grid(
            row=row, column=2, sticky="e", padx=gap_x, pady=pad_y)
        self.port_entry = ttk.Entry(outer, textvariable=self.port_var, width=8)
        self.port_entry.grid(row=row, column=3, sticky="w", pady=pad_y)
        row += 1

        ttk.Label(outer, text="用户名").grid(
            row=row, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.user_entry = ttk.Entry(outer, textvariable=self.user_var)
        self.user_entry.grid(row=row, column=1, columnspan=3, sticky="we", pady=pad_y)
        row += 1

        ttk.Label(outer, text="密码").grid(
            row=row, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.password_entry = ttk.Entry(outer, textvariable=self.password_var)
        self.password_entry.grid(row=row, column=1, columnspan=3, sticky="we", pady=pad_y)
        row += 1

        ttk.Label(outer, text="数据库名/文件").grid(
            row=row, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.database_cb = self._make_combobox(
            outer, state="readonly", textvariable=self.database_var,
        )
        self.database_cb.grid(row=row, column=1, sticky="we", pady=pad_y)
        self.database_cb.bind(
            "<<ComboboxSelected>>",
            lambda e: self._load_tables_for_current_db(), add="+")
        self.database_cb.bind(
            "<Return>",
            lambda e: self._load_tables_for_current_db())
        self._bind_clear_selection(self.database_cb)

        db_btn_row = ttk.Frame(outer)
        db_btn_row.grid(row=row, column=2, columnspan=2, sticky="w",
                        padx=(self._px(16), 0), pady=pad_y)
        self.db_action_btn = ttk.Button(
            db_btn_row, text="连接", command=self._on_db_action, width=8)
        self.db_action_btn.pack(side=tk.LEFT)
        row += 1

        ttk.Label(outer, text="数据表").grid(
            row=row, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.table_cb = self._make_combobox(
            outer, values=[], state="readonly", textvariable=self.table_var,
        )
        self.table_cb.grid(row=row, column=1, columnspan=3,
                           sticky="we", pady=pad_y)
        self._bind_clear_selection(self.table_cb)
        row += 1

        ttk.Label(outer, text="输出文件").grid(
            row=row, column=0, sticky="e", padx=pad_x, pady=pad_y)
        self.outfile_entry = ttk.Entry(outer, textvariable=self.outfile_var)
        self.outfile_entry.grid(row=row, column=1, columnspan=2,
                                sticky="we", pady=pad_y)
        self.outfile_browse_btn = ttk.Button(
            outer, text="浏览…", command=self._browse_outfile, width=8)
        self.outfile_browse_btn.grid(
            row=row, column=3, sticky="w", padx=(self._px(16), 0), pady=pad_y)
        row += 1

        outer.rowconfigure(row, weight=1)
        row += 1

        bottom = ttk.Frame(outer)
        bottom.grid(row=row, column=0, columnspan=4, sticky="we",
                    pady=(self._px(20), 0))
        bottom.columnconfigure(0, weight=1)

        status_frame = ttk.Frame(bottom)
        status_frame.grid(row=0, column=0, sticky="w")

        self.status_prefix = tk.Label(
            status_frame, text="就绪", fg=FG_MUTED, bg=BG_PAGE,
            font=(self._family, 10), anchor="w")
        self.status_prefix.pack(side=tk.LEFT)

        self.status_detail = tk.Label(
            status_frame, text="", fg=FG_DETAIL, bg=BG_PAGE,
            font=(self._family, 10), anchor="w")
        self.status_detail.pack(side=tk.LEFT, padx=(self._px(6), 0))

        self.generate_btn = ttk.Button(
            bottom, text="生成模型", command=self._generate,
            style="Accent.TButton")
        self.generate_btn.grid(row=0, column=1, sticky="e")

    def _bind_clear_selection(self, cb):
        def handler(_e=None):
            def clear():
                try:
                    cb.selection_clear()
                except Exception:
                    try:
                        cb.select_clear()
                    except Exception:
                        pass
                try:
                    cb.icursor(tk.END)
                except Exception:
                    pass
            cb.after_idle(clear)
        cb.bind("<<ComboboxSelected>>", handler, add="+")
        cb.bind("<FocusIn>", lambda e: cb.after_idle(
            lambda: (cb.selection_clear(), cb.icursor(tk.END))), add="+")

    def _on_db_type_change(self):
        is_sqlite = self.db_type_var.get() == "SQLite"
        state = "disabled" if is_sqlite else "normal"
        for w in (self.host_entry, self.port_entry,
                  self.user_entry, self.password_entry):
            w.configure(state=state)

        self.db_action_btn.configure(text="浏览…" if is_sqlite else "连接")
        self.database_cb.configure(state="normal" if is_sqlite else "readonly")

        self.database_var.set("")
        self.database_cb.configure(values=[])

        self._db_url = None
        self._tables = []
        self.table_cb.configure(values=[])
        self.table_var.set("")
        self._set_status("就绪", prefix_color=FG_MUTED)

    def _on_db_action(self):
        if self.db_type_var.get() == "SQLite":
            self._browse_sqlite_file()
        else:
            self._connect_mysql()

    def _browse_sqlite_file(self):
        path = filedialog.askopenfilename(
            title="选择 SQLite 数据库文件",
            parent=self.root,
            filetypes=[("SQLite 数据库", "*.db *.sqlite *.sqlite3"),
                       ("所有文件", "*.*")],
        )
        if path:
            self.database_var.set(path)
            self._load_tables_for_current_db()

    def _browse_outfile(self):
        current = self.outfile_var.get()
        path = filedialog.asksaveasfilename(
            title="选择输出文件",
            parent=self.root,
            defaultextension=".py",
            initialdir=os.path.dirname(current) or os.path.expanduser("~"),
            initialfile=os.path.basename(current) or "models.py",
            filetypes=[("Python 文件", "*.py"), ("所有文件", "*.*")],
        )
        if path:
            self.outfile_var.set(path)

    def _set_status(self, prefix, detail="",
                    prefix_color=FG_MUTED, detail_color=FG_DETAIL):
        self.status_prefix.configure(text=prefix, fg=prefix_color)
        self.status_detail.configure(text=detail, fg=detail_color)

    def _set_busy(self, busy, msg="", color=FG_MUTED):
        """
        忙状态只禁用“会触发任务”的两个按钮 + 等待光标。
        输入控件保持可用——参数变了不影响已提交的后台任务，
        重复点击由 _run_async 内部的 self._busy 判断拦截。
        这样避免了整屏控件禁用/恢复带来的闪烁。
        """
        self._busy = busy
        state = "disabled" if busy else "normal"
        self.db_action_btn.configure(state=state)
        self.generate_btn.configure(state=state)
        self.generate_btn.configure(text="生成中…" if busy else "生成模型")

        # 等待光标：给用户明确的“正在处理”反馈，但不重绘任何控件
        try:
            self.root.configure(cursor="wait" if busy else "")
        except Exception:
            pass

        if msg:
            self._set_status(msg, prefix_color=color)

    def _collect_conn_params(self):
        return {
            "host": self.host_var.get(),
            "port": self.port_var.get(),
            "user": self.user_var.get(),
            "password": self.password_var.get(),
            "database": self.database_var.get(),
        }

    # ----------------------------- 连接 / 加载 ----------------------------- #
    def _connect_mysql(self):
        try:
            server_url = build_server_url(self._collect_conn_params())
        except ValueError as exc:
            self._show_message("参数错误", str(exc), "warning")
            return

        self._set_status("正在连接…", prefix_color=FG_TEXT)
        self._run_async(
            work=lambda: load_databases(server_url),
            on_ok=self._on_connect_done,
            on_err=self._on_connect_error,
        )

    def _on_connect_done(self, dbs):
        self.database_cb.configure(values=dbs)
        if dbs:
            self.database_var.set(dbs[0])
            self._set_status(
                "连接成功", f"共 {len(dbs)} 个数据库",
                FG_SUCCESS, FG_DETAIL,
            )
            self._load_tables_for_current_db()
        else:
            self.database_var.set("")
            self._set_status(
                "连接成功", "（服务器上没有数据库）",
                FG_SUCCESS, FG_DETAIL,
            )

    def _on_connect_error(self, _exc=None):
        self._set_status("连接失败", prefix_color=FG_ERROR)
        self._show_message("连接失败", "连接失败，请检查连接信息", "error")

    def _load_tables_for_current_db(self):
        try:
            db_url = build_db_url(self.db_type_var.get(), self._collect_conn_params())
        except ValueError:
            return

        self._set_status("正在加载数据表…", prefix_color=FG_TEXT)
        self._run_async(
            work=lambda: (db_url, load_tables(db_url)),
            on_ok=lambda pair: self._on_load_tables_done(*pair),
            on_err=self._on_load_tables_error,
        )

    def _on_load_tables_done(self, db_url, tables):
        self._db_url = db_url
        self._tables = tables

        if not tables:
            self.table_cb.configure(values=[])
            self.table_var.set("")
            self._set_status(
                "连接成功", "（数据库中没有表）",
                FG_SUCCESS, FG_DETAIL,
            )
            return

        self.table_cb.configure(values=tables)
        self.table_var.set(tables[0])
        self._set_status(
            "连接成功", f"共 {len(tables)} 张表",
            FG_SUCCESS, FG_DETAIL,
        )

    def _on_load_tables_error(self, _exc=None):
        self._db_url = None
        self._tables = []
        self.table_cb.configure(values=[])
        self.table_var.set("")
        self._set_status("连接失败", prefix_color=FG_ERROR)
        self._show_message("连接失败", "连接失败，请检查连接信息", "error")

    # ----------------------------- 生成 ----------------------------- #
    def _generate(self):
        if not self._db_url:
            self._show_message("提示", "请先连接数据库并选择数据表", "warning")
            return
        table = self.table_var.get().strip()
        if not table:
            self._show_message("提示", "请选择一张数据表", "warning")
            return
        outfile = self.outfile_var.get().strip()
        if not outfile:
            self._show_message("提示", "请指定输出文件路径", "warning")
            return

        self._set_status("正在生成…", prefix_color=FG_TEXT)
        self._run_async(
            work=lambda: run_sqlacodegen(self._db_url, table, outfile),
            on_ok=lambda result: self._on_generate_done(result, table, outfile),
            on_err=self._on_generate_error,
        )

    def _on_generate_done(self, result, table, outfile):
        if result.returncode == 0:
            abs_path = os.path.abspath(outfile)
            self._set_status("生成成功", abs_path, FG_SUCCESS, FG_DETAIL)
            self._show_message(
                "生成成功",
                f"表 {table} 的模型已生成到：\n{abs_path}",
                "info",
            )
        elif result.returncode == 124:
            self._set_status("生成超时", prefix_color=FG_ERROR)
            self._show_message(
                "生成超时",
                (result.stderr or f"sqlacodegen 未在 {GEN_TIMEOUT} 秒内返回")[:1500],
                "error",
            )
        else:
            self._set_status("生成失败", prefix_color=FG_ERROR)
            msg = (result.stderr or "").strip() \
                  or (result.stdout or "").strip() \
                  or "(无输出)"
            self._show_message(
                "生成失败",
                f"sqlacodegen 返回码：{result.returncode}\n\n{msg[:1500]}",
                "error",
            )

    def _on_generate_error(self, exc):
        self._set_status("生成失败", prefix_color=FG_ERROR)
        message = str(exc)
        if isinstance(exc, FileNotFoundError):
            message = ("找不到 sqlacodegen 可执行环境，请先安装：\n"
                       "pip install sqlacodegen")
        self._show_message("错误", message[:1500], "error")