# Практическая работа №3. Форматы данных

Богданов Роман Романович, ИС-41.

## Запуск в Windows

Откройте терминал в папке date_format:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python run_all.py
python step_json.py
python step_protobuf.py
```

Для Linux: `python3 -m venv .venv`, затем `source .venv/bin/activate`.

## TCP

В первом терминале: `python server.py`.
Во втором: `python client.py --format json`.
Повторить с `msgpack`, `cbor`, `protobuf`, каждый раз перезапуская сервер.
Значение FMT в client.py также можно менять как в задании.

## Схемная эволюция

Готовый profile_pb2.py соответствует новой схеме с email. В received/ уже
сохранено старое сообщение без email; выполните `python check_evolution.py`.

Для повторения генерации старого сообщения с нуля (до новой компиляции):

```bat
python -m grpc_tools.protoc -Ilegacy --python_out=legacy legacy/profile.proto
python legacy/make_old.py
python -m grpc_tools.protoc -I. --python_out=. profile.proto
python check_evolution.py
```

Если установлен обычный protoc, новая схема компилируется командой
`protoc --python_out=. profile.proto`.

## Результаты

Все шесть step_*.py проверяют полное восстановление исходного профиля.
run_all.py сравнивает размер и медианное время пяти серий по 1000 операций.
logs/ содержит фактический вывод запусков, screenshots/ - его изображения.
Изображения сделаны из текстовых журналов, а не снимком рабочего стола.
received/ содержит полезную нагрузку без 5-байтового заголовка приложения.
JSON с indent=2 в step_json.py больше JSON без отступов в run_all.py.
Оценки скорости относятся только к данному профилю и окружению.

Для задания достаточно Python 3.10 или новее; рекомендуем Python 3.12.
Сгенерированный модуль требует версию protobuf из requirements.txt.
