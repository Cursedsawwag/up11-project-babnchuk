"""Окно списка заказов."""
import tkinter as tk
from tkinter import ttk, messagebox
from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, font
)
import order_manager as om


class OrdersWindow:
    """Окно списка заказов."""

    def __init__(self, parent, current_user=None):
        self.current_user = current_user

        self.window = tk.Toplevel(parent)
        self.window.title("Список заказов")
        self.window.geometry("800x500")
        self.window.configure(bg=COLOR_MAIN_BG)

        self.build_ui()
        self.load_orders()

    def is_admin(self):
        """Проверяет роль Администратора."""
        return (self.current_user and
                self.current_user[5] == "Администратор")

    def build_ui(self):
        """Строит интерфейс."""
        # Шапка — ГОТОВО

        columns = ("id", "date", "client")
        self.tree = ttk.Treeview(self.window, columns=("id", "date", "client"),
                                  show="headings", height=15)
        self.tree.heading("id", text="№")
        self.tree.heading("date", text="Дата")
        self.tree.heading("client", text="Клиент")
        self.tree.column("id", width=50)
        self.tree.column("date", width=120)
        self.tree.column("client", width=400)
        self.tree.pack(fill="x", expand=True, padx=20, pady=20)
        self.tree.bind("<Double-1>", self.on_order_select)

        btn_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="Просмотр состава",
                  command=self.load_orders , bg=COLOR_ACCENT, fg="white").pack(side="left")
        tk.Button(btn_frame, text="Обновить",
                  command=self.load_orders , bg=COLOR_ACCENT, fg="white").pack(side="left")
        tk.Button(btn_frame, text="Назад",
                  command=self.window.destroy, bg=COLOR_ACCENT, fg="white").pack(side="right")

    def load_orders(self):
        """Загружает заказы из БД."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        orders = om.get_all_orders()
        for order in orders:
            self.tree.insert("", tk.END,iid=order[0], values=order)

    def on_order_select(self, event=None):
        """Обработчик выбора заказа."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите заказ")
            return
        item = selected[0]
        order_id = int(item)
        from order_items_window import OrderItemsWindow
        OrderItemsWindow (self.window, order_id, self.current_user)
