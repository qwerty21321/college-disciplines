from pathlib import Path
import profile_pb2
from data import PROFILE
from profile_codecs import from_proto

path = Path(__file__).resolve().parent / 'received' / 'message_protobuf.pb'
p = profile_pb2.Profile()
p.ParseFromString(path.read_bytes())
assert from_proto(p) == PROFILE
assert p.email == ''
print('Новая схема: добавлено string email = 7;')
print('Старый файл:', path.name)
print('Имя:', p.name)
print('Email (новое поле):', repr(p.email))
print('Остальные поля совпадают: True')
print('Новый код успешно прочитал старые данные без email.')
