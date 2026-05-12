import asyncio
import json
from websockets.asyncio.server import serve

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
    print(f"Клиент подключился. Всего: {len(connected_clients)}")
    
    try:
        # Отправляем текущее состояние
        await websocket.send(json.dumps({
            'type': 'state',
            'ralik1_active': ralik1_active,
            'ralik1_value': ralik1_value,
            'ralik2_active': ralik2_active,
            'ralik2_value': ralik2_value
        }))
        
        # Слушаем сообщения
        async for message in websocket:
            data = json.loads(message)
            if data.get('command'):
                cmd = data['command']
                if cmd == 'ralik1_toggle':
                    ralik1_active = not ralik1_active
                    if ralik1_active:
                        ralik1_value = 29
                elif cmd == 'ralik2_toggle':
                    ralik2_active = not ralik2_active
                    if ralik2_active:
                        ralik2_value = 29
                elif cmd == 'clear':
                    ralik1_active = False
                    ralik2_active = False
                    ralik1_value = 29
                    ralik2_value = 29
                
                # Рассылаем новое состояние
                await broadcast(json.dumps({
                    'type': 'state',
                    'ralik1_active': ralik1_active,
                    'ralik1_value': ralik1_value,
                    'ralik2_active': ralik2_active,
                    'ralik2_value': ralik2_value
                }))
                
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        connected_clients.discard(websocket)
        print(f"Клиент отключился. Всего: {len(connected_clients)}")

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
            await broadcast(json.dumps({
                'type': 'state',
                'ralik1_active': ralik1_active,
                'ralik1_value': ralik1_value,
                'ralik2_active': ralik2_active,
                'ralik2_value': ralik2_value
            }))

async def main():
    print("Starting Ralik WebSocket server...")
    async with serve(handler, "0.0.0.0", 10000):
        asyncio.create_task(timer_updater())
        print(f"Server running on port 10000")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
