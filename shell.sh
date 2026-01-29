#!/bin/bash
VENV_PATH="$HOME/pyenv/wagtail-show-test"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

"$VENV_PATH/bin/python" "$PROJECT_DIR/manage.py" shell
