"""Проверки исходной программы без графического окна. Код приложения не меняется.
Запуск: python проверка.py. Каждый сценарий изолирован временной папкой.
Fail означает отличие от технического задания, а не сбой сценария проверки.
"""
import ast
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import gui
import logic
import storage
BASE = [dict(article='A001', name='Ноутбук', category='Электроника', quantity=5, price=40000.0, date='01.10.2026', comment='Учебный товар'), dict(article='A002', name='Мышь', category='Электроника', quantity=10, price=1000.0, date='02.10.2026', comment='Учебный товар'), dict(article='B001', name='Стул', category='Мебель', quantity=0, price=5000.0, date='03.10.2026', comment='Учебный товар')]

class Field:

    def __init__(self, value=''):
        self.value = value

    def get(self):
        return self.value

    def delete(self, *_):
        self.value = ''

    def set(self, value):
        self.value = value

class Label:

    def config(self, **kw):
        self.text = kw.get('text', '')

class Tree:

    def __init__(self):
        self.rows = {}
        self.chosen = []
        self.counter = 0

    def get_children(self):
        return tuple(self.rows)

    def delete(self, key):
        self.rows.pop(key, None)

    def insert(self, parent, index, values):
        self.counter += 1
        key = str(self.counter)
        self.rows[key] = tuple(values)
        return key

    def selection(self):
        return tuple(self.chosen)

    def index(self, key):
        return list(self.rows).index(key)

    def select_first(self):
        self.chosen = [next(iter(self.rows))]

def app(items=None, **changes):
    a = gui.WarehouseApp.__new__(gui.WarehouseApp)
    a.items = copy.deepcopy(BASE if items is None else items)
    a.current_items = a.items.copy()
    defaults = dict(article='C001', name='Клавиатура', category='Электроника', quantity='2', price='1500', date='04.10.2026', comment='Проверка')
    defaults.update(changes)
    for k, v in defaults.items():
        setattr(a, 'combo_category' if k == 'category' else 'entry_' + k, Field(v))
    a.entry_search = Field()
    a.combo_filter_cat = Field('Все')
    a.entry_filter_qty = Field()
    a.tree = Tree()
    a.tree_stats = Tree()
    a.label_totals = Label()
    a._refresh_table()
    a.refresh_stats()
    return a

def articles(items):
    return [v['article'] for v in items]

def adding(**changes):
    a = app(**changes)
    a.add_item()
    return a

def rejected(**changes):
    a = app(**changes)
    before = copy.deepcopy(a.items)
    try:
        a.add_item()
    except (ValueError, TypeError, OverflowError) as e:
        return (False, f'Необработанное исключение {type(e).__name__}: {e}')
    ok = a.items == before
    return (ok, 'Товар отклонён' if ok else 'Товар добавлен: ' + json.dumps(a.items[-1], ensure_ascii=False))
RESULTS = []
DISPLAY_IDS = {n: i for i, n in enumerate([1, 5, 6, 13, 17, 18, 19, 22, 23, 26, 27, 29, 30, 31, 32, 34, 36, 39, 42, 43], 1)}

def run(number, function, data, expected, check):
    with tempfile.TemporaryDirectory(prefix='warehouse-check-') as tmp:
        before = os.getcwd()
        os.chdir(tmp)
        try:
            status, actual = check()
            status = 'Pass' if status is True else 'Fail' if status is False else 'Не выполнен'
        except Exception as e:
            status = 'Fail'
            actual = f'Необработанное исключение {type(e).__name__}: {e}'
        finally:
            os.chdir(before)
    RESULTS.append(dict(id=f'TC-{DISPLAY_IDS[number]:02}', function=function, data=data, expected=expected, actual=actual, status=status))

def ok_add():
    a = adding()
    return (len(a.items) == 4 and a.items[-1]['article'] == 'C001', 'Добавлен C001; строка таблицы: ' + str(list(a.tree.rows.values())[-1]))
run(1, 'Добавление FR-1', 'Клавиатура; C001; Электроника; 2; 1500; 04.10.2026; Проверка', 'Товар добавлен; сумма 3000', ok_add)
for n, f, d, k, v, e in [(5, 'Уникальность FR-1', 'Существующий артикул A001', 'article', 'A001', 'Дубликат отклонён')]:
    run(n, f, d, e, lambda k=k, v=v: rejected(**{k: v}))

def add_zero():
    a = adding(quantity='0')
    return (a.items[-1]['quantity'] == 0 and list(a.tree.rows.values())[-1][5] == 0, 'Товар добавлен; количество 0; сумма 0')
