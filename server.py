import asyncio
import json
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
import socket

connected_clients = set()
ralik1_active = False
ralik2_active = False
ralik1_value = 29
ralik2_value = 29

async def broadcast(message):
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

async def handler(websocket):
    global ralik1_active, ralik2_active, ralik1_value, ralik2_value
    connected_clients.add(websocket)
    print(f"✅ Клиент подключился. Всего: {len(connected_clients)}")
    try:
        state = {
            'type': 'state',
            'ralik1_active': ralik1_active,
            'ralik1_value': ralik1_value,
            'ralik2_active': ralik2_active,
            'ralik2_value': ralik2_value
        }
        await websocket.send(json.dumps(state))
        
        async for message in websocket:
            data = json.loads(message)
            if data.get('type') == 'command':
                if 'ralik1_active' in data:
                    ralik1_active = data['ralik1_active']
                    if ralik1_active:
                        ralik1_value = 29
                if 'ralik2_active' in data:
                    ralik2_active = data['ralik2_active']
                    if ralik2_active:
                        ralik2_value = 29
                if data.get('clear'):
                    ralik1_active = False
                    ralik2_active = False
                    ralik1_value = 29
                    ralik2_value = 29
                
                state = {
                    'type': 'state',
                    'ralik1_active': ralik1_active,
                    'ralik1_value': ralik1_value,
                    'ralik2_active': ralik2_active,
                    'ralik2_value': ralik2_value
                }
                await broadcast(json.dumps(state))
    except ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        print(f"❌ Клиент отключился. Всего: {len(connected_clients)}")

async def timer_updater():
    global ralik1_value, ralik2_value, ralik1_active, ralik2_active
    while True:
        await asyncio.sleep(1)
        changed = False
        if ralik1_active:
            ralik1_value -= 1
            if ralik1_value < 0:
                ralik1_value = 29
            changed = True
        if ralik2_active:
            ralik2_value -= 1
            if ralik2_value < 0:
                ralik2_value = 29
            changed = True
        if changed:
            state = {
                'type': 'state',
                'ralik1_active': ralik1_active,
                'ralik1_value': ralik1_value,
                'ralik2_active': ralik2_active,
                'ralik2_value': ralik2_value
            }
            await broadcast(json.dumps(state))

async def health_check_handler(reader, writer):
    """Обработчик HTTP-запросов для health check Render"""
    try:
        request = await reader.read(1024)
        response = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Stalcraft Ralik Server</h1><p>WebSocket сервер работает</p>"
        writer.write(response)
        await writer.drain()
    except:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    print("🚀 Stalcraft Ralik Server запущен!")
    
    # Запускаем WebSocket сервер на порту 10000
    async with serve(handler, "0.0.0.0", 10000):
        # Запускаем таймеры
        asyncio.create_task(timer_updater())
        
        # Запускаем простой HTTP сервер для health check на том же порту? 
        # (WebSocket сам обрабатывает HTTP, но не HEAD запросы)
        # Render требует только чтобы сервер слушал порт 10000, 
        # а WebSocket справляется с этим сам. Ошибки в логах не критичны.
        
        print("✅ Сервер готов к работе")
        print(f"📡 WebSocket endpoint: wss://ваш-сервер.onrender.com")
        print("⏲️  Таймеры раликов запущены")
        
        await asyncio.Future()  # Бесконечное ожидание

if __name__ == "__main__":
    asyncio.run(main())
