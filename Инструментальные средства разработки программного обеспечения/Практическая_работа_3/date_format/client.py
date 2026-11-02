import argparse
import socket
from data import PROFILE
from profile_codecs import encode
from server import HOST, PORT, CODES, recv_exact

FMT = 'json'

def send(fmt=FMT, port=PORT):
    payload = encode(fmt, PROFILE)
    code = {value: key for key, value in CODES.items()}[fmt]
    print(f'Отправка в формате {fmt}, размер: {len(payload)} байт')
    with socket.create_connection((HOST, port), timeout=10) as conn:
        conn.sendall(code + len(payload).to_bytes(4, 'big') + payload)
        if recv_exact(conn, 2) != b'OK':
            raise RuntimeError('Сервер не подтвердил приём')
    print('Отправлено. Сервер подтвердил сохранение.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--format', choices=list(CODES.values()), default=FMT)
    parser.add_argument('--port', type=int, default=PORT)
    args = parser.parse_args()
    send(args.format, args.port)
