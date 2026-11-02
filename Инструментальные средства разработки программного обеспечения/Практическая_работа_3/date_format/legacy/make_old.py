from pathlib import Path
import sys
import profile_pb2
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data import PROFILE
p = profile_pb2.Profile(id=PROFILE['id'], name=PROFILE['name'], age=PROFILE['age'], is_student=PROFILE['is_student'], courses=PROFILE['courses'])
p.address.city = PROFILE['address']['city']
p.address.zip = PROFILE['address']['zip']
folder = Path(__file__).resolve().parents[1] / 'received'
folder.mkdir(exist_ok=True)
(folder / 'message_protobuf.pb').write_bytes(p.SerializeToString())
print('Старая схема без email:', len(p.SerializeToString()), 'байт сохранено.')
