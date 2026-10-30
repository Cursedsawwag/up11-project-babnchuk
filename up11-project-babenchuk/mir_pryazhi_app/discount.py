"""Алгоритм расчёта цены со скидкой 25%."""
from datetime import datetime, timedelta
from config import DB_PATH
import sqlite3


def get_previous_month_range(date):
    """
    Возвращает (начало, конец) предыдущего месяца.
    :param date: дата расчёта
    :return: (start_date, end_date) в формате YYYY-MM-DD
    """
    # TODO: первое число текущего месяца
    first_day = date.replace(day=1)
    # TODO: последний день предыдущего месяца
    last_day_prev = first_day - timedelta(days=1)
    # TODO: первое число предыдущего месяца
    first_day_prev = last_day_prev.replace(day=1)
    # TODO: вернуть две даты в формате YYYY-MM-DD
    return (first_day_prev.strftime("%Y-%m-%d"), last_day_prev.strftime("%Y-%m-%d"))


def has_orders_in_previous_month(product_id, date):
    """
    Есть ли заказы товара в предыдущем месяце?
    :param product_id: id товара
    :param date: дата расчёта
    :return: True / False
    """
    # TODO: получить диапазон предыдущего месяца
    start, end = get_previous_month_range(date)
    # TODO: открыть соединение
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # TODO: выполнить SQL
    cur.execute(
        "SELECT COUNT(*) FROM Заказ WHERE товар_id = ? AND дата BETWEEN ? AND ?",
        (product_id, start, end)
    )
    # TODO: получить счётчик
    count = cur.fetchone()[0]
    conn.close()
    # TODO: вернуть результат
    return count > 0


def calculate_price_with_discount(product_id, price, date):
    """
    Рассчитывает цену со скидкой 25%.
    :param product_id: id товара
    :param price: базовая цена
    :param date: дата расчёта
    :return: цена со скидкой или без
    """
    # TODO: если есть заказы — вернуть цену без скидки
    if has_orders_in_previous_month(product_id, date):
        return price
    # TODO: иначе — цена × 0.75
    return price * 0.75
