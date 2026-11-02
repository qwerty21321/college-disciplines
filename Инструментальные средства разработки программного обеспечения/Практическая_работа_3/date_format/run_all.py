import json
import platform
import statistics
import sys
import timeit
from pathlib import Path
from data import PROFILE
from profile_codecs import encode, decode, FORMATS, EXT

BASE = Path(__file__).resolve().parent

def main():
    folder = BASE / 'received'
    folder.mkdir(exist_ok=True)
    report = []
    print('Python:', platform.python_version())
    print('Замер: медиана 5 серий по 1000 операций; время в мкс/операцию.')
    print(f"{'Формат':<14} {'Байт':>6} {'Запись, мкс':>12} {'Чтение, мкс':>12} {'Читаем?':>9}")
    for fmt in FORMATS:
        payload = encode(fmt, PROFILE)
        assert decode(fmt, payload) == PROFILE, fmt
        dump_us = statistics.median(timeit.repeat(
            lambda: encode(fmt, PROFILE), number=1000, repeat=5)) * 1000
        load_us = statistics.median(timeit.repeat(
            lambda: decode(fmt, payload), number=1000, repeat=5)) * 1000
        readable = fmt in ('json', 'xml', 'yaml')
        item = dict(format=fmt, wire_size_bytes=len(payload),
                    serialize_us=round(dump_us, 3), deserialize_us=round(load_us, 3),
                    readable=readable, needs_schema=fmt == 'protobuf')
        report.append(item)
        (folder / f'message_{fmt}.{EXT[fmt]}').write_bytes(payload)
        print(f"{fmt:<14} {len(payload):>6} {dump_us:>12.3f} {load_us:>12.3f} {('да' if readable else 'нет'):>9}")
    (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Все 6 форматов: исходные данные восстановлены без потерь.')
    print('Размеры указаны без TCP-заголовка приложения (5 байт).')
    return report

if __name__ == '__main__':
    main()
