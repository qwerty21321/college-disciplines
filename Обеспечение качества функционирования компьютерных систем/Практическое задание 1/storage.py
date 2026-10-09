import json
import os

DATA_FILE = "data.json"


def load_data():
    """Загружает данные из JSON-файла."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        # ДЕФЕКТ 6: нет обработки повреждённого JSON
        # Если файл повреждён — программа упадёт с ошибкой json.JSONDecodeError
        return json.load(f)


def save_data(items):
    """Сохраняет данные в JSON-файл."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def export_to_csv(items, filename="export.csv"):
    """Экспортирует данные в CSV."""
    # encoding="utf-8-sig" добавляет BOM — Excel корректно распознаёт UTF-8
    with open(filename, "w", encoding="utf-8-sig", newline="") as f:
        f.write("Артикул,Наименование,Категория,Количество,Цена,Сумма,Дата,Комментарий\n")
        for item in items:
            f.write(f"{item['article']},{item['name']},{item['category']},"
                    f"{item['quantity']},{item['price']},{item['quantity'] * item['price']},"
                    f"{item['date']},{item['comment']}\n")