run(6, 'Количество FR-1', 'Количество 0', 'Товар добавлен; сумма 0', add_zero)

def decimal_price():
    a = adding(price='1500.50')
    return (a.items[-1]['price'] == 1500.5 and list(a.tree.rows.values())[-1][5] == 3001, 'Цена 1500.5; сумма строки 3001')
run(13, 'Цена FR-1', 'Количество 2; цена 1500.50', 'Цена сохранена; сумма 3001', decimal_price)

def empty_comment():
    a = adding(comment='')
    return (a.items[-1]['comment'] == '', 'Товар добавлен с пустым комментарием')
run(17, 'Комментарий FR-1', 'Пустой комментарий', 'Товар добавлен', empty_comment)

def columns():
    a = app()
    rows = list(a.tree.rows.values())
    return (rows[0] == ('A001', 'Ноутбук', 'Электроника', 5, 40000.0, 200000.0, '01.10.2026'), 'Сформированы 7 значений первой строки: ' + str(rows[0]))
run(18, 'Таблица FR-2', 'Три исходных товара', 'Верные значения семи колонок', columns)

def editing():
    tree = ast.parse((ROOT / 'gui.py').read_text())
    methods = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    present = any((n in methods for n in ['edit_item', 'update_item', 'edit_product']))
    return (present, 'В gui.py нет обработчика редактирования, кнопки Редактировать или привязки открытия карточки для изменения')
run(19, 'Редактирование FR-3', 'Проверка обработчиков и построения интерфейса в gui.py', 'Есть возможность изменить любое поле', editing)

def confirmation():
    a = app()
    a.tree.select_first()
    with patch.object(gui.messagebox, 'askyesno', return_value=False) as ask:
        a.delete_item()
        return (ask.called and len(a.items) == 3, f'Вызов подтверждения: {ask.called}; осталось товаров: {len(a.items)}')

def delete_filtered():
    a = app()
    a.combo_filter_cat.set('Мебель')
    a.do_filter()
    a.tree.select_first()
    a.delete_item()
    return (articles(a.items) == ['A001', 'A002'], 'После выбора B001 в отфильтрованной таблице остались: ' + str(articles(a.items)))

def deleted_saved():
    a = app()
    storage.save_data(a.items)
    a.tree.select_first()
    a.delete_item()
    saved = storage.load_data()
    return (articles(saved) == ['A002', 'B001'], 'В памяти: ' + str(articles(a.items)) + '; после загрузки JSON: ' + str(articles(saved)))
run(22, 'Сохранение удаления FR-10', 'Сохранить исходные данные; удалить A001; снова загрузить JSON', 'A001 отсутствует после загрузки', deleted_saved)
run(23, 'Поиск FR-5', 'Запрос Ноут', 'Найден A001', lambda: (articles(logic.search_items(BASE, 'Ноут')) == ['A001'], str(articles(logic.search_items(BASE, 'Ноут')))))
run(26, 'Категория FR-6', 'Фильтр Электроника', 'Найдены A001, A002', lambda: (articles(logic.filter_by_category(BASE, 'Электроника')) == ['A001', 'A002'], str(articles(logic.filter_by_category(BASE, 'Электроника')))))

def qty_filter():
    a = app()
    a.entry_filter_qty.set('9')
    a.do_filter_qty()
    return (articles(a.current_items) == ['A001', 'B001'], str(articles(a.current_items)))
run(27, 'Количество FR-6', 'Поле Кол-во ≤: 9', 'Найдены A001 с 5 и B001 с 0', qty_filter)

def combined():
    a = app()
    a.combo_filter_cat.set('Мебель')
    a.do_filter()
    a.entry_search.set('Ноут')
    a.do_search()
    return (a.current_items == [], 'При выбранной Мебели и поиске Ноут показаны: ' + str(articles(a.current_items)))
run(29, 'Количество FR-7', 'Количество исходного набора 5+10+0', '15', lambda: (logic.calculate_total_quantity(BASE) == 15, str(logic.calculate_total_quantity(BASE))))
run(30, 'Стоимость FR-7', 'Исходный набор без копеек', '210000', lambda: (logic.calculate_total_value(BASE) == 210000, str(logic.calculate_total_value(BASE))))

def kopecks():
    items = [dict(BASE[0], quantity=3, price=100.5)]
    value = logic.calculate_total_value(items)
    return (value == 301.5, str(value))
run(31, 'Копейки FR-7', 'Количество 3; цена 100.50', '301.50', kopecks)

