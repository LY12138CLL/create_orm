"""全局常量与配色。"""

# 隐藏 CLI 分支的入口参数（PyInstaller 打包后用 exe 自身当子进程跑 sqlacodegen）
CLI_FLAG = "--run-sqlacodegen"

# 单次生成最长等待秒数，超时后强制终止
GEN_TIMEOUT = 180

# ------------------------------ 主题配色 ------------------------------ #
BG_PAGE    = "#eef2f7"
BG_INPUT   = "#ffffff"
FG_TEXT    = "#1e293b"
FG_MUTED   = "#475569"
FG_ERROR   = "#dc2626"
FG_SUCCESS = "#16a34a"
FG_DETAIL  = "#2563eb"
ACCENT     = "#2563eb"
ACCENT_HV  = "#1d4ed8"
BORDER     = "#cbd5e1"
BORDER_FS  = "#3b82f6"