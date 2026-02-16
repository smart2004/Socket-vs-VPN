# Ключевые отличия в алгоритмах:
# Proxy:
# 1. Клиент → Proxy: "Подключись к example.com" 2. Proxy → Target: TCP-соединение 3. Proxy ↔ Target: Пересылка открытых данных 4. Proxy ↔ Client: Пересылка открытых данных 
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


# ============== 

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