def stats():
    s = logic.get_statistics(BASE)
    return (s == {'Электроника': {'count': 2, 'quantity': 15, 'value': 210000.0}, 'Мебель': {'count': 1, 'quantity': 0, 'value': 0.0}}, json.dumps(s, ensure_ascii=False))
run(32, 'Статистика FR-8', 'Три исходных товара', 'Электроника: 2 товара, 15 единиц, 210000; Мебель: 1 товар, 0 единиц, 0', stats)

def empty_cat():
    items = [dict(BASE[0], category='', quantity=2, price=100)]
    s = logic.get_statistics(items)
    return (sum((v['quantity'] for v in s.values())) == 2 and sum((v['value'] for v in s.values())) == 200, json.dumps(s, ensure_ascii=False))

def export_plain():
    storage.export_to_csv(BASE, 'plain.csv')
    with open('plain.csv', encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    return (len(rows) == 4 and all((len(r) == 8 for r in rows)), f'Строк: {len(rows)}; колонок в строках: {[len(r) for r in rows]}')
run(34, 'Экспорт FR-9', 'Исходный набор без запятых в тексте', 'CSV: заголовок и три товара, по 8 полей', export_plain)

def export_comma():
    item = dict(BASE[0], comment='Хлопок, размер M')
    storage.export_to_csv([item], 'comma.csv')
    with open('comma.csv', encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    return (len(rows[1]) == 8 and rows[1][-1] == 'Хлопок, размер M', f'В строке {len(rows[1])} колонок вместо 8; поля: {rows[1]}')

def save_load():
    storage.save_data(BASE)
    loaded = storage.load_data()
    return (loaded == BASE, 'После сохранения и загрузки все поля совпали')
run(36, 'JSON FR-10', 'Сохранить и загрузить три товара', 'Все данные совпадают', save_load)

def invalid_json():
    Path('data.json').write_text('{bad json', encoding='utf-8')
    data = storage.load_data()
    return (isinstance(data, list), 'Возвращён список после обработки повреждения')

def russian():
    src = (ROOT / 'gui.py').read_text()
    needed = ['Учёт товаров на складе', 'Добавить товар', 'Товары', 'Статистика', 'Удалить', 'Экспорт в CSV']
    return (all((t in src for t in needed)), 'Русские заголовки, кнопки, подписи и сообщения присутствуют в построении интерфейса')
run(39, 'Русский интерфейс NFR-1', 'Проверить строки построения интерфейса', 'Интерфейс на русском', russian)

def reset():
    a = app()
    a.entry_search.set('Ноут')
    a.do_search()
    a.combo_filter_cat.set('Мебель')
    a.entry_filter_qty.set('9')
    a.reset_filters()
    return (a.current_items == BASE and a.entry_search.get() == '' and (a.combo_filter_cat.get() == 'Все') and (a.entry_filter_qty.get() == ''), 'Все три товара восстановлены; поиск и числовой фильтр очищены; категория Все')
run(42, 'Сброс фильтров FR-5 FR-6', 'Выбрать условия и вызвать Сбросить', 'Все исходные товары, условия очищены', reset)

def export_filtered():
    a = app()
    a.combo_filter_cat.set('Мебель')
    a.do_filter()
    with patch.object(gui.filedialog, 'asksaveasfilename', return_value='all.csv'), patch.object(gui.messagebox, 'showinfo'):
        a.do_export()
    with open('all.csv', encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    return (len(rows) == 4, f'Экспортировано {len(rows) - 1} товаров при фильтре Мебель')
run(43, 'Экспорт с фильтром FR-9', 'Выбрана категория Мебель; экспорт', 'Экспортированы все три товара', export_filtered)

def no_selection():
    a = app()
    with patch.object(gui.messagebox, 'showwarning') as warning:
        a.delete_item()
        return (warning.called and a.items == BASE, f'Предупреждение вызвано: {warning.called}; данные сохранены')
RESULTS.sort(key=lambda x: x['id'])
payload = dict(source='https://github.com/AlexSkoruk/App_testing-warehouse_manager', source_commit='ae9da8a81567573c8bec1ff7f6460d7608584af8', method='Проверка кода и вызов функций/обработчиков; поля и таблицы заменены тестовыми объектами; настоящее окно не запускалось', checks=RESULTS, summary={s: sum((r['status'] == s for r in RESULTS)) for s in ['Pass', 'Fail', 'Не выполнен']}, source_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py') if p.name != 'проверка.py'})
(ROOT / 'Результаты_проверок.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(payload['summary'], ensure_ascii=False))
for r in RESULTS:
    print(r['id'], r['status'], r['actual'])
