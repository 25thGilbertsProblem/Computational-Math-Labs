from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from interpolation.differences import difference_table_rows


class RightPanel(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master, padding=10)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)

        self.result_box = tk.Text(self, height=8, wrap="word")
        self.result_box.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        body = ttk.PanedWindow(self, orient=tk.VERTICAL)
        body.grid(row=1, column=0, sticky="nsew")

        tables_frame = ttk.Frame(body)
        tables_frame.columnconfigure(0, weight=1)
        tables_frame.rowconfigure(0, weight=1)
        tables_frame.rowconfigure(1, weight=1)

        plot_frame = ttk.LabelFrame(body, text="График")
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)

        body.add(tables_frame, weight=1)
        body.add(plot_frame, weight=4)

        self.diff_table_frame = ttk.LabelFrame(tables_frame, text="Таблица конечных разностей")
        self.diff_table_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        self.diff_table_frame.columnconfigure(0, weight=1)

        self.plot_container = plot_frame
        self.plot_container.rowconfigure(0, weight=1)
        self.plot_container.columnconfigure(0, weight=1)

        self.diff_table = None
        self.canvas_widget = None
        self.figure = None

    def set_result_text(self, text: str) -> None:
        self.result_box.delete("1.0", tk.END)
        self.result_box.insert(tk.END, text)

    def _create_tree(self, parent, columns, heading_labels):
        for child in parent.winfo_children():
            child.destroy()

        frame = ttk.Frame(parent)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        index = 0
        while index < len(columns):
            tree.heading(columns[index], text=heading_labels[index])
            tree.column(columns[index], width=90, anchor="center")
            index += 1

        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        return tree

    def set_difference_table(self, x, y) -> None:
        rows = difference_table_rows(x, y)
        if len(rows) == 0:
            for child in self.diff_table_frame.winfo_children():
                child.destroy()
            return

        ncols = len(rows[0])
        columns = []
        headings = []

        index = 0
        while index < ncols:
            columns.append(f"c{index}")
            if index == 0:
                headings.append("x")
            elif index == 1:
                headings.append("y")
            elif index == 2:
                headings.append("Δy")
            else:
                headings.append(f"Δ^{index - 1}y")
            index += 1

        self.diff_table = self._create_tree(self.diff_table_frame, tuple(columns), headings)
        for row in rows:
            self.diff_table.insert("", tk.END, values=row)

    def clear_difference_table(self) -> None:
        for child in self.diff_table_frame.winfo_children():
            child.destroy()
        self.diff_table = None

    def set_plot(self, figure: Figure) -> None:
        if self.canvas_widget is not None:
            self.canvas_widget.get_tk_widget().destroy()

        self.figure = figure
        canvas = FigureCanvasTkAgg(figure, master=self.plot_container)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas_widget = canvas

    def clear_plot(self) -> None:
        if self.canvas_widget is not None:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None
        self.figure = None
