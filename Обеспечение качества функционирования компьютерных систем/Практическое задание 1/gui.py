import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from logic import (calculate_total_value, calculate_total_quantity,
                   filter_by_category, filter_by_quantity, search_items,
                   get_statistics)
from storage import load_data, save_data, export_to_csv

CATEGORIES = ["Электроника", "Мебель", "Одежда", "Продукты", "Прочее", ""]


class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт товаров на складе")
        self.root.geometry("1000x600")

        self.items = load_data()
        self.current_items = self.items.copy()

        self._build_ui()
        self._refresh_table()

    def _build_ui(self):
        # Вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_items = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_items, text="Товары")
        self.notebook.add(self.tab_stats, text="Статистика")

        # Автообновление статистики при переключении вкладки
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._build_items_tab()
        self._build_stats_tab()

    def _build_items_tab(self):
        # Форма ввода
        form = ttk.LabelFrame(self.tab_items, text="Добавить товар")
        form.pack(fill="x", padx=10, pady=5)

        ttk.Label(form, text="Артикул:").grid(row=0, column=0, padx=5, pady=2)
        self.entry_article = ttk.Entry(form)
        self.entry_article.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(form, text="Наименование:").grid(row=0, column=2, padx=5, pady=2)
        self.entry_name = ttk.Entry(form)
        self.entry_name.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(form, text="Категория:").grid(row=1, column=0, padx=5, pady=2)
        self.combo_category = ttk.Combobox(form, values=CATEGORIES)
        self.combo_category.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(form, text="Количество:").grid(row=1, column=2, padx=5, pady=2)
        self.entry_quantity = ttk.Entry(form)
        self.entry_quantity.grid(row=1, column=3, padx=5, pady=2)

        ttk.Label(form, text="Цена:").grid(row=2, column=0, padx=5, pady=2)
        self.entry_price = ttk.Entry(form)
        self.entry_price.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(form, text="Дата (ДД.ММ.ГГГГ):").grid(row=2, column=2, padx=5, pady=2)
        self.entry_date = ttk.Entry(form)
        self.entry_date.grid(row=2, column=3, padx=5, pady=2)

        ttk.Label(form, text="Комментарий:").grid(row=3, column=0, padx=5, pady=2)
        self.entry_comment = ttk.Entry(form)
        self.entry_comment.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=2)

        # ДЕФЕКТ 8: кнопка не блокируется после нажатия
        btn_add = ttk.Button(form, text="Добавить", command=self.add_item)
        btn_add.grid(row=4, column=0, columnspan=4, pady=5)

        # Панель фильтров
        filters = ttk.LabelFrame(self.tab_items, text="Фильтры и поиск")
        filters.pack(fill="x", padx=10, pady=5)

        # Поиск — динамический
        ttk.Label(filters, text="Поиск:").grid(row=0, column=0, padx=5)
        self.entry_search = ttk.Entry(filters)
        self.entry_search.grid(row=0, column=1, padx=5)
        self.entry_search.bind("<KeyRelease>", lambda e: self.do_search())

        # Категория — динамическая
        ttk.Label(filters, text="Категория:").grid(row=0, column=3, padx=5)
        self.combo_filter_cat = ttk.Combobox(filters, values=["Все"] + CATEGORIES)
        self.combo_filter_cat.set("Все")
        self.combo_filter_cat.grid(row=0, column=4, padx=5)
        self.combo_filter_cat.bind("<<ComboboxSelected>>", lambda e: self.do_filter())

        # Количество — динамическое
        ttk.Label(filters, text="Кол-во ≤:").grid(row=0, column=6, padx=5)
        self.entry_filter_qty = ttk.Entry(filters, width=8)
        self.entry_filter_qty.grid(row=0, column=7, padx=5)
        self.entry_filter_qty.bind("<KeyRelease>", lambda e: self.do_filter_qty())

        ttk.Button(filters, text="Сбросить", command=self.reset_filters).grid(row=0, column=9, padx=5)

        # Таблица
        columns = ("article", "name", "category", "quantity", "price", "total", "date")
        self.tree = ttk.Treeview(self.tab_items, columns=columns, show="headings")
        for col, title in zip(columns, ["Артикул", "Наименование", "Категория",
                                         "Кол-во", "Цена", "Сумма", "Дата"]):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Кнопки действий (кнопка «Сохранить» убрана)
        actions = ttk.Frame(self.tab_items)
        actions.pack(fill="x", padx=10, pady=5)
        ttk.Button(actions, text="Удалить", command=self.delete_item).pack(side="left", padx=5)
        ttk.Button(actions, text="Экспорт в CSV", command=self.do_export).pack(side="left", padx=5)

        # Итоги
        self.label_totals = ttk.Label(self.tab_items, text="", font=("Arial", 11, "bold"))
        self.label_totals.pack(pady=5)

    def _build_stats_tab(self):
        self.tree_stats = ttk.Treeview(self.tab_stats,
                                        columns=("category", "count", "quantity", "value"),
                                        show="headings")
        for col, title in zip(("category", "count", "quantity", "value"),
                               ["Категория", "Кол-во товаров", "Единиц", "Стоимость"]):
            self.tree_stats.heading(col, text=title)
            self.tree_stats.column(col, width=150)
        self.tree_stats.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Button(self.tab_stats, text="Обновить статистику",
                   command=self.refresh_stats).pack(pady=5)

    def _on_tab_changed(self, event):
        """Автообновление статистики при переключении на вкладку."""
        if self.notebook.index("current") == 1:
            self.refresh_stats()

    def add_item(self):
        # ДЕФЕКТ 9: пустое поле количества вызывает ошибку
        article = self.entry_article.get()
        name = self.entry_name.get()
        category = self.combo_category.get()
        quantity = int(self.entry_quantity.get())
        price = float(self.entry_price.get())
        date = self.entry_date.get()
        comment = self.entry_comment.get()

        # ДЕФЕКТ 7: нет проверки уникальности артикула
        # ДЕФЕКТ 10: нет проверки отрицательного количества

        item = {
            "article": article,
            "name": name,
            "category": category,
            "quantity": quantity,
            "price": price,
            "date": date,
            "comment": comment,
        }
        self.items.append(item)

        # Автоматическое обновление таблицы после добавления
        self.current_items = self.items.copy()
        self._refresh_table()
        self.refresh_stats()
        save_data(self.items)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар")
            return
        index = self.tree.index(selected[0])
        del self.items[index]
        # ДЕФЕКТ 5: save_data не вызывается — удаление не сохраняется
        # Кнопки «Сохранить» больше нет, поэтому обойти дефект невозможно
        self.current_items = self.items.copy()
        self._refresh_table()
        self.refresh_stats()

    def do_search(self):
        """Динамический поиск — вызывается при каждом нажатии клавиши."""
        query = self.entry_search.get()
        self.current_items = search_items(self.items, query)
        self._refresh_table()

    def do_filter(self):
        """Динамический фильтр по категории — вызывается при выборе."""
        category = self.combo_filter_cat.get()
        self.current_items = filter_by_category(self.items, category)
        self._refresh_table()

    def do_filter_qty(self):
        """Динамический фильтр по количеству — вызывается при вводе."""
        max_qty = self.entry_filter_qty.get()
        self.current_items = filter_by_quantity(self.items, max_qty)
        self._refresh_table()

    def reset_filters(self):
        """Сброс всех фильтров и обновление таблицы."""
        self.current_items = self.items.copy()
        self.entry_search.delete(0, "end")
        self.combo_filter_cat.set("Все")
        self.entry_filter_qty.delete(0, "end")
        self._refresh_table()

    def do_export(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv")
        if filename:
            export_to_csv(self.items, filename)
            messagebox.showinfo("Экспорт", "Данные экспортированы")

    def _refresh_table(self):
        """Обновляет таблицу и итоги."""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in self.current_items:
            self.tree.insert("", "end", values=(
                item['article'], item['name'], item['category'],
                item['quantity'], item['price'],
                item['quantity'] * item['price'], item['date']
            ))
        total_qty = calculate_total_quantity(self.current_items)
        total_val = calculate_total_value(self.current_items)
        self.label_totals.config(text=f"Всего единиц: {total_qty} | Общая стоимость: {total_val} руб.")

    def refresh_stats(self):
        """Обновляет таблицу статистики."""
        for row in self.tree_stats.get_children():
            self.tree_stats.delete(row)
        stats = get_statistics(self.items)
        for cat, data in stats.items():
            self.tree_stats.insert("", "end", values=(
                cat, data["count"], data["quantity"], data["value"]
            ))


def run():
    root = tk.Tk()
    app = WarehouseApp(root)
    root.mainloop()