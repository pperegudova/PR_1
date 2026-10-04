#!/bin/bash
cd "$(dirname "$0")/.."

echo "ТЕСТ 1: Минимальный VFS"
python3 src/main.py --vfs tests/vfs_minimal.xml
read -p "Закройте окно и нажмите Enter..."

echo "ТЕСТ 2: VFS с файлами и папками"
python3 src/main.py --vfs tests/vfs_files.xml
read -p "Закройте окно и нажмите Enter..."

echo "ТЕСТ 3: Глубокая вложенность (3 уровня)"
python3 src/main.py --vfs tests/vfs_deep.xml --script tests/script_stage3.txt
read -p "Закройте окно и нажмите Enter..."

echo "ТЕСТ 4: Ошибка загрузки (файл не найден)"
python3 src/main.py --vfs missing_vfs.xml
read -p "Нажмите Enter..."