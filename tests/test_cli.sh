#!/bin/bash
cd "$(dirname "$0")/.."
echo "ТЕСТ 1: Все параметры заданы"
python3 src/main.py --vfs test_vfs.xml --config config.toml --script test_script.txt
read -p "Закройте окно и нажмите Enter..."

echo "ТЕСТ 2: Задан конфиг"
python3 src/main.py --config config.toml
read -p "Закройте окно и нажмите Enter..."

echo "ТЕСТ 3: Приоритет CLI над TOML"
python3 src/main.py --config config.toml --vfs override_from_cli.zip
read -p "Закройте окно и нажмите Enter..."

echo "ТЕСТ 4: Ошибка чтения конфига"
python3 src/main.py --config missing.toml
read -p "Нажмите Enter..."

echo "ТЕСТ 5: Остановка скрипта при ошибке"
python3 src/main.py --script tests/script.txt