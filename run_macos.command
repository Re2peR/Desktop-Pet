#!/bin/zsh
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
  echo "未找到 Python 3。请先安装 Python 3.10 或更新版本。"
  echo "https://www.python.org/downloads/macos/"
  read -k 1 "?按任意键退出…"
  exit 1
fi

if [ ! -x ".venv-macos/bin/python" ]; then
  python3 -m venv .venv-macos
  .venv-macos/bin/python -m pip install --upgrade pip
  .venv-macos/bin/python -m pip install -r requirements.txt
fi

exec .venv-macos/bin/python main.py
