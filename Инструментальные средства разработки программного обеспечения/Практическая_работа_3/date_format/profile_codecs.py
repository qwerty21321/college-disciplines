import json
import xml.etree.ElementTree as ET
import yaml
import msgpack
import cbor2
import profile_pb2

FORMATS = ('json', 'xml', 'yaml', 'msgpack', 'cbor', 'protobuf')
EXT = dict(json='json', xml='xml', yaml='yaml', msgpack='msgpack', cbor='cbor', protobuf='pb')

def to_proto(data):
    p = profile_pb2.Profile(
        id=data['id'], name=data['name'], age=data['age'],
        is_student=data['is_student'], courses=data['courses'])
    p.address.city = data['address']['city']
    p.address.zip = data['address']['zip']
    if 'email' in data:
        p.email = data['email']
    return p

def from_proto(p):
    result = dict(id=p.id, name=p.name, age=p.age,
                  is_student=p.is_student, courses=list(p.courses),
                  address=dict(city=p.address.city, zip=p.address.zip))
    if p.email:
        result['email'] = p.email
    return result

def dict_to_xml(tag, data):
    element = ET.Element(tag)
    for key, value in data.items():
        if isinstance(value, dict):
            element.append(dict_to_xml(key, value))
        elif isinstance(value, list):
            child = ET.SubElement(element, key)
            for item in value:
                ET.SubElement(child, 'item').text = str(item)
        else:
            ET.SubElement(element, key).text = str(value)
    return element

def encode(fmt, data):
    if fmt == 'json':
        return json.dumps(data, ensure_ascii=False).encode('utf-8')
    if fmt == 'xml':
        return ET.tostring(dict_to_xml('profile', data), encoding='utf-8')
    if fmt == 'yaml':
        return yaml.dump(data, allow_unicode=True, sort_keys=False,
                         default_flow_style=False).encode('utf-8')
    if fmt == 'msgpack':
        return msgpack.packb(data, use_bin_type=True)
    if fmt == 'cbor':
        return cbor2.dumps(data)
    if fmt == 'protobuf':
        return to_proto(data).SerializeToString()
    raise ValueError('Неизвестный формат: ' + fmt)

def decode(fmt, payload):
    if fmt == 'json':
        return json.loads(payload.decode('utf-8'))
    if fmt == 'xml':
        # Для учебного профиля типы восстанавливаются явно.
        root = ET.fromstring(payload)
        return dict(id=int(root.findtext('id')), name=root.findtext('name'),
                    age=int(root.findtext('age')),
                    is_student=root.findtext('is_student') == 'True',
                    courses=[item.text for item in root.findall('courses/item')],
                    address=dict(city=root.findtext('address/city'),
                                 zip=root.findtext('address/zip')))
    if fmt == 'yaml':
        return yaml.safe_load(payload.decode('utf-8'))
    if fmt == 'msgpack':
        return msgpack.unpackb(payload, raw=False)
    if fmt == 'cbor':
        return cbor2.loads(payload)
    if fmt == 'protobuf':
        p = profile_pb2.Profile()
        p.ParseFromString(payload)
        return from_proto(p)
    raise ValueError('Неизвестный формат: ' + fmt)

def show(fmt):
    from data import PROFILE
    if fmt == 'json':
        payload = json.dumps(PROFILE, ensure_ascii=False, indent=2).encode('utf-8')
    else:
        payload = encode(fmt, PROFILE)
    print('=== ' + fmt.upper() + ' ===')
    if fmt in ('json', 'xml', 'yaml'):
        print(payload.decode('utf-8'))
    else:
        print('HEX:', payload.hex())
    print('Размер:', len(payload), 'байт')
    restored = decode(fmt, payload)
    assert restored == PROFILE, (fmt, restored)
    print('Десериализация успешна:', restored['name'])
    print('Все поля совпадают с исходными: True')
