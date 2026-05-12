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
        tasks = [client.send(message) for client in connected_clients]
        await asyncio.gather(*tasks, return_exceptions=True)

async def handler(websocket):
    global ralik1_active, ralik2_active, ralik1_value, ralik2_value
    connected_clients.add(websocket)
    print(f"✅ Клиент подключился. Всего: {len(connected_clients)}")
    
    try:
        await websocket.send(json.dumps({
            'ralik1_active': ralik1_active,
            'ralik1_value': ralik1_value,
            'ralik2_active': ralik2_active,
            'ralik2_value': ralik2_value
        }))
        
        async for message in websocket:
            data = json.loads(message)
            cmd = data.get('cmd')
            
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
            
            await broadcast(json.dumps({
                'ralik1_active': ralik1_active,
                'ralik1_value': ralik1_value,
                'ralik2_active': ralik2_active,
                'ralik2_value': ralik2_value
            }))
            
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        connected_clients.discard(websocket)

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
                'ralik1_active': ralik1_active,
                'ralik1_value': ralik1_value,
                'ralik2_active': ralik2_active,
                'ralik2_value': ralik2_value
            }))

async def main():
    port = int(os.environ.get("PORT", 10000))
    async with serve(handler, "0.0.0.0", port):
        asyncio.create_task(timer_updater())
        await asyncio.Future()

if __name__ == "__main__":
    import os
    asyncio.run(main())
