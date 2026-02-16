##### do edit

# Ключевые отличия в алгоритмах:
# Proxy:
# Клиент → Proxy: "Подключись к example.com" 2. Proxy → Target: TCP-соединение 3. Proxy ↔ Target: Пересылка открытых данных 4. Proxy ↔ Client: Пересылка открытых данных 
# VPN:
# 1. Клиент → VPN: Шифрованные данные 2. VPN → Расшифровка → Target: TCP-соединение 3. Target → VPN → Шифрование → Client 4. Client → Расшифровка данных 
# Важно: Эти примеры демонстрационные. Для реального использования требуются:
# • Правильная обработка ошибок
# • Поддержка всех протоколов (TCP/UDP)
# • Высокопроизводительное шифрование
# • DNS-туннелирование
# • Защита от утечек
# • Масштабируемость
# Но они четко показывают фундаментальные различия в работе!

============== 

import socket
import threading 

def handle_client(client_socket):
    """Обработка одного клиентского соединения"""
    try:
        # Получаем HTTP-запрос от клиента
        request = client_socket.recv(4096).decode('utf-8')
        print(f"[Proxy] Получен запрос:\n{request[:100]}...") 

        # Парсим первую строку запроса (GET/POST /path HTTP/1.1)
        first_line = request.split('\n')[0]
        method, url, protocol = first_line.split(' ') 

        # Извлекаем хост из заголовков
        host = None
        port = 80
        for line in request.split('\n'):
            if line.lower().startswith('host:'):
                host = line.split(' ')[1].strip()
                break 

        if not host:
            client_socket.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
            return 

        # Устанавливаем соединение с целевым сервером
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.connect((host, port)) 

        # Пересылаем запрос к целевому серверу (меняем только IP, не шифруем)
        target_socket.send(request.encode('utf-8')) 

        # Пересылаем ответ обратно клиенту
        while True:
            data = target_socket.recv(4096)
            if not data:
                break
            client_socket.send(data) 

    except Exception as e:
        print(f"[Proxy] Ошибка: {e}")
    finally:
        client_socket.close() 

def proxy_server(host='127.0.0.1', port=8080):
    """Запуск Proxy-сервера"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"[Proxy] Сервер запущен на {host}:{port}") 

    while True:
        client_socket, addr = server.accept()
        print(f"[Proxy] Подключение от {addr}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start() 

if name == "main":
    proxy_server() 

_____ 

# Запустите скрипт, затем настройте браузер на прокси 127.0.0.1:8080
# Откройте любой сайт - запросы будут проходить через прокси 

_____ 

import socket
import threading
import struct
import base64
from cryptography.fernet import Fernet
import os 

# Генерация ключа для симметричного шифрования (в реальности обменивается по ключу)
KEY = Fernet.generate_key()
cipher = Fernet(KEY)
print(f"[VPN] Ключ для шифрования: {KEY.decode()}") 

def encrypt_data(data):
    """Шифрование данных"""
    return cipher.encrypt(data) 

def decrypt_data(encrypted_data):
    """Расшифровка данных"""
    return cipher.decrypt(encrypted_data) 

class SimpleVPN:
    def init(self, server_host='127.0.0.1', server_port=8888):
        self.server_host = server_host
        self.server_port = server_port
        self.running = False 

    def handle_vpn_client(self, client_socket, client_addr):
        """Обработка VPN-клиента (VPN-сервер)"""
        print(f"[VPN-Server] Клиент подключен: {client_addr}") 

        try:
            # Устанавливаем соединение с целевым интернет-сервером
            # В примере используем google.com:80
            target_host = "www.google.com"
            target_port = 80
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((target_host, target_port))
            # Двунаправленный туннель
            def forward_client_to_target():
                try:
                    while True:
                        # Получаем зашифрованные данные от клиента
                        encrypted_data = client_socket.recv(4096)
                        if not encrypted_data:
                            break 

                        # Расшифровываем и отправляем в интернет
                        data = decrypt_data(encrypted_data)
                        target_socket.send(data)
                except:
                    pass 

            def forward_target_to_client():
                try:
                    while True:
                        # Получаем данные из интернета
                        data = target_socket.recv(4096)
                        if not data:
                            break 

                        # Шифруем и отправляем клиенту
                        encrypted_data = encrypt_data(data)
                        client_socket.send(encrypted_data)
                except:
                    pass 

            # Запускаем потоки для двунаправленной передачи
            client_to_target = threading.Thread(target=forward_client_to_target)
            target_to_client = threading.Thread(target=forward_target_to_client) 

            client_to_target.start()
            target_to_client.start() 

            client_to_target.join()
            target_to_client.join() 

        except Exception as e:
            print(f"[VPN-Server] Ошибка: {e}")
        finally:
            client_socket.close()
            target_socket.close() 

    def vpn_server(self):
        """VPN-сервер"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.server_host, self.server_port))
        server.listen(5)
        self.running = True
        print(f"[VPN-Server] Запущен на {self.server_host}:{self.server_port}") 

        while self.running:
            client_socket, addr = server.accept()
            client_thread = threading.Thread(
                target=self.handle_vpn_client, 
                args=(client_socket, addr)
            )
            client_thread.start() 

    def vpn_client(self, target_host='127.0.0.1', target_port=8888):
        """VPN-клиент"""
        vpn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        vpn_socket.connect((target_host, target_port)) 

        print("[VPN-Client] Подключен к VPN-серверу") 

        # Пример отправки HTTP-запроса через VPN-туннель
        http_request = b"GET / HTTP/1.1\r\nHost: www.google.com\r\n\r\n"
        encrypted_request = encrypt_data(http_request)
        vpn_socket.send(encrypted_request) 

        # Получаем зашифрованный ответ
        encrypted_response = vpn_socket.recv(4096)
        response = decrypt_data(encrypted_response)
        print("[VPN-Client] Получен ответ:")
        print(response.decode('utf-8', errors='ignore')[:500]) 

        vpn_socket.close() 

# Запуск демонстрации
if name == "main":
    print("=== Демонстрация VPN ===") 

    # Вариант 1: Запуск VPN-сервера в отдельном потоке
    vpn = SimpleVPN() 

    server_thread = threading.Thread(target=vpn.vpn_server)
    server_thread.daemon = True
    server_thread.start() 

    # Ждем запуска сервера
    import time
    time.sleep(1) 

    # Запуск VPN-клиента
    vpn.vpn_client()


_______ 

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
