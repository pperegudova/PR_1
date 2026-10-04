"""Модуль эмулятора оболочки ОС с графическим интерфейсом."""
import sys
import os
import shlex
import argparse
import base64
import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import scrolledtext

UI_WIDTH = 60
UI_HEIGHT = 20
PROMPT = "$ "


class VFSNode:
    """Узел виртуальной файловой системы."""

    def __init__(self, name, is_dir, parent=None):
        self.name = name
        self.is_dir = is_dir
        self.children = {}
        self.content = b""
        self.parent = parent


def _parse_xml_node(xml_node, parent=None):
    """Рекурсивно строит дерево VFS из XML узла."""
    is_dir = xml_node.tag in ("dir", "vfs")
    name = xml_node.get("name")
    node = VFSNode(name, is_dir, parent)
    if not is_dir and xml_node.text:
        node.content = base64.b64decode(xml_node.text)
    for child in xml_node:
        child_node = _parse_xml_node(child, node)
        node.children[child_node.name] = child_node
    return node


def load_vfs(xml_path):
    """Загружает VFS из XML файла в память."""
    if not xml_path or not os.path.exists(xml_path):
        print(f"Error: VFS '{xml_path}' not found.")
        return None
    try:
        tree = ET.parse(xml_path)
        return _parse_xml_node(tree.getroot())
    except Exception as e:
        print(f"Error: Invalid VFS format. {e}")
        return None


def parse_command(raw_input: str) -> list:
    """
    Разбирает строку ввода на список аргументов.
    Корректно обрабатывает аргументы в кавычках.
    """
    try:
        return shlex.split(raw_input)
    except ValueError:
        return None


def parse_cli_args() -> argparse.Namespace:
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Shell Emulator"
    )
    parser.add_argument(
        "--vfs", help="Path to VFS"
    )
    parser.add_argument(
        "--script", help="Path to startup script"
    )
    parser.add_argument(
        "--config", help="Path to TOML config"
    )
    return parser.parse_args()


def load_toml_config(path: str) -> dict:
    """
    Загружает простой TOML конфиг.
    Возвращает словарь или None при ошибке.
    """
    if not path:
        return {}
    if not os.path.exists(path):
        print(f"Error: Config '{path}' not found.")
        return None
    try:
        config = {}
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    if not line.startswith('#'):
                        k, v = line.split('=', 1)
                        key = k.strip()
                        val = v.strip().strip('"\'')
                        config[key] = val
        return config
    except Exception as e:
        print(f"Error reading config: {e}")
        return None


def merge_configs(toml_cfg: dict, cli_args: argparse.Namespace) -> dict:
    """
    Объединяет конфигурации.
    Аргументы CLI имеют приоритет над TOML файлом.
    """
    if toml_cfg is None:
        toml_cfg = {}

    vfs = cli_args.vfs or toml_cfg.get("vfs_path")
    script = cli_args.script or toml_cfg.get("script_path")

    return {
        "vfs_path": vfs,
        "script_path": script
    }


