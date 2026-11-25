"""Об'єднання двох PDF-файлів в один (Windows, Python + tkinter + pypdf)."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pypdf import PdfReader, PdfWriter


def merge_pdfs(first: str, second: str, output: str) -> int:
    """Об'єднує два PDF у один файл. Повертає загальну кількість сторінок."""
    writer = PdfWriter()
    for path in (first, second):
        reader = PdfReader(path)
        if reader.is_encrypted:
            # порожній пароль працює для PDF, захищених лише від редагування
            if not reader.decrypt(""):
                raise ValueError(
                    f"Файл захищено паролем:\n{os.path.basename(path)}"
                )
        writer.append(reader)
    with open(output, "wb") as f:
        writer.write(f)
    return len(writer.pages)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Об'єднання PDF")
        self.geometry("620x260")
        self.minsize(520, 240)

        self.first = tk.StringVar()
        self.second = tk.StringVar()

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Перший PDF:").grid(row=0, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.first).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(frame, text="Обрати…", command=lambda: self.pick(self.first)).grid(row=0, column=2)

        ttk.Label(frame, text="Другий PDF:").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.second).grid(row=1, column=1, sticky="ew", padx=8)
        ttk.Button(frame, text="Обрати…", command=lambda: self.pick(self.second)).grid(row=1, column=2)

        ttk.Button(frame, text="⇅ Поміняти місцями", command=self.swap).grid(
            row=2, column=1, sticky="w", padx=8, pady=4
        )

        ttk.Button(frame, text="Об'єднати та зберегти…", command=self.merge).grid(
            row=3, column=0, columnspan=3, pady=18, ipadx=12, ipady=6
        )

        self.status = ttk.Label(frame, text="Оберіть два PDF-файли.", foreground="gray")
        self.status.grid(row=4, column=0, columnspan=3, sticky="w")

    def pick(self, var):
        path = filedialog.askopenfilename(
            title="Оберіть PDF-файл",
            filetypes=[("PDF-файли", "*.pdf"), ("Усі файли", "*.*")],
        )
        if path:
            var.set(os.path.normpath(path))

    def swap(self):
        a, b = self.first.get(), self.second.get()
        self.first.set(b)
        self.second.set(a)

    def merge(self):
        first, second = self.first.get().strip(), self.second.get().strip()
        if not first or not second:
            messagebox.showwarning("Увага", "Оберіть обидва PDF-файли.")
            return
        for p in (first, second):
            if not os.path.isfile(p):
                messagebox.showerror("Помилка", f"Файл не знайдено:\n{p}")
                return

        initial = os.path.splitext(os.path.basename(first))[0] + "_об'єднаний.pdf"
        output = filedialog.asksaveasfilename(
            title="Зберегти результат як",
            defaultextension=".pdf",
            initialdir=os.path.dirname(first),
            initialfile=initial,
            filetypes=[("PDF-файли", "*.pdf")],
        )
        if not output:
            return
        output = os.path.normpath(output)
        if os.path.normcase(output) in (os.path.normcase(first), os.path.normcase(second)):
            messagebox.showerror("Помилка", "Не можна зберігати поверх вхідного файлу.")
            return

        try:
            self.config(cursor="watch")
            self.update_idletasks()
            pages = merge_pdfs(first, second, output)
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Помилка", f"Не вдалося об'єднати файли:\n{e}")
            self.status.config(text="Помилка.", foreground="red")
            return
        finally:
            self.config(cursor="")

        self.status.config(text=f"Готово: {pages} стор. → {output}", foreground="green")
        messagebox.showinfo("Готово", f"Файли об'єднано.\nСторінок: {pages}\n\n{output}")


if __name__ == "__main__":
    App().mainloop()
