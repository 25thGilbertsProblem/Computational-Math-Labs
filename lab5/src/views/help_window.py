from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class HelpWindow:
    def __init__(self, master: tk.Misc):
        self.window = tk.Toplevel(master)
        self.window.title("Справка")
        self.window.geometry("640x360")
        self.window.transient(master)
        self.window.grab_set()

        text = (
            "Программа выполняет интерполяцию функции по табличным данным.\n\n"
            "Поддерживается ввод:\n"
            "• с клавиатуры через таблицу;\n"
            "• из файла;\n"
            "• по заданной функции.\n\n"
            "Результаты вычисляются методами Лагранжа, Ньютона и Гаусса.\n"
            "При вводе с клавиатуры и из файла точки автоматически сортируются по x.\n"
            "Повторяющиеся значения x недопустимы."
        )

        label = ttk.Label(self.window, text=text, justify="left", padding=16)
        label.pack(fill="both", expand=True)