class ShellEmulator:
    """Класс, реализующий графический интерфейс эмулятора."""

    def __init__(self, root: tk.Tk, config: dict):
        """
        Инициализирует интерфейс, региструет команды и запускает скрипт.
        """
        self.root = root
        self.config = config

        vfs_path = self.config.get("vfs_path")
        self.vfs_root = load_vfs(vfs_path)

        if not self.vfs_root:
            self.vfs_root = VFSNode("root", True)

        if vfs_path:
            file_name = os.path.basename(vfs_path)
            vfs_display_name, _ = os.path.splitext(file_name)
        else:
            vfs_display_name = "Default VFS"

        self.root.title(f"Эмулятор - {vfs_display_name}")

        self.current_dir = self.vfs_root
        self._setup_ui()
        self._register_commands()
        self._print_debug_info()
        self._run_startup_script()

    def _setup_ui(self):
        """Создает текстовую область и поле ввода."""
        self.output = scrolledtext.ScrolledText(
            self.root, width=UI_WIDTH, height=UI_HEIGHT
        )
        self.output.pack()
        self.output.config(state=tk.DISABLED)

        self.entry = tk.Entry(self.root)
        self.entry.pack(fill=tk.X)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.focus()

    def _register_commands(self):
        """Регистрирует доступные команды эмулятора."""
        self.commands = {
            "ls": self._ls_cmd,
            "cd": self._cd_cmd,
            "exit": self._exit_cmd,
        }

    def _print_debug_info(self):
        """Выводит отладочную информацию о загруженных параметрах."""
        self._write_output("--- Отладочный вывод ---")
        vfs_msg = f"VFS Path: {self.config.get('vfs_path')}"
        self._write_output(vfs_msg)
        scr_msg = f"Script Path: {self.config.get('script_path')}"
        self._write_output(scr_msg)
        self._write_output("------------------")

    def _run_startup_script(self):
        """Выполняет стартовый скрипт, отображая процесс в GUI."""
        path = self.config.get("script_path")
        if not path or not os.path.exists(path):
            return

        msg = f"Запуск стартового скрипта: {path}"
        self._write_output(msg)

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                cmd = line.strip()
                if not cmd or cmd.startswith("#"):
                    continue

                self._write_output(f"{PROMPT}{cmd}")
                success = self._execute(cmd)

                if not success:
                    err_msg = "Скрипт остановлен из-за ошибки."
                    self._write_output(err_msg)
                    break

    def _write_output(self, text: str):
        """Безопасно добавляет текст в текстовое поле вывода."""
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n")
        self.output.config(state=tk.DISABLED)
        self.output.see(tk.END)

    def _on_enter(self, event):
        """Обрабатывает нажатие клавиши Enter."""
        raw = self.entry.get()
        self.entry.delete(0, tk.END)
        self._write_output(f"{PROMPT}{raw}")
        self._execute(raw)

    def _resolve_path(self, path_str):
        """Ищет узел VFS по относительному или абсолютному пути."""
        if path_str == "/":
            return self.vfs_root
        parts = path_str.strip("/").split("/")
        current = self.vfs_root
        if not path_str.startswith("/"):
            current = self.current_dir
        for part in parts:
            if not part:
                continue
            if part == "..":
                if current.parent:
                    current = current.parent
            elif part == ".":
                continue
            elif part in current.children:
                child = current.children[part]
                if not child.is_dir:
                    return None
                current = child
            else:
                return None
        return current

    def _execute(self, raw_input: str) -> bool:
        """
        Выполняет распарсенную команду.
        Возвращает True при успехе, False при ошибке.
        """
        args = parse_command(raw_input)
        if not args:
            self._write_output("Ошибка: неверные аргументы.")
            return False

        cmd_name = args[0]
        cmd_args = args[1:]

        if cmd_name in self.commands:
            return self.commands[cmd_name](cmd_name, cmd_args)

        msg = f"Ошибка: неизвестная команда '{cmd_name}'."
        self._write_output(msg)
        return False

    def _ls_cmd(self, name: str, args: list) -> bool:
        """Выводит содержимое текущей директории VFS."""
        path = args[0] if args else "."
        target = self._resolve_path(path)
        if not target or not target.is_dir:
            self._write_output(f"ls: cannot access '{path}'")
            return False
        for child in target.children.values():
            prefix = "d" if child.is_dir else "-"
            self._write_output(f"{prefix} {child.name}")
        return True

    def _cd_cmd(self, name: str, args: list) -> bool:
        """Меняет текущую директорию в VFS."""
        if not args:
            return True
        target = self._resolve_path(args[0])
        if target and target.is_dir:
            self.current_dir = target
            return True
        self._write_output(f"cd: {args[0]}: No such directory")
        return False

    def _exit_cmd(self, name: str, args: list) -> bool:
        """Завершает работу эмулятора."""
        self.root.destroy()
        sys.exit(0)


def main():
    """Точка входа в приложение."""
    cli_args = parse_cli_args()
    toml_cfg = load_toml_config(cli_args.config)

    if toml_cfg is None and cli_args.config:
        sys.exit(1)

    final_config = merge_configs(toml_cfg, cli_args)

    root = tk.Tk()
    ShellEmulator(root, final_config)
    root.mainloop()


if __name__ == "__main__":
    main()