"""Модуль эмулятора оболочки ОС с графическим интерфейсом."""

import sys
import shlex
import tkinter as tk
from tkinter import scrolledtext

UI_WIDTH = 60
UI_HEIGHT = 20
PROMPT = "$ "
VFS_NAME = "VFS"


def parse_command(raw_input: str) -> list:
    """
    Разбирает строку ввода на список аргументов.
    Корректно обрабатывает аргументы в кавычках.

    Args:
        raw_input: Строка ввода от пользователя.

    Returns:
        Список аргументов или None при ошибке.
    """
    try:
        return shlex.split(raw_input)
    except ValueError:
        return None


class ShellEmulator:
    """Класс, реализующий графический интерфейс эмулятора."""

    def __init__(self, root: tk.Tk):
        """
        Инициализирует интерфейс и регистрирует команды.

        Args:
            root: Корневое окно tkinter.
        """
        self.root = root
        self.root.title(f"Эмулятор - {VFS_NAME}")
        self._setup_ui()
        self.commands = {
            "ls": self._stub_cmd,
            "cd": self._stub_cmd,
            "exit": self._exit_cmd,
        }

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

    def _write_output(self, text: str):
        """
        Выводит текст в консоль эмулятора.

        Args:
            text: Текст для отображения.
        """
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

    def _execute(self, raw_input: str):
        """
        Выполняет распарсенную команду.

        Args:
            raw_input: Сырая строка команды.
        """
        args = parse_command(raw_input)
        if not args:
            self._write_output("Ошибка: неверные аргументы.")
            return

        cmd_name = args[0]
        cmd_args = args[1:]

        if cmd_name in self.commands:
            self.commands[cmd_name](cmd_name, cmd_args)
        else:
            msg = f"Ошибка: неизвестная команда '{cmd_name}'."
            self._write_output(msg)

    def _stub_cmd(self, name: str, args: list):
        """
        Заглушка для команд ls и cd.

        Args:
            name: Имя вызванной команды.
            args: Список аргументов.
        """
        self._write_output(f"{name}: {args}")

    def _exit_cmd(self, name: str, args: list):
        """
        Завершает работу эмулятора.

        Args:
            name: Имя команды.
            args: Список аргументов.
        """
        self.root.destroy()
        sys.exit(0)


def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    ShellEmulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()