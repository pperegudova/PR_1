#!/bin/bash
cd "$(dirname "$0")/.."

echo "ТЕСТ 1: Запуск с VFS и скриптом Этапа 4"
python3 src/main.py \
  --vfs tests/vfs_files_stage4.xml \
  --script tests/script_stage4.txt
read -p "Нажмите Enter..."