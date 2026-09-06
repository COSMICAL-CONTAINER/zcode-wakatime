# -*- coding: utf-8 -*-
"""ZCode → WakaTime 心跳钩子：把 ZCode 的使用时长计入 WakaTime。

由 ZCode 钩子（UserPromptSubmit / PostToolUse）以 process 方式调用：
  python zcode_wakatime_hook.py
钩子事件信息从 stdin JSON 读取（取 cwd 作为项目），本脚本立即返回，
真正的 wakatime-cli 调用以分离进程在后台完成，不阻塞会话。

节流：同一项目 120 秒内只发一条心跳（WakaTime 插件标准行为），
状态保存在 ~/.wakatime/zcode-wakatime/ 下的 marker 文件 mtime 里。
"""
import hashlib
import json
import os
import subprocess
import sys
import time

HOME = os.path.expanduser("~")
STATE_DIR = os.path.join(HOME, ".wakatime", "zcode-wakatime")
THROTTLE_SECONDS = 60  # WakaTime 时长分组超时为 2 分钟，120s 节流会在空档处截断时长；60s 保证链条连续
PLUGIN = "zcode-wakatime/1.0.0"

CLI_CANDIDATES = [
    os.path.join(HOME, ".wakatime", "wakatime-cli-windows-amd64.exe"),
    os.path.join(HOME, ".wakatime", "wakatime-cli"),
    "wakatime-cli",  # PATH 上的
]


def find_cli():
    for p in CLI_CANDIDATES:
        if os.path.isfile(p) or any(
            os.path.isfile(os.path.join(d, p + (".exe" if os.name == "nt" else "")))
            for d in os.environ.get("PATH", "").split(os.pathsep)
        ):
            return p
    return None


def read_cwd():
    """从 stdin 的钩子 JSON / 环境变量 / 当前目录里取项目目录。"""
    try:
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")  # pythonw 下管道默认编码非 UTF-8，中文路径需显式指定
    except Exception:
        pass
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    for source in (
        (json.loads(raw).get("cwd") if raw.strip() else None),
        os.environ.get("ZCODE_PROJECT_DIR"),
        os.environ.get("CLAUDE_PROJECT_DIR"),
        os.getcwd(),
    ):
        if source and os.path.isdir(source):
            return source
    return HOME


def send(cli, project, epoch):
    args = [
        cli,
        "--entity", "ZCode",
        "--entity-type", "app",
        "--project", project,
        "--category", "coding",
        "--plugin", PLUGIN,
        "--time", str(epoch),
    ]
    flags = 0
    if os.name == "nt":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
    subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
        close_fds=True,
    )


def main():
    cli = find_cli()
    if not cli:
        sys.exit(0)  # 没有 CLI 时静默退出，不影响会话

    cwd = read_cwd()
    project = os.path.basename(os.path.normpath(cwd)) or "ZCode"
    epoch = time.time()

    os.makedirs(STATE_DIR, exist_ok=True)
    marker = os.path.join(STATE_DIR, hashlib.sha256(cwd.encode("utf-8")).hexdigest())
    try:
        last = os.path.getmtime(marker)
    except OSError:
        last = 0
    if epoch - last < THROTTLE_SECONDS:
        sys.exit(0)

    # 先记节流时间戳再发送：O_CREAT 仅在首次创建空文件，之后只更新 mtime
    fd = os.open(marker, os.O_CREAT | os.O_WRONLY, 0o644)
    os.close(fd)
    os.utime(marker, (epoch, epoch))

    send(cli, project, epoch)
    sys.exit(0)


if __name__ == "__main__":
    main()
