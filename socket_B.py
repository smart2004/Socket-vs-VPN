# Упрощенный SOCKS5 Proxy (фрагмент)
import socket 

def socks5_handshake(client_socket):
    """SOCKS5 рукопожатие"""
    # Версия 5, количество методов аутентификации
    client_socket.send(b'\x05\x02\x00\x02')  # No auth + Password auth 

    version, nmethods = client_socket.recv(2)
    if version != 5:
        return False 

    # Выбираем метод аутентификации 0 (no auth)
    client_socket.send(b'\x05\x00') 

    version, method = client_socket.recv(2)
    return method == 0
def handle_socks5(client_socket):
    """SOCKS5 обработка запроса"""
    if not socks5_handshake(client_socket):
        return 

    # Читаем запрос на соединение
    request = client_socket.recv(4)
    version, cmd, rsv, atyp = request 

    if atyp == 1:  # IPv4
        addr = socket.inet_ntoa(client_socket.recv(4))
        port = struct.unpack('>H', client_socket.recv(2))[0]
    else:
        print("Поддержка только IPv4")
        return 

    # Подключаемся к целевому серверу
    target_socket = socket.socket()
    target_socket.connect((addr, port)) 

    # Ответ клиенту: успех
    client_socket.send(b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + struct.pack('>H', 0)) 

    # Туннелируем данные
    def forward(source, dest):
        while True:
            data = source.recv(4096)
            if not data: break
            dest.send(data) 

    threading.Thread(target=forward, args=(client_socket, target_socket)).start()
    threading.Thread(target=forward, args=(target_socket, client_socket)).start()
