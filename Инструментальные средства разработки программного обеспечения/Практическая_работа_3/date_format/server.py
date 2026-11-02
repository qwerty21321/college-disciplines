import argparse
import socket
from pathlib import Path
from profile_codecs import decode, EXT

HOST, PORT = '127.0.0.1', 9999
CODES = {b'J': 'json', b'M': 'msgpack', b'C': 'cbor', b'P': 'protobuf'}
BASE = Path(__file__).resolve().parent

def recv_exact(conn, length):
    result = bytearray()
    while len(result) < length:
        chunk = conn.recv(length - len(result))
        if not chunk:
            raise ConnectionError('Соединение закрыто до получения всего сообщения')
        result.extend(chunk)
    return bytes(result)

def serve(port=PORT):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, port))
        server.listen(1)
        server.settimeout(30)
        print(f'Сервер слушает {HOST}:{port}...', flush=True)
        conn, _ = server.accept()
        with conn:
            conn.settimeout(10)
            code = recv_exact(conn, 1)
            if code not in CODES:
                raise ValueError('Неизвестный код формата')
            fmt = CODES[code]
            length = int.from_bytes(recv_exact(conn, 4), 'big')
            if not 0 < length <= 1_048_576:
                raise ValueError('Недопустимый размер сообщения')
            payload = recv_exact(conn, length)
            data = decode(fmt, payload)
            print(f'=== Получено {len(payload)} байт, формат: {fmt} ===')
            print('HEX:', payload.hex())
            try:
                text = payload.decode('utf-8')
                print('TEXT:', text if text.isprintable() else '<не текст, бинарные данные>')
            except UnicodeDecodeError:
                print('TEXT: <не текст, бинарные данные>')
            print('DATA:', data)
            folder = BASE / 'received'
            folder.mkdir(exist_ok=True)
            path = folder / f'message_{fmt}.{EXT[fmt]}'
            path.write_bytes(payload)
            print(f'[СОХРАНЕНО] received/{path.name} ({len(payload)} байт)')
            conn.sendall(b'OK')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=PORT)
    serve(parser.parse_args().port)
