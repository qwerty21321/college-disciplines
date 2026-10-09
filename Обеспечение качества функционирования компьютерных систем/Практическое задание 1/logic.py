def calculate_total_value(items):
    """Считает общую стоимость склада."""
    total = 0
    for item in items:
        # ДЕФЕКТ 1: округление до целого теряет копейки
        # Пример: 3 * 100.50 = 301.50, а вернёт 301
        total += int(item['quantity'] * item['price'])
    return total


def calculate_total_quantity(items):
    """Считает общее количество единиц."""
    return sum(item['quantity'] for item in items)


def filter_by_category(items, category):
    """Фильтрует товары по категории."""
    if not category or category == "Все":
        return items
    return [item for item in items if item['category'] == category]


def filter_by_quantity(items, max_quantity):
    """Фильтрует товары по количеству."""
    # ДЕФЕКТ 2: сравнение строк, а не чисел
    # Пример: "10" <= "5" вернёт True (лексикографическое сравнение)
    return [item for item in items if item['quantity'] <= max_quantity]


def search_items(items, query):
    """Поиск по наименованию или артикулу."""
    # ДЕФЕКТ 4: регистрозависимый поиск
    # Пример: "ноутбук" не найдёт "Ноутбук"
    result = []
    for item in items:
        if query in item['name'] or query in item['article']:
            result.append(item)
    return result


def get_statistics(items):
    """Статистика по категориям."""
    stats = {}
    for item in items:
        # ДЕФЕКТ 3: пустая категория игнорируется
        # Товары без категории не попадают в статистику
        if not item['category']:
            continue
        cat = item['category']
        if cat not in stats:
            stats[cat] = {"count": 0, "quantity": 0, "value": 0}
        stats[cat]["count"] += 1
        stats[cat]["quantity"] += item['quantity']
        stats[cat]["value"] += item['quantity'] * item['price']
    return stats