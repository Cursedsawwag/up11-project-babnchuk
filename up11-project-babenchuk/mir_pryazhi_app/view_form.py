"""Форма просмотра товара."""
import tkinter as tk
from tkinter import messagebox
from styles import (
    COLOR_MAIN_BG, COLOR_SECONDARY_BG, COLOR_ACCENT,
    FONT_SIZE_NORMAL, FONT_SIZE_TITLE, font
)
from resources import get_product_image
from database import get_product_quantity
from order_manager import create_order
from error_handler import validate_positive_int


class ViewForm:
    """Форма просмотра товара."""

    def __init__(self, parent, product, on_add_to_order=None):
        self.product = product
        self.on_add_to_order = on_add_to_order

        self.window = tk.Toplevel(parent)
        self.window.title(f"Просмотр — {product[1]}")
        self.window.geometry("700x600")
        self.window.configure(bg=COLOR_MAIN_BG)

        self.build_ui()

    def build_ui(self):
        """Строит интерфейс формы."""
        # Шапка с названием
        header = tk.Label(
            self.window,
            text=self.product[1] or "[Без названия]",
            font=font(FONT_SIZE_TITLE, bold=True),
            bg=COLOR_MAIN_BG, fg=COLOR_ACCENT
        )
        header.pack(pady=10)

        # Картинка (если есть)
        photo = get_product_image(self.product[7], size=(150, 150))
        if photo:
            img_label = tk.Label(self.window, image=photo, bg=COLOR_MAIN_BG)
            img_label.image = photo   # ← держим ссылку!
            img_label.pack(pady=5)

        # Блок полей
        info = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        info.pack(fill="x", padx=20, pady=10)

        self._add_field(info, "Производитель", self.product[2] or "—")
        self._add_field(info, "Категория",     self.product[3] or "—")
        self._add_field(info, "Характеристики", self.product[4] or "—")
        self._add_field(info, "Цена",          f"{self.product[5]} руб.")
        self._add_field(info, "В наличии",     get_product_quantity(self.product[0]))

        # Поле ввода количества
        qty_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        qty_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(qty_frame, text="Количество:", font=font(bold=True),
                 bg=COLOR_MAIN_BG).pack(side="left")

        self.qty_var = tk.StringVar(value="1")
        tk.Entry(qty_frame, textvariable=self.qty_var, width=10).pack(side="left", padx=10)

        # Кнопки
        btn_frame = tk.Frame(self.window, bg=COLOR_MAIN_BG)
        btn_frame.pack(fill="x", padx=20, pady=20)

        tk.Button(btn_frame, text="Добавить в заказ",
                  command=self.add_to_order,
                  bg=COLOR_ACCENT, fg="white", width=20).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Закрыть",
                  command=self.window.destroy,
                  bg=COLOR_SECONDARY_BG, fg="white", width=15).pack(side="left", padx=5)

    def _add_field(self, parent, label, value):
        """
        Добавляет поле в форму.
        :param parent: родительский фрейм
        :param label: название поля
        :param value: значение
        """
        # TODO: создать фрейм строки

        row = tk.Frame(parent, bg=COLOR_MAIN_BG)
        row.pack(fill="x", pady=2)
        # TODO: метка с label: — жирно, ширина 15
        tk.Label(row, text=f"{label}:", font=font(bold=True),
                 width=15, anchor="w").pack(side="left")
        # TODO: метка со значением
        tk.Label(row, text=str(value), font=font(),
                 anchor="w").pack(side="left")

    def add_to_order(self):
        print("DWDDW")
        """Обработчик кнопки «Добавить в заказ»."""
        if not self.product:
            messagebox.showerror("Ошибка", "Товар не выбран")
            return
        ok, result = validate_positive_int(self.qty_var.get(), "Количество")
        if not ok:
            messagebox.showerror("Ошибка ввода", result)
            return
        qty = result
        current_qty = get_product_quantity(self.product[0])
        if qty > current_qty:
            messagebox.showwarning("Ошибка", f"Доступно только {current_qty} шт.")
            return
        try:
            items = [(self.product[0], self.product[8], qty, self.product[5])]
            order_id = create_order("Клиент", items)
            print("orderID: " + str(order_id))
            if order_id:
                messagebox.showinfo("Успех", f"Заказ №{order_id} оформлен")
                if self.on_add_to_order:
                    self.on_add_to_order()
                self.window.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка заказа:\n{e}")
