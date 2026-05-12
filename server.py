import asyncio
import json
import websockets

connected_clients = set()
ralik1_active = False
ralik2_active = False
ralik1_value = 29
ralik2_value = 29

async def broadcast(message):
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

async def handler(websocket, path):
    global ralik1_active, ralik2_active, ralik1_value, ralik2_value
    connected_clients.add(websocket)
    print(f"Клиент подключился. Всего: {len(connected_clients)}")
    try:
        state = {'type': 'state', 'ralik1_active': ralik1_active, 'ralik1_value': ralik1_value,
                 'ralik2_active': ralik2_active, 'ralik2_value': ralik2_value}
        await websocket.send(json.dumps(state))
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'command':
                if 'ralik1_active' in data:
                    ralik1_active = data['ralik1_active']
                    if ralik1_active: ralik1_value = 29
                if 'ralik2_active' in data:
                    ralik2_active = data['ralik2_active']
                    if ralik2_active: ralik2_value = 29
                if 'clear' in data:
                    ralik1_active = ralik2_active = False
                    ralik1_value = ralik2_value = 29
                state = {'type': 'state', 'ralik1_active': ralik1_active, 'ralik1_value': ralik1_value,
                         'ralik2_active': ralik2_active, 'ralik2_value': ralik2_value}
                await broadcast(json.dumps(state))
    except:
        pass
    finally:
        connected_clients.remove(websocket)

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
            state = {'type': 'state', 'ralik1_active': ralik1_active, 'ralik1_value': ralik1_value,
                     'ralik2_active': ralik2_active, 'ralik2_value': ralik2_value}
            await broadcast(json.dumps(state))

async def main():
    print("Сервер запущен на порту 10000")
    asyncio.create_task(timer_updater())
    async with websockets.serve(handler, "0.0.0.0", 10000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